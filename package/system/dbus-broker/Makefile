# OpenWRT Package Makefile for dbus-broker
#
# SPDX-License-Identifier: Apache-2.0 OR LGPL-2.1+

include $(TOPDIR)/rules.mk

PKG_NAME:=dbus-broker
PKG_VERSION:=36
PKG_RELEASE:=1

PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.xz
PKG_SOURCE_URL:=https://github.com/bus1/dbus-broker/releases/download/v$(PKG_VERSION)
PKG_HASH:=skip

PKG_LICENSE:=Apache-2.0 AND LGPL-2.1+
PKG_LICENSE_FILES:=LICENSE

PKG_BUILD_PARALLEL:=1
PKG_FIXUP:=autoreconf
PKG_INSTALL:=1

PKG_BUILD_DEPENDS:=expat systemd

include $(INCLUDE_DIR)/package.mk

define Package/dbus-broker
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=dbus-broker - A modern D-Bus message bus
  DEPENDS:=+libexpat +systemd +dbus
  URL:=https://github.com/bus1/dbus-broker
endef

define Package/dbus-broker/description
  dbus-broker is a modern implementation of the D-Bus message bus.
  It is designed to be fully compatible with the reference implementation,
  while providing significant improvements in performance and resource usage.
endef

# Configuration options
MESON_ARGS += \
	-Dlauncher=true

ifeq ($(CONFIG_PACKAGE_libselinux),y)
  MESON_ARGS += -Dselinux=true
  DEPENDS+= +libselinux
else
  MESON_ARGS += -Dselinux=false
endif

ifeq ($(CONFIG_PACKAGE_audit),y)
  MESON_ARGS += -Daudit=true
  DEPENDS+= +audit +libcap-ng
else
  MESON_ARGS += -Daudit=false
endif

define Build/Configure
	$(call Build/Configure/Default, $(MESON_ARGS))
endef

define Package/dbus-broker/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/dbus-broker $(1)/usr/bin/

	# systemd integration
	$(INSTALL_DIR) $(1)/usr/lib/systemd/system
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/dbus.socket $(1)/usr/lib/systemd/system/
	$(INSTALL_DIR) $(1)/usr/share/dbus-1
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/session.conf $(1)/usr/share/dbus-1/
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/system.conf $(1)/usr/share/dbus-1/
endef

$(eval $(call BuildPackage,dbus-broker))
