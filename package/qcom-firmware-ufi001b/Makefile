# SPDX-License-Identifier: GPL-2.0-only
# Package recipe is GPL-2.0-only; extracted firmware remains proprietary.

include $(TOPDIR)/rules.mk

PKG_NAME:=qcom-firmware-ufi001b
PKG_VERSION:=r1034.2.1
PKG_RELEASE:=1
PKG_SOURCE_PROTO:=git
PKG_SOURCE_URL:=https://github.com/HandsomeMod/qcom-firmware.git
PKG_SOURCE_VERSION:=fc0ce66ecb7dcc1293c1e29cad2d7f566221efca
PKG_MIRROR_HASH:=6a9f773cfa43360d1a261edd37bbde857eb0aeea4bfe9c388be3d760c8b259b9
PKG_LICENSE:=Proprietary
PKG_REDISTRIBUTE:=0
PKG_FLAGS:=nonshared
STRIP:=:

include $(INCLUDE_DIR)/package.mk

define Package/qcom-ufi001b-firmware/Default
  SECTION:=firmware
  CATEGORY:=Firmware
  HIDDEN:=1
endef

define Package/qcom-ufi001b-modem-firmware
  $(Package/qcom-ufi001b-firmware/Default)
  TITLE:=Private UFI001B MSM8916 modem firmware
endef

define Package/qcom-ufi001b-wcnss-firmware
  $(Package/qcom-ufi001b-firmware/Default)
  TITLE:=Private UFI001B WCNSS firmware
endef

define Package/qcom-ufi001b-wcnss-nv
  $(Package/qcom-ufi001b-firmware/Default)
  TITLE:=Private UFI001B Wi-Fi calibration template
endef

define Build/Compile
	mkdir -p $(PKG_BUILD_DIR)/ufi001b
	mcopy -i $(PKG_BUILD_DIR)/openstick-ufi001b-modem.bin -p -m -v \
		::image/mba.mbn ::image/modem.* ::image/wcnss.* $(PKG_BUILD_DIR)/ufi001b
endef

define Package/qcom-ufi001b-modem-firmware/install
	$(INSTALL_DIR) $(1)/lib/firmware
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/ufi001b/mba.mbn $(1)/lib/firmware/
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/ufi001b/modem.* $(1)/lib/firmware/
endef

define Package/qcom-ufi001b-wcnss-firmware/install
	$(INSTALL_DIR) $(1)/lib/firmware
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/ufi001b/wcnss.* $(1)/lib/firmware/
endef

define Package/qcom-ufi001b-wcnss-nv/install
	$(INSTALL_DIR) $(1)/lib/firmware/wlan/prima
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/openstick-ufi001b-nv.bin \
		$(1)/lib/firmware/wlan/prima/WCNSS_qcom_wlan_nv.bin
endef

$(eval $(call BuildPackage,qcom-ufi001b-modem-firmware))
$(eval $(call BuildPackage,qcom-ufi001b-wcnss-firmware))
$(eval $(call BuildPackage,qcom-ufi001b-wcnss-nv))
