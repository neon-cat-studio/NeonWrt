include $(TOPDIR)/rules.mk

PKG_NAME:=s2geometry
PKG_VERSION:=0.9.0
PKG_RELEASE:=1
PKG_SOURCE:=v$(PKG_VERSION).tar.gz
PKG_SOURCE_URL:=https://github.com/google/s2geometry/archive
PKG_HASH:=54c09b653f68929e8929bffa60ea568e26f3b4a51e1b1734f5c3c037f1d89062

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/cmake.mk

ifeq ($(CONFIG_BIG_ENDIAN),y)
TARGET_CFLAGS+= -DHAVE_BIG_ENDIAN=1
endif
TARGET_CFLAGS+= -D_GNU_SOURCE

define Package/libs2
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=google-s2 (s2geometry) libraries
  URL:=https://github.com/google/s2geometry
  DEPENDS:= +libc +libstdcpp +libpthread +libopenssl +libgtest
endef

TARGET_CFLAGS += $(FPIC) -ffunction-sections -fdata-sections -flto
TARGET_LDFLAGS += -Wl,--gc-sections,--as-needed -flto

CMAKE_OPTIONS += \
	-DBUILD_SHARED_LIBS=ON \
	-DBUILD_TESTING=OFF \

define Build/Configure
	$(call Build/Configure/Default)
endef

define Package/libs2/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/*.so $(1)/usr/lib/
endef

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include
	$(CP) $(PKG_INSTALL_DIR)/usr/include/* $(1)/usr/include/
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/*.so $(1)/usr/lib/
endef

$(eval $(call BuildPackage,libs2))