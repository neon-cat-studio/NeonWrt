# OpenWRT Package Makefile for libsigc++
#
# SPDX-License-Identifier: LGPL-3.0+

include $(TOPDIR)/rules.mk

PKG_NAME:=libsigc++
PKG_VERSION:=3.4.0
PKG_RELEASE:=1

PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.xz
PKG_SOURCE_URL:=https://download.gnome.org/sources/libsigc++/3.4
PKG_HASH:=skip

PKG_LICENSE:=LGPL-3.0+
PKG_LICENSE_FILES:=COPYING

PKG_BUILD_DEPENDS:=ninja/host meson/host
PKG_INSTALL:=1
PKG_FIXUP:=meson

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/meson.mk

define Package/libsigc++
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=libsigc++ - A callback framework for C++
  URL:=https://libsigc.sourceforge.io/
endef

define Package/libsigc++/description
  libsigc++ is a C++ library for typesafe callbacks and signals. It is
  the cornerstone for other libraries like gtkmm or other GObject-based
  C++ bindings.
endef

MESON_OPTIONS += \
	-Dbuild-examples=false \
	-Dbuild-tests=false \
	-Dvalidation=false

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include/sigc++-3.0
	$(CP) $(PKG_BUILD_DIR)/sigc++/* $(1)/usr/include/sigc++-3.0/

	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/libsigc++-3.0.so* $(1)/usr/lib/

	$(INSTALL_DIR) $(1)/usr/lib/pkgconfig
	$(CP) $(PKG_BUILD_DIR)/libsigc++-3.0.pc $(1)/usr/lib/pkgconfig/
endef

define Package/libsigc++/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/libsigc++-3.0.so* $(1)/usr/lib/
endef

$(eval $(call BuildPackage,libsigc++))
