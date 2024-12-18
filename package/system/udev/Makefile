# OpenWRT Package Makefile for udev
#
# SPDX-License-Identifier: GPL-2.0+

include $(TOPDIR)/rules.mk

PKG_NAME:=udev
PKG_VERSION:=252
PKG_RELEASE:=1

PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.gz
PKG_SOURCE_URL:=https://www.kernel.org/pub/linux/utils/kernel/hotplug
PKG_HASH:=skip

PKG_LICENSE:=GPL-2.0+
PKG_CPE_ID:=cpe:/a:kernel:udev

PKG_BUILD_PARALLEL:=1
PKG_FIXUP:=autoreconf
PKG_INSTALL:=1

include $(INCLUDE_DIR)/package.mk

define Package/udev
  SECTION:=base
  CATEGORY:=Base system
  TITLE:=udev - Dynamic device management
  DEPENDS:=+libblkid +kmod +libpthread
  URL:=https://www.kernel.org/pub/linux/utils/kernel/hotplug/udev
endef

define Package/udev/description
  udev is a device manager for the Linux kernel. It creates and removes
  device nodes in /dev dynamically, handles hotplug events, and loads
  the appropriate kernel modules.
endef

# Add group and user definitions
define UDEV_USERS
	- - input -1 * - - - Input device group
	- - kvm -1 * - - - KVM nodes
	- - sgx -1 * - - - SGX device nodes
endef

# 編譯選項
CONFIGURE_ARGS += \
	--disable-static \
	--enable-libkmod \
	--libexecdir=/usr/lib/udev \
	--sysconfdir=/etc \
	--with-systemdsystemunitdir=no

define Build/Compile
	$(MAKE) -C $(PKG_BUILD_DIR) \
		CC="$(TARGET_CC)" \
		CFLAGS="$(TARGET_CFLAGS)" \
		LDFLAGS="$(TARGET_LDFLAGS)"
endef

define Package/udev/install
	# 安裝二進位檔
	$(INSTALL_DIR) $(1)/sbin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/udevd $(1)/sbin/
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/udevadm $(1)/sbin/

	# 安裝 udev 規則
	$(INSTALL_DIR) $(1)/lib/udev/rules.d
	$(CP) $(PKG_BUILD_DIR)/rules.d/* $(1)/lib/udev/rules.d/

	# 安裝 libexec 目錄
	$(INSTALL_DIR) $(1)/usr/lib/udev
	$(CP) $(PKG_BUILD_DIR)/libexec/* $(1)/usr/lib/udev/
endef

$(eval $(call BuildPackage,udev))
