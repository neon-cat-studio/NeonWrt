include $(TOPDIR)/rules.mk

PKG_NAME:=gperftools
PKG_VERSION:=2.8
PKG_RELEASE:=1
PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.gz

PKG_SOURCE_URL:=https://github.com/gperftools/gperftools/releases/download/$(PKG_NAME)-$(PKG_VERSION)
PKG_HASH:=240deacdd628b6459671b83eb0c4db8e97baadf659f25b92e9a078d536bd513e

include $(INCLUDE_DIR)/package.mk

ifeq ($(CONFIG_BIG_ENDIAN),y)
TARGET_CFLAGS+= -DHAVE_BIG_ENDIAN=1
endif
TARGET_CFLAGS+= -D_GNU_SOURCE

define Package/libtcmalloc
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=google-perftools
  URL:=https://code.google.com/p/gperftools
  DEPENDS:= +libc +libstdcpp +libunwind
endef

TARGET_CFLAGS += $(FPIC)
CONFIGURE_VARS += CC="$(TARGET_CROSS)gcc"
CONFIGURE_ARGS += \
	--enable-shared \
	--enable-static \
	--without-readline \
	--disable-fft \

define Build/Compile
	$(call Build/Compile/Default, \
		DESTDIR="$(PKG_INSTALL_DIR)" \
		CC="$(TARGET_CC)" \
	)
endef

define Package/libtcmalloc/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/.libs/*.{a,so*} $(1)/usr/lib/
	$(INSTALL_DIR) $(1)/usr/lib/pkgconfig
	$(CP) $(PKG_BUILD_DIR)/*.pc $(1)/usr/lib/pkgconfig/
endef

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include
	$(CP) $(PKG_BUILD_DIR)/src/gperftools $(1)/usr/include/
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/.libs/*.{a,so*} $(1)/usr/lib/
endef

$(eval $(call BuildPackage,libtcmalloc))