# OpenWRT Package Makefile for libuev
#
# SPDX-License-Identifier: MIT

include $(TOPDIR)/rules.mk

PKG_NAME:=libuev
PKG_VERSION:=2.4.1
PKG_RELEASE:=1

PKG_SOURCE:=libuev-$(PKG_VERSION).tar.xz
PKG_SOURCE_URL:=https://github.com/troglobit/libuev/releases/download/v$(PKG_VERSION)
PKG_HASH:=skip

PKG_LICENSE:=MIT
PKG_LICENSE_FILES:=LICENSE

PKG_INSTALL:=1
PKG_BUILD_PARALLEL:=1
PKG_FIXUP:=autoreconf

include $(INCLUDE_DIR)/package.mk

define Package/libuev
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=A lightweight event loop library
  URL:=https://github.com/troglobit/libuev
endef

define Package/libuev/description
  libuEv is a simple, small and modular event loop library for Linux.
endef

define Build/Configure
	$(call Build/Configure/Default, \
		--disable-examples \
	)
endef

define Package/libuev/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/.libs/libuev.so* $(1)/usr/lib/
endef

$(eval $(call BuildPackage,libuev))
