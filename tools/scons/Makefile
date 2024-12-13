#
# Copyright (C) 2011-2015 OpenWrt.org
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=scons
PKG_VERSION:=4.7.0  # 更新版本號至支援 Python 3 的版本
PKG_RELEASE:=1

PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.gz
PKG_SOURCE_URL:=https://github.com/SCons/scons/releases/download/$(PKG_VERSION)
PKG_HASH:=skip  # 下載新版時，先設置為 skip，之後用 `make download` 確認 HASH

PKG_LICENSE:=MIT
PKG_LICENSE_FILES:=LICENSE

include $(INCLUDE_DIR)/host-build.mk

define Host/Configure
endef

define Host/Compile
endef

define Host/Install
    $(PYTHON3) setup.py install --prefix=$(STAGING_DIR_HOST)
    $(INSTALL_BIN) ./files/pywrap.sh $(STAGING_DIR_HOST)/bin/scons
    ln -sf $(STAGING_DIR_HOST)/bin/scons $(STAGING_DIR_HOST)/bin/scons.py
endef

$(eval $(call HostBuild))
