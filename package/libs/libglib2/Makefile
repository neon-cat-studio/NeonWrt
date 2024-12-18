# OpenWRT Package Makefile for libglib2
#
# SPDX-License-Identifier: LGPL-2.1+

include $(TOPDIR)/rules.mk

PKG_NAME:=libglib2
PKG_VERSION:=2.76.1
PKG_RELEASE:=1

PKG_SOURCE:=glib-$(PKG_VERSION).tar.xz
PKG_SOURCE_URL:=https://download.gnome.org/sources/glib/2.76
PKG_HASH:=skip

PKG_LICENSE:=LGPL-2.1+
PKG_LICENSE_FILES:=COPYING

PKG_BUILD_PARALLEL:=1
PKG_FIXUP:=meson
PKG_INSTALL:=1

HOST_BUILD_DEPENDS:=host-pkgconf host-libffi host-pcre2

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/meson.mk

define Package/libglib2
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=GLib 2 - Core Application and Utility Library
  DEPENDS:=+libffi +libpcre2 +zlib
  URL:=https://developer.gnome.org/glib/
endef

define Package/libglib2/description
  GLib provides the core application building blocks for libraries and applications
  written in C. It provides data structure handling, portability wrappers, and more.
endef

# 配置選項
MESON_OPTIONS += \
	-Dglib_debug=disabled \
	-Dtests=false \
	-Doss_fuzz=disabled \
	-Dgio_module_dir=/usr/lib/gio/modules

ifeq ($(CONFIG_PACKAGE_libiconv),y)
  MESON_OPTIONS += -Dlibiconv=true
  DEPENDS += +libiconv
else
  MESON_OPTIONS += -Dlibiconv=false
endif

ifeq ($(CONFIG_PACKAGE_util-linux),y)
  MESON_OPTIONS += -Dlibmount=enabled
  DEPENDS += +util-linux
else
  MESON_OPTIONS += -Dlibmount=disabled
endif

ifeq ($(CONFIG_PACKAGE_libselinux),y)
  MESON_OPTIONS += -Dselinux=enabled -Dxattr=true
  DEPENDS += +libselinux
else
  MESON_OPTIONS += -Dselinux=disabled -Dxattr=false
endif

# 針對 ARM Thumb1 特殊編譯選項
ifeq ($(CONFIG_ARM_THUMB),y)
  TARGET_CFLAGS += -marm
endif

# 清理不必要的文件
define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include/glib-2.0
	$(CP) $(PKG_BUILD_DIR)/glib/*.h $(1)/usr/include/glib-2.0
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/.libs/*.so* $(1)/usr/lib/
endef

define Package/libglib2/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/.libs/*.so* $(1)/usr/lib/

	# 清理開發工具和 gdb 文件
	rm -rf $(1)/usr/lib/glib-2.0
	rm -f $(1)/usr/bin/gdbus-codegen
endef

define Package/libglib2/postinst
#!/bin/sh
# 編譯 GLib schemas
if [ -x /usr/bin/glib-compile-schemas ]; then
    glib-compile-schemas /usr/share/glib-2.0/schemas
fi
endef

$(eval $(call BuildPackage,libglib2))
