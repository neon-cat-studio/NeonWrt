# OpenWRT Package Makefile for dbus-glib
#
# SPDX-License-Identifier: AFL-2.1 OR GPL-2.0+

include $(TOPDIR)/rules.mk

PKG_NAME:=dbus-glib
PKG_VERSION:=0.112
PKG_RELEASE:=1

PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.gz
PKG_SOURCE_URL:=http://dbus.freedesktop.org/releases/dbus-glib
PKG_HASH:=skip

PKG_LICENSE:=AFL-2.1 OR GPL-2.0+
PKG_LICENSE_FILES:=COPYING
PKG_CPE_ID:=cpe:/a:freedesktop:dbus_glib

PKG_BUILD_PARALLEL:=1
PKG_FIXUP:=autoreconf
PKG_INSTALL:=1

PKG_BUILD_DEPENDS:=libglib2 dbus expat

include $(INCLUDE_DIR)/package.mk

define Package/dbus-glib
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=GLib-based library for D-Bus
  DEPENDS:=+libglib2 +dbus +libexpat
  URL:=https://dbus.freedesktop.org
endef

define Package/dbus-glib/description
  dbus-glib is a GLib-based library for integrating D-Bus into GLib-based applications.
  It provides tools and APIs to simplify communication over the D-Bus message bus.
endef

# Configuration options
CONFIGURE_ARGS += \
	ac_cv_have_abstract_sockets=yes \
	ac_cv_func_posix_getpwnam_r=yes \
	have_abstract_sockets=yes \
	--disable-tests \
	--disable-xml-docs \
	--disable-bash-completion \
	--disable-doxygen-docs \
	--enable-asserts=yes

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include/dbus-glib-1.0
	$(CP) $(PKG_BUILD_DIR)/dbus/*.h $(1)/usr/include/dbus-glib-1.0
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/.libs/libdbus-glib*.so* $(1)/usr/lib/
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/tools/dbus-binding-tool $(1)/usr/bin/
endef

define Package/dbus-glib/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/.libs/libdbus-glib*.so* $(1)/usr/lib/
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/tools/dbus-binding-tool $(1)/usr/bin/
endef

$(eval $(call BuildPackage,dbus-glib))
