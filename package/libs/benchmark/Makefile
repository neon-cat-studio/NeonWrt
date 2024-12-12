include $(TOPDIR)/rules.mk

PKG_NAME:=benchmark
PKG_VERSION:=1.5.1
PKG_RELEASE:=1
PKG_SOURCE:=v$(PKG_VERSION).tar.gz
PKG_SOURCE_URL:=https://github.com/google/benchmark/archive
PKG_HASH:=23082937d1663a53b90cb5b61df4bcc312f6dee7018da78ba00dd6bd669dfef2

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/cmake.mk

ifeq ($(CONFIG_BIG_ENDIAN),y)
TARGET_CFLAGS+= -DHAVE_BIG_ENDIAN=1
endif
TARGET_CFLAGS+= -D_GNU_SOURCE

define Package/libbenchmark
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=google benchmark
  URL:=https://github.com/google/benchmark
  DEPENDS:= +libc +libstdcpp +libpthread
endef

TARGET_CFLAGS += $(FPIC) -ffunction-sections -fdata-sections -flto
TARGET_LDFLAGS += -Wl,--gc-sections,--as-needed -flto

CMAKE_OPTIONS += \
	-DBUILD_SHARED_LIBS=ON \
	-DBUILD_TESTING=OFF \
	-DHAVE_STD_REGEX=OFF \
	-DHAVE_POSIX_REGEX=OFF \
	-DHAVE_STEADY_CLOCK=OFF \
	-DBENCHMARK_ENABLE_GTEST_TESTS=OFF \
	-DBENCHMARK_ENABLE_TESTING=OFF \

define Build/Configure
	$(call Build/Configure/Default)
endef

define Package/libbenchmark/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libbenchmark.so.* $(1)/usr/lib/
	$(INSTALL_DIR) $(1)/usr/lib/pkgconfig
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/pkgconfig/*.pc $(1)/usr/lib/pkgconfig/
endef

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include
	$(CP) $(PKG_INSTALL_DIR)/usr/include/benchmark $(1)/usr/include/
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libbenchmark.so* $(1)/usr/lib/
endef

$(eval $(call BuildPackage,libbenchmark))