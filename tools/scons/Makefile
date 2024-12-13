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
	# 使用 Python 3 執行 SCons 的安裝腳本
	$(PYTHON3) $(HOST_BUILD_DIR)/setup.py install --prefix=$(STAGING_DIR_HOST)

	# 清理多餘的腳本，重新包裝為可執行的 scons
	rm -f $(STAGING_DIR_HOST)/bin/scons*.py
	for bin in $(STAGING_DIR_HOST)/bin/scons*; do \
		mv "$$$$bin" "$$$$bin.py";                \
		cp ./files/pywrap.sh "$$$$bin";           \
	done

endef

$(eval $(call HostBuild))
