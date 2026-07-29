# SPDX-License-Identifier: GPL-2.0-or-later

include $(TOPDIR)/rules.mk

PKG_NAME:=rmtfs
PKG_VERSION:=0.2
PKG_RELEASE:=2
PKG_SOURCE_PROTO:=git
PKG_SOURCE_URL:=https://github.com/andersson/rmtfs.git
PKG_SOURCE_VERSION:=b08ef6f98ec567876d7d45f15c85c6ed00d7c463
PKG_MIRROR_HASH:=0b5dcd7d7d80dfac9b1b06dcba011a503e19f564cc28356c71064e4fa57bd969
PKG_INSTALL:=1
PKG_BUILD_PARALLEL:=1
PKG_LICENSE:=GPL-2.0-or-later

include $(INCLUDE_DIR)/package.mk

define Package/rmtfs
  SECTION:=utils
  CATEGORY:=Utilities
  TITLE:=Qualcomm Remote Filesystem service
  DEPENDS:=+libqrtr +qrtr-ns +libudev-zero
endef

define Package/rmtfs/install
	$(INSTALL_DIR) $(1)/etc/init.d $(1)/usr/bin
	$(INSTALL_BIN) ./files/rmtfs.init $(1)/etc/init.d/rmtfs
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/local/bin/rmtfs $(1)/usr/bin/rmtfs
endef

$(eval $(call BuildPackage,rmtfs))
