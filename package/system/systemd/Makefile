include $(TOPDIR)/rules.mk

PKG_NAME:=systemd
PKG_VERSION:=256.7
PKG_RELEASE:=1

PKG_SOURCE:=$(PKG_NAME)-v$(PKG_VERSION).tar.gz
PKG_SOURCE_URL:=https://github.com/systemd/systemd/archive/v$(PKG_VERSION)
PKG_HASH:=skip

PKG_LICENSE:=LGPL-2.1+ GPL-2.0+
PKG_LICENSE_FILES:=LICENSE.GPL2 LICENSE.LGPL2.1

PKG_BUILD_PARALLEL:=1
PKG_INSTALL:=1

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/meson.mk   # 改用 meson.mk

define Package/systemd
  SECTION:=base
  CATEGORY:=Base system
  TITLE:=Systemd init system
  DEPENDS:=+libc +libcap +libxcrypt +kmod +mount-utils +fdisk +lsblk +blkid +logger
endef

define Package/systemd/description
  systemd is a modern init system and system manager for Linux.
endef

TARGET_CFLAGS += -O3 -fno-finite-math-only
MESON_ARGS += \
	-Dgshadow=false \
    -Dc_args='-DENABLE_GSHADOW=0' \
    -Dcpp_args='-DENABLE_GSHADOW=0'
	-Ddefault-locale='C.UTF-8' \
	-Ddefault-user-shell=/bin/sh \
	-Dkexec-path=/usr/sbin/kexec \
	-Dkmod-path=/usr/bin/kmod \
	-Dmount-path=/usr/bin/mount \
	-Dumount-path=/usr/bin/umount \
	-Dsystem-uid-max=999 \
	-Dsystem-gid-max=999 \
	-Dsysvinit-path= \
	-Dsplit-bin=true \
	-Dtests=false \
	-Dinstall-tests=false \
	-Ddefault-dnssec=allow-downgrade

define Package/systemd/install
	$(INSTALL_DIR) $(1)/usr/lib/systemd
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/systemd/* $(1)/usr/lib/systemd/

	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/bin/systemctl $(1)/usr/bin/
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/bin/journalctl $(1)/usr/bin/

	# 安裝 init.d 啟動腳本
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ./files/systemd.init $(1)/etc/init.d/systemd

	# 安裝 system.conf 配置檔案
	$(INSTALL_DIR) $(1)/etc/systemd
	$(INSTALL_CONF) ./files/system.conf $(1)/etc/systemd/system.conf
endef

define Package/systemd/postinst
#!/bin/sh
echo "systemd installation completed."
endef

define Package/systemd/prerm
#!/bin/sh
echo "systemd removal completed."
endef

$(eval $(call BuildPackage,systemd))
