#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 4 ]]; then
	echo "usage: $0 NAME VERSION GIT_URL COMMIT" >&2
	exit 2
fi

name="$1"
version="$2"
git_url="$3"
commit="$4"

if [[ ! $name =~ ^[A-Za-z0-9._+-]+$ || ! $version =~ ^[A-Za-z0-9._+~-]+$ ]]; then
	echo "name and version must be safe archive components" >&2
	exit 2
fi
if [[ ! $git_url =~ ^https://github\.com/[^/]+/[^/]+\.git$ ]]; then
	echo "GIT_URL must be an HTTPS GitHub clone URL" >&2
	exit 2
fi
if [[ ! $commit =~ ^[0-9a-f]{40}$ ]]; then
	echo "COMMIT must be a full lowercase Git commit" >&2
	exit 2
fi

for tool in git tar zstd sha256sum realpath; do
	command -v "$tool" >/dev/null || {
		echo "missing required tool: $tool" >&2
		exit 1
	}
done

temp_root="$(realpath "${TMPDIR:-/tmp}")"
work="$(mktemp -d "$temp_root/ufi001b-mirror-hash.XXXXXX")"
work="$(realpath "$work")"
case "$work" in
"$temp_root"/ufi001b-mirror-hash.*) ;;
*) echo "refusing unsafe temporary path: $work" >&2; exit 1 ;;
esac

cleanup() {
	case "$work" in
	"$temp_root"/ufi001b-mirror-hash.*) rm -rf -- "$work" ;;
	*) echo "refusing unsafe cleanup path: $work" >&2 ;;
	esac
}
trap cleanup EXIT

subdir="$name-$version"
cd "$work"
git clone --quiet "$git_url" "$subdir"
git -C "$subdir" checkout --quiet "$commit"
timestamp="@$(git -C "$subdir" log -1 --no-show-signature --format=%ct)"
git -C "$subdir" config core.abbrev 8
git -C "$subdir" archive --format=tar HEAD --output="../$subdir.tar.git"
tar --numeric-owner --owner=0 --group=0 --ignore-failed-read \
	-C "$subdir" -f "$subdir.tar.git" -r .git .gitmodules 2>/dev/null

rm -rf -- "$subdir"
mkdir "$subdir"
tar -C "$subdir" -xf "$subdir.tar.git"
(
	cd "$subdir"
	git submodule update --init --recursive --
	rm -rf -- .git .gitmodules
)
tar --numeric-owner --owner=0 --group=0 --mode=a-s --sort=name \
	--mtime="$timestamp" -c "$subdir" |
	zstd -q -T0 --ultra -20 -c >"$subdir.tar.zst"

printf '%s  %s\n' "$(sha256sum "$subdir.tar.zst" | cut -d' ' -f1)" "$subdir.tar.zst"
