#!/usr/bin/env bash
set -euo pipefail

# OpenWrt rejects non-standard masks because they create broken package modes.
umask 022

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
profile="${1:-developer-ext4}"
build_root="${BUILD_ROOT:-$HOME/ufi001b-openwrt-build}"
output_root="${OUTPUT_ROOT:-$repo_root/out}"
tree="$build_root/openwrt"
jobs="${JOBS:-$(nproc)}"
private_firmware="${PRIVATE_FIRMWARE:-0}"
apk_signing_key_file="${APK_SIGNING_KEY_FILE:-}"
export SOURCE_DATE_EPOCH

# WSL may append Windows paths containing spaces. GNU find rejects relative PATH
# entries when OpenWrt uses -execdir, so builds must start from a Linux-only PATH.
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

if [[ ! $jobs =~ ^[1-9][0-9]*$ ]]; then
	echo "JOBS must be a positive integer" >&2
	exit 2
fi

if [[ $EUID -eq 0 ]]; then
	echo "OpenWrt must be built as an unprivileged user, not root" >&2
	exit 1
fi

mkdir -p "$build_root"

case "$profile" in
developer-ext4|stable-squashfs) ;;
*) echo "usage: $0 {developer-ext4|stable-squashfs}" >&2; exit 2 ;;
esac

if [[ "$(stat -f -c %T "$build_root" 2>/dev/null || true)" == "9p" ]]; then
	echo "BUILD_ROOT must be on a case-sensitive Linux filesystem, not /mnt/*" >&2
	exit 1
fi

python3 "$repo_root/scripts/verify-locks.py"
python3 "$repo_root/scripts/prepare-source.py" --tree "$tree" --update-feeds --install-feeds
SOURCE_DATE_EPOCH="$(git -C "$tree" show -s --format=%ct HEAD)"

if [[ -n "$apk_signing_key_file" ]]; then
	if [[ ! -f "$apk_signing_key_file" || ! -r "$apk_signing_key_file" ]]; then
		echo "APK_SIGNING_KEY_FILE must name a readable EC private key" >&2
		exit 1
	fi
	command -v openssl >/dev/null
	install -m 0600 "$apk_signing_key_file" "$tree/private-key.pem"
	openssl ec -in "$tree/private-key.pem" -check -noout >/dev/null 2>&1
	openssl ec -in "$tree/private-key.pem" -pubout -out "$tree/public-key.pem" 2>/dev/null
	chmod 0644 "$tree/public-key.pem"
	echo "using externally supplied APK signing key; only its public key will be collected"
else
	echo "warning: using an ephemeral APK signing key; this build is not release-eligible" >&2
fi

cp "$repo_root/configs/$profile.config" "$tree/.config"
if [[ "$private_firmware" == 1 ]]; then
	if [[ "$profile" != developer-ext4 ]]; then
		echo "private firmware is allowed only for the local developer HIL image" >&2
		exit 1
	fi
	cat "$repo_root/configs/hil-private-firmware.config" >> "$tree/.config"
fi

make -C "$tree" defconfig
make -C "$tree" download -j"$jobs"
if [[ "$profile" == stable-squashfs ]]; then
	rust_jobs="$jobs"
	if (( rust_jobs > 4 )); then
		rust_jobs=4
	fi
	make -C "$tree" package/feeds/packages/rust/host/configure -j1 V=sc
	python3 "$repo_root/scripts/configure-rust-jobs.py" \
		--tree "$tree" --jobs "$rust_jobs"
fi
make -C "$tree" -j"$jobs" V=sc

validate_args=(--tree "$tree" --profile "$profile")
if [[ "$private_firmware" == 1 ]]; then
	validate_args+=(--allow-private-firmware)
fi
python3 "$repo_root/scripts/validate-build.py" "${validate_args[@]}"
python3 "$repo_root/scripts/collect-artifacts.py" \
	--tree "$tree" --profile "$profile" --out "$output_root/$profile"

echo "build completed: $output_root/$profile"
