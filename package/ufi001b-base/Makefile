# SPDX-License-Identifier: GPL-2.0-only

include $(TOPDIR)/rules.mk

PKG_NAME:=ufi001b-base
PKG_VERSION:=0.1.0
PKG_RELEASE:=5

include $(INCLUDE_DIR)/package.mk

define Package/ufi001b-base
  SECTION:=base
  CATEGORY:=Base system
  TITLE:=Handsome OpenStick UFI001B board defaults and safety guards
  DEPENDS:=+kmod-usb-gadget-eth
  PKGARCH:=all
endef

define Package/ufi001b-base/description
 Board defaults and USB Ethernet startup for UFI001B.
endef

define Build/Compile
endef

define Package/ufi001b-base/install
	$(INSTALL_DIR) $(1)/etc/board.d $(1)/etc/init.d $(1)/etc/uci-defaults
	$(INSTALL_BIN) ./files/etc/board.d/02_network $(1)/etc/board.d/02_network
	$(INSTALL_BIN) ./files/etc/init.d/ufi001b-usb-gadget $(1)/etc/init.d/ufi001b-usb-gadget
	$(INSTALL_BIN) ./files/etc/uci-defaults/90-ufi001b-system $(1)/etc/uci-defaults/90-ufi001b-system
endef

$(eval $(call BuildPackage,ufi001b-base))
