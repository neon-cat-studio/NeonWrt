# OpenWRT Package Makefile for dbus-triggerd
#
# SPDX-License-Identifier: GPL-2.0+

include $(TOPDIR)/rules.mk

PKG_NAME:=dbus-triggerd
PKG_VERSION:=ba3dbec805cb707c94c54de21666bf18b79bcc09
PKG_RELEASE:=1

PKG_SOURCE_PROTO:=git
PKG_SOURCE_URL:=git://rg42.org/dbustriggerd.git
PKG_SOURCE_VERSION:=$(PKG_VERSION)
PKG_HASH:=skip

PKG_LICENSE:=GPL-2.0+
PKG_LICENSE_FILES:=dbus-triggerd.c

PKG_BUILD_PARALLEL:=1
PKG_INSTALL:=1

PKG_BUILD_DEPENDS:=dbus

include $(INCLUDE_DIR)/package.mk

define Package/dbus-triggerd
  SECTION:=utils
  CATEGORY:=Utilities
  TITLE:=dbus-triggerd - D-Bus triggered command execution daemon
  DEPENDS:=+dbus
  URL:=http://rg42.org/dbustriggerd
endef

define Package/dbus-triggerd/description
  dbus-triggerd is a daemon that executes commands based on D-Bus signals.
  It is lightweight and suitable for embedded systems or environments
  that rely on D-Bus messaging.
endef

define Build/Compile
	$(MAKE) -C $(PKG_BUILD_DIR) \
		CC="$(TARGET_CC)" \
		CFLAGS="$(TARGET_CFLAGS)" \
		LDFLAGS="$(TARGET_LDFLAGS)" \
		all
endef

define Package/dbus-triggerd/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/dbus-triggerd $(1)/usr/bin/
endef

$(eval $(call BuildPackage,dbus-triggerd))
