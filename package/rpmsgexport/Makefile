# SPDX-License-Identifier: GPL-2.0-or-later

include $(TOPDIR)/rules.mk

PKG_NAME:=rpmsgexport
PKG_VERSION:=2018.02.28
PKG_RELEASE:=2
PKG_SOURCE_PROTO:=git
PKG_SOURCE_URL:=https://github.com/andersson/rpmsgexport.git
PKG_SOURCE_VERSION:=324d88d668f36c6a5e6a9c2003a050b8a5a3cd60
PKG_MIRROR_HASH:=784e385e55cdf52b882b6d7ec26eef7b5343611b6a19a7432a69075465bccf07
PKG_INSTALL:=1
PKG_BUILD_PARALLEL:=1
PKG_LICENSE:=GPL-2.0-or-later

include $(INCLUDE_DIR)/package.mk

define Package/rpmsgexport
  SECTION:=utils
  CATEGORY:=Utilities
  TITLE:=Create RPMsg modem endpoint devices
endef

define Package/rpmsgexport/install
	$(INSTALL_DIR) $(1)/etc/hotplug.d/rpmsg $(1)/usr/sbin
	$(INSTALL_BIN) ./files/55-rpmsgexport $(1)/etc/hotplug.d/rpmsg/55-rpmsgexport
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/local/bin/rpmsgexport $(1)/usr/sbin/rpmsgexport
endef

$(eval $(call BuildPackage,rpmsgexport))
