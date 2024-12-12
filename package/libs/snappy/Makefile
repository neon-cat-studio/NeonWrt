include $(TOPDIR)/rules.mk

PKG_NAME:=snappy
PKG_VERSION:=1.1.8
PKG_RELEASE:=1
PKG_SOURCE:=$(PKG_VERSION).tar.gz
PKG_SOURCE_URL:=https://github.com/google/snappy/archive
PKG_HASH:=16b677f07832a612b0836178db7f374e414f94657c138e6993cbfc5dcc58651f

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/cmake.mk

ifeq ($(CONFIG_BIG_ENDIAN),y)
TARGET_CFLAGS+= -DHAVE_BIG_ENDIAN=1
endif
TARGET_CFLAGS+= -D_GNU_SOURCE

define Package/libsnappy
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=google snappy
  URL:=https://github.com/google/snappy
  DEPENDS:= +libc +libstdcpp +libpthread +libgtest
endef

TARGET_CFLAGS += $(FPIC) -ffunction-sections -fdata-sections -flto
TARGET_LDFLAGS += -Wl,--gc-sections,--as-needed -flto

CMAKE_OPTIONS += \
	-DBUILD_SHARED_LIBS=ON \
	-DBUILD_TESTING=OFF \
	-DSNAPPY_BUILD_TESTS=OFF \

define Build/Configure
	$(call Build/Configure/Default)
endef

define Package/libsnappy/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libsnappy.so.* $(1)/usr/lib/
endef

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include
	$(CP) $(PKG_INSTALL_DIR)/usr/include/* $(1)/usr/include/
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libsnappy.so* $(1)/usr/lib/
endef

$(eval $(call BuildPackage,libsnappy))