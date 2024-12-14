# OpenWRT Package Makefile for efl
#
# SPDX-License-Identifier: BSD-2-Clause AND LGPL-2.1+ AND GPL-2.0+ AND MIT AND FTL

include $(TOPDIR)/rules.mk

PKG_NAME:=efl
PKG_VERSION:=1.26.3
PKG_RELEASE:=1

PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.xz
PKG_SOURCE_URL:=https://download.enlightenment.org/rel/libs/efl
PKG_HASH:=skip

PKG_LICENSE:=BSD-2-Clause AND LGPL-2.1+ AND GPL-2.0+ AND MIT AND FTL
PKG_LICENSE_FILES:=COPYING licenses/COPYING.*

PKG_BUILD_PARALLEL:=1
PKG_FIXUP:=meson
PKG_INSTALL:=1

PKG_BUILD_DEPENDS:=libpng libfreetype libjpeg-turble luajit libglib2 zlib liblz4

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/meson.mk

define Package/efl
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=Enlightenment Foundation Libraries
  DEPENDS:=+libpng +libfreetype +libjpeg-turble +libglib2 +luajit +zlib +liblz4
  URL:=https://www.enlightenment.org
endef

define Package/efl/description
  EFL (Enlightenment Foundation Libraries) is a set of libraries to build
  rich and fast applications with beautiful UIs. It is the base for the
  Enlightenment desktop environment.
endef

# 配置選項
MESON_OPTIONS += \
	-Dbuild-examples=false \
	-Dbuild-tests=false \
	-Dnative-arch-optimization=false \
	-Dlua-interpreter=luajit \
	-Dembedded-lz4=false \
	-Dnetwork-backend=none \
	-Dsdl=false \
	-Dnls=false \
	-Dpixman=false \
	-Dsystemd=false \
	-Dvnc-server=false

# 可選依賴選項
ifeq ($(CONFIG_PACKAGE_fontconfig),y)
  MESON_OPTIONS += -Dfontconfig=true
  DEPENDS += +fontconfig
else
  MESON_OPTIONS += -Dfontconfig=false
endif

ifeq ($(CONFIG_PACKAGE_libfribidi),y)
  MESON_OPTIONS += -Dfribidi=true
  DEPENDS += +libfribidi
else
  MESON_OPTIONS += -Dfribidi=false
endif

ifeq ($(CONFIG_PACKAGE_pulseaudio),y)
  MESON_OPTIONS += -Dpulseaudio=true
  DEPENDS += +pulseaudio
else
  MESON_OPTIONS += -Dpulseaudio=false
endif

ifeq ($(CONFIG_PACKAGE_wayland),y)
  MESON_OPTIONS += -Dwl=true
  DEPENDS += +wayland +wayland-protocols
else
  MESON_OPTIONS += -Dwl=false
endif

ifeq ($(CONFIG_PACKAGE_libdrm),y)
  MESON_OPTIONS += -Ddrm=true
  DEPENDS += +libdrm +libegl +mesa3d
else
  MESON_OPTIONS += -Ddrm=false
endif

# OpenGL 支援
ifeq ($(CONFIG_PACKAGE_libgl),y)
  MESON_OPTIONS += -Dopengl=full
  DEPENDS += +libgl
else ifeq ($(CONFIG_PACKAGE_libgles),y)
  MESON_OPTIONS += -Dopengl=es-egl
  DEPENDS += +libgles +libegl
else
  MESON_OPTIONS += -Dopengl=none
endif

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include/efl
	$(CP) $(PKG_BUILD_DIR)/src/*.h $(1)/usr/include/efl
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/lib/*.so* $(1)/usr/lib/
endef

define Package/efl/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/lib/*.so* $(1)/usr/lib/
endef

$(eval $(call BuildPackage,efl))
