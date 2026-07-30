# SPDX-License-Identifier: GPL-2.0-only

include $(TOPDIR)/rules.mk

ARCH:=aarch64
BOARD:=msm89xx
BOARDNAME:=Qualcomm MSM89xx mobile SoCs
FEATURES:=fpu usb ext4 squashfs rtc usbgadget gpio rootfs-part
SUBTARGETS:=msm8916
MAINTAINER:=UFI001B OpenWrt maintainers

KERNEL_PATCHVER:=6.12
KERNELNAME:=Image.gz dtbs

define Target/Description
	OpenWrt for Qualcomm MSM89xx devices booted by an Android boot image.
endef

include $(INCLUDE_DIR)/target.mk

DEFAULT_PACKAGES += e2fsprogs resize2fs block-mount losetup partx-utils \
	modemmanager luci-proto-modemmanager wpad-basic-mbedtls \
	kmod-qcom-msm8916-usb kmod-usb-gadget-eth \
	usbutils uclient-fetch ca-bundle

$(eval $(call BuildTarget))
