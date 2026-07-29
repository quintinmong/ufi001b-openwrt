# SPDX-License-Identifier: GPL-2.0-only

include $(TOPDIR)/rules.mk
include $(INCLUDE_DIR)/image.mk

DEVICE_VARS += QCOM_BOOTIMG_BASE QCOM_BOOTIMG_KERNEL_OFFSET
DEVICE_VARS += QCOM_BOOTIMG_RAMDISK_OFFSET QCOM_BOOTIMG_SECOND_OFFSET
DEVICE_VARS += QCOM_BOOTIMG_TAGS_OFFSET QCOM_BOOTIMG_PAGE_SIZE QCOM_CMDLINE

define Build/qcom-bootimg
	rm -f $@.kernel-dtb $@.empty-ramdisk
	cp $(KDIR)/Image.gz $@.kernel-dtb
	cat $(KDIR)/image-$(firstword $(DEVICE_DTS)).dtb >> $@.kernel-dtb
	touch $@.empty-ramdisk
	mkbootimg \
		--base $(QCOM_BOOTIMG_BASE) \
		--kernel_offset $(QCOM_BOOTIMG_KERNEL_OFFSET) \
		--ramdisk_offset $(QCOM_BOOTIMG_RAMDISK_OFFSET) \
		--second_offset $(QCOM_BOOTIMG_SECOND_OFFSET) \
		--tags_offset $(QCOM_BOOTIMG_TAGS_OFFSET) \
		--pagesize $(QCOM_BOOTIMG_PAGE_SIZE) \
		--ramdisk $@.empty-ramdisk \
		--cmdline '$(QCOM_CMDLINE)' \
		--kernel $@.kernel-dtb \
		-o $@
	rm -f $@.kernel-dtb $@.empty-ramdisk
endef

define Build/ufi001b-e2fsck
	rc=0; $(STAGING_DIR_HOST)/bin/e2fsck -pDf $@ || rc=$$?; \
		[ "$$rc" -le 1 ]
endef

define Device/Default
  PROFILES := Default
  DEVICE_DTS_DIR := $(DTS_DIR)/qcom
  KERNEL_NAME := Image.gz
  KERNEL := kernel-bin
  FILESYSTEMS := squashfs ext4
  IMAGES := boot.img rootfs.img
  IMAGE/boot.img := qcom-bootimg | check-size 65536k
  IMAGE/rootfs.img := append-rootfs | check-size 3454959k
  IMAGE/rootfs.img/ext4 := append-rootfs | ufi001b-e2fsck | check-size 3454959k
  QCOM_BOOTIMG_BASE := 0x80000000
  QCOM_BOOTIMG_KERNEL_OFFSET := 0x00080000
  QCOM_BOOTIMG_RAMDISK_OFFSET := 0x02000000
  QCOM_BOOTIMG_SECOND_OFFSET := 0x00f00000
  QCOM_BOOTIMG_TAGS_OFFSET := 0x01e00000
  QCOM_BOOTIMG_PAGE_SIZE := 2048
  QCOM_CMDLINE := earlycon console=tty0 console=ttyMSM0,115200 root=/dev/mmcblk0p14 rw rootwait
endef

include msm8916.mk

$(eval $(call BuildImage))
