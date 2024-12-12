# OpenWRT Package Makefile for udev-gentoo-scripts
#
# SPDX-License-Identifier: GPL-2.0

include $(TOPDIR)/rules.mk

PKG_NAME:=udev-gentoo-scripts
PKG_VERSION:=33
PKG_RELEASE:=1

PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.bz2
PKG_SOURCE_URL:=https://gitweb.gentoo.org/proj/udev-gentoo-scripts.git/snapshot
PKG_HASH:=skip

PKG_LICENSE:=GPL-2.0
PKG_LICENSE_FILES:=init.d/udev-settle

PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)

include $(INCLUDE_DIR)/package.mk

define Package/udev-gentoo-scripts
  SECTION:=utils
  CATEGORY:=Utilities
  TITLE:=Gentoo udev scripts for device initialization
  URL:=https://gitweb.gentoo.org/proj/udev-gentoo-scripts.git
  DEPENDS:=+udev
endef

define Package/udev-gentoo-scripts/description
  This package provides udev-settle and udev-trigger scripts, used in 
  OpenRC-like environments to initialize devices properly during boot.
endef

define Build/Compile
	$(MAKE) -C $(PKG_BUILD_DIR)
endef

define Package/udev-gentoo-scripts/install
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/init.d/udev-settle $(1)/etc/init.d/
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/init.d/udev-trigger $(1)/etc/init.d/

	$(INSTALL_DIR) $(1)/etc/runlevels/sysinit
	ln -sf /etc/init.d/udev-settle $(1)/etc/runlevels/sysinit/udev-settle
	ln -sf /etc/init.d/udev-trigger $(1)/etc/runlevels/sysinit/udev-trigger
endef

$(eval $(call BuildPackage,udev-gentoo-scripts))
