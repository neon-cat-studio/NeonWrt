# OpenWRT Package Makefile for dbus-cxx
#
# SPDX-License-Identifier: LGPL-3.0+ OR BSD-3-Clause AND Boost License

include $(TOPDIR)/rules.mk

PKG_NAME:=dbus-cxx
PKG_VERSION:=2.4.0
PKG_RELEASE:=1

PKG_SOURCE_PROTO:=git
PKG_SOURCE_URL:=https://github.com/dbus-cxx/dbus-cxx.git
PKG_SOURCE_VERSION:=$(PKG_VERSION)

PKG_LICENSE:=LGPL-3.0+ OR BSD-3-Clause
PKG_LICENSE_FILES:=COPYING cmake-modules/LICENSE_1_0.txt tools/libcppgenerate/LICENSE

PKG_BUILD_PARALLEL:=1
PKG_INSTALL:=1

PKG_BUILD_DEPENDS:=libsigc
PKG_CONFIG_DEPENDS:=PACKAGE_glib2 PACKAGE_qt5base

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/cmake.mk

define Package/dbus-cxx
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=C++ wrapper for D-Bus
  DEPENDS:=+libsigc +glib2 +qt5base
  URL:=https://github.com/dbus-cxx/dbus-cxx
endef

define Package/dbus-cxx/description
  dbus-cxx is a C++ library providing a simple and easy-to-use API for
  D-Bus, the message bus system. It supports optional integration with
  GLib and Qt5.
endef

# Configuration options
CMAKE_OPTIONS += \
	-DENABLE_EXAMPLES=OFF \
	-DENABLE_TESTS=OFF

ifeq ($(CONFIG_PACKAGE_qt5base),y)
  CMAKE_OPTIONS += -DENABLE_QT_SUPPORT=ON
else
  CMAKE_OPTIONS += -DENABLE_QT_SUPPORT=OFF
endif

ifeq ($(CONFIG_PACKAGE_libglib2),y)
  CMAKE_OPTIONS += -DENABLE_GLIB_SUPPORT=ON
else
  CMAKE_OPTIONS += -DENABLE_GLIB_SUPPORT=OFF
endif

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include/dbus-cxx
	$(CP) $(PKG_BUILD_DIR)/src/*.h $(1)/usr/include/dbus-cxx
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/lib/*.so* $(1)/usr/lib/
endef

define Package/dbus-cxx/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/lib/*.so* $(1)/usr/lib/
endef

$(eval $(call BuildPackage,dbus-cxx))
