# OpenWRT Package Makefile for dbus-python
#
# SPDX-License-Identifier: MIT AND AFL-2.1 OR GPL-2.0+

include $(TOPDIR)/rules.mk

PKG_NAME:=dbus-python
PKG_VERSION:=1.2.18
PKG_RELEASE:=1

PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.gz
PKG_SOURCE_URL:=http://dbus.freedesktop.org/releases/dbus-python
PKG_HASH:=skip

PKG_LICENSE:=MIT AND AFL-2.1 OR GPL-2.0+
PKG_LICENSE_FILES:=COPYING dbus-gmain/COPYING

PKG_BUILD_PARALLEL:=1
PKG_FIXUP:=autoreconf
PKG_INSTALL:=1

PKG_BUILD_DEPENDS:=dbus glib2 python3

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/host-build.mk

define Package/dbus-python
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=Python bindings for D-Bus
  DEPENDS:=+python3 +dbus +glib2
  URL:=https://dbus.freedesktop.org
endef

define Package/dbus-python/description
  dbus-python is a Python binding for D-Bus, the message bus system.
  It provides an easy way for Python applications to communicate
  over D-Bus.
endef

# Configuration environment for Python3
CONFIGURE_ENV += \
	PYTHON=$(STAGING_DIR_HOST)/bin/python3 \
	PYTHON_INCLUDES="$(STAGING_DIR)/usr/bin/python3-config --includes" \
	PYTHON_LIBS="$(STAGING_DIR)/usr/bin/python3-config --ldflags" \
	PYTHON_EXTRA_LIBS="$(STAGING_DIR)/usr/bin/python3-config --libs --embed"

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include/dbus-python
	$(CP) $(PKG_BUILD_DIR)/dbus/*.h $(1)/usr/include/dbus-python
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/.libs/libdbus-python*.so* $(1)/usr/lib/
	$(INSTALL_DIR) $(1)/usr/lib/python3
	$(CP) $(PKG_BUILD_DIR)/build/lib*/dbus/*.so $(1)/usr/lib/python3/
endef

define Package/dbus-python/install
	$(INSTALL_DIR) $(1)/usr/lib/python3
	$(CP) $(PKG_BUILD_DIR)/build/lib*/dbus/*.so $(1)/usr/lib/python3/
endef

$(eval $(call BuildPackage,dbus-python))
