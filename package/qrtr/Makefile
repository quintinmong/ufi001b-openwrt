# SPDX-License-Identifier: GPL-2.0-or-later

include $(TOPDIR)/rules.mk

PKG_NAME:=qrtr
PKG_VERSION:=0.2
PKG_RELEASE:=2
PKG_SOURCE_PROTO:=git
PKG_SOURCE_URL:=https://github.com/andersson/qrtr.git
PKG_SOURCE_VERSION:=9dc7a88548c27983e06465d3fbba2ba27d4bc050
PKG_MIRROR_HASH:=ca4ead6d96565d6fb34abdeccfb7731d431c629d93f7bdad480bd032e8ec991c
PKG_INSTALL:=1
PKG_BUILD_PARALLEL:=1
PKG_LICENSE:=GPL-2.0-or-later

include $(INCLUDE_DIR)/package.mk

define Package/libqrtr
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=Userspace library for the Qualcomm IPC Router
endef

define Package/qrtr-ns
  SECTION:=utils
  CATEGORY:=Utilities
  TITLE:=Qualcomm IPC Router name-service daemon
  DEPENDS:=+libqrtr
endef

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/include/libqrtr.h $(1)/usr/include/
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libqrtr.so* $(1)/usr/lib/
endef

define Package/libqrtr/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libqrtr.so* $(1)/usr/lib/
endef

define Package/qrtr-ns/install
	$(INSTALL_DIR) $(1)/etc/init.d $(1)/usr/bin
	$(INSTALL_BIN) ./files/qrtr.init $(1)/etc/init.d/qrtr
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/bin/qrtr-ns $(1)/usr/bin/qrtr-ns
endef

$(eval $(call BuildPackage,libqrtr))
$(eval $(call BuildPackage,qrtr-ns))
