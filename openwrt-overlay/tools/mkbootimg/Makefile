# SPDX-License-Identifier: GPL-2.0-only

include $(TOPDIR)/rules.mk

PKG_NAME:=mkbootimg
PKG_VERSION:=2021.01.06
PKG_RELEASE:=1
PKG_SOURCE_PROTO:=git
PKG_SOURCE_URL:=https://github.com/osm0sis/mkbootimg.git
PKG_SOURCE_VERSION:=8dd5b5b5c68bcf8ecdb5859aa7036df276efcc79
PKG_MIRROR_HASH:=1d0afab3fe3d2721184f0a99f107f68b3b1a588b8a29b43125632dc3b5872823

HOST_BUILD_PARALLEL:=1

include $(INCLUDE_DIR)/host-build.mk

define Host/Compile
	$(MAKE) -C $(HOST_BUILD_DIR) CC="$(HOSTCC_NOCACHE)" mkbootimg
endef

define Host/Install
	$(INSTALL_DIR) $(STAGING_DIR_HOST)/bin
	$(INSTALL_BIN) $(HOST_BUILD_DIR)/mkbootimg $(STAGING_DIR_HOST)/bin/mkbootimg
endef

$(eval $(call HostBuild))
