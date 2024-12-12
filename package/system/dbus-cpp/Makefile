# OpenWRT Package Makefile for dbus-cpp
#
# SPDX-License-Identifier: LGPL-2.1+

include $(TOPDIR)/rules.mk

PKG_NAME:=dbus-cpp
PKG_VERSION:=0.9.0
PKG_RELEASE:=1

PKG_SOURCE:=libdbus-c++-$(PKG_VERSION).tar.gz
PKG_SOURCE_URL:=http://downloads.sourceforge.net/project/dbus-cplusplus/dbus-c++/$(PKG_VERSION)
PKG_HASH:=skip

PKG_LICENSE:=LGPL-2.1+
PKG_LICENSE_FILES:=COPYING

PKG_BUILD_PARALLEL:=1
PKG_FIXUP:=autoreconf
PKG_INSTALL:=1

PKG_BUILD_DEPENDS:=dbus expat
PKG_CONFIG_DEPENDS:=PACKAGE_libglib2 PACKAGE_efl

include $(INCLUDE_DIR)/package.mk

define Package/dbus-cpp
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=C++ API for D-Bus message bus
  DEPENDS:=+dbus +libexpat +libglib2? +efl?
  URL:=https://sourceforge.net/projects/dbus-cplusplus/
endef

define Package/dbus-cpp/description
  dbus-cpp is a C++ wrapper for the D-Bus message bus system.
  It provides an object-oriented API for communication with D-Bus services.
endef

# Configuration options
CONFIGURE_ARGS += \
	--disable-examples \
	--disable-tests \
	--disable-doxygen-docs

ifeq ($(CONFIG_PACKAGE_efl),y)
  CONFIGURE_ARGS += --enable-ecore
else
  CONFIGURE_ARGS += --disable-ecore
endif

ifeq ($(CONFIG_PACKAGE_libglib2),y)
  CONFIGURE_ARGS += --enable-glib
else
  CONFIGURE_ARGS += --disable-glib
endif

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include/dbus-c++
	$(CP) $(PKG_BUILD_DIR)/dbus-c++/*.h $(1)/usr/include/dbus-c++
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/.libs/libdbus-c++* $(1)/usr/lib/
endef

define Package/dbus-cpp/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/.libs/libdbus-c++* $(1)/usr/lib/
endef

$(eval $(call BuildPackage,dbus-cpp))
