# OpenWRT Package Makefile for dbus
#
# SPDX-License-Identifier: AFL-2.1 OR GPL-2.0+

include $(TOPDIR)/rules.mk

PKG_NAME:=dbus
PKG_VERSION:=1.14.10
PKG_RELEASE:=1

PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.xz
PKG_SOURCE_URL:=https://dbus.freedesktop.org/releases/dbus
PKG_HASH:=skip

PKG_LICENSE:=AFL-2.1 OR GPL-2.0+
PKG_LICENSE_FILES:=COPYING
PKG_CPE_ID:=cpe:/a:freedesktop:dbus

PKG_BUILD_PARALLEL:=1
PKG_FIXUP:=autoreconf
PKG_INSTALL:=1

PKG_BUILD_DEPENDS:=expat

include $(INCLUDE_DIR)/package.mk

define Package/dbus
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=D-Bus message bus system
  URL:=https://www.freedesktop.org/wiki/Software/dbus/
  DEPENDS:=+libexpat +systemd
endef

define Package/dbus/description
  D-Bus is a message bus system, a simple way for applications to talk to each other.
  It is designed for two specific use cases: communication between desktop applications,
  and communication between the desktop session and the operating system.
endef

# Configuration options
CONFIGURE_ARGS += \
	--with-dbus-user=dbus \
	--disable-tests \
	--disable-asserts \
	--disable-xml-docs \
	--disable-doxygen-docs \
	--with-system-socket=/var/run/dbus/system_bus_socket \
	--with-system-pid-file=/var/run/messagebus.pid \
	--runstatedir=/var/run

ifeq ($(CONFIG_PACKAGE_libselinux),y)
CONFIGURE_ARGS += --enable-selinux
endif

ifeq ($(CONFIG_PACKAGE_systemd),y)
CONFIGURE_ARGS += \
	--enable-systemd \
	--with-systemdsystemunitdir=/usr/lib/systemd/system
endif

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include/dbus-1.0
	$(CP) $(PKG_BUILD_DIR)/dbus $(1)/usr/include/dbus-1.0
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/libdbus* $(1)/usr/lib/
endef

define Package/dbus/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/bus/dbus-daemon $(1)/usr/bin/
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/libdbus* $(1)/usr/lib/
	$(INSTALL_DIR) $(1)/etc/dbus-1
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/bus/session.conf $(1)/etc/dbus-1/
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/bus/system.conf $(1)/etc/dbus-1/
	$(INSTALL_DIR) $(1)/var/lib/dbus
	ln -sf /etc/machine-id $(1)/var/lib/dbus/machine-id
endef

$(eval $(call BuildPackage,dbus))
