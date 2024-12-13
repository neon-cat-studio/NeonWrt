# OpenWRT Package Makefile for pcre2
#
# SPDX-License-Identifier: BSD-3-Clause

include $(TOPDIR)/rules.mk

PKG_NAME:=pcre2
PKG_VERSION:=10.43
PKG_RELEASE:=1

PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.bz2
PKG_SOURCE_URL:=https://github.com/PCRE2Project/pcre2/releases/download/pcre2-$(PKG_VERSION)
PKG_HASH:=skip

PKG_LICENSE:=BSD-3-Clause
PKG_LICENSE_FILES:=LICENCE

PKG_FIXUP:=autoreconf
PKG_INSTALL:=1

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/host-build.mk

define Package/pcre2
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=PCRE2 - Perl Compatible Regular Expressions Library (v2)
  URL:=https://www.pcre.org/
  DEPENDS:=
endef

define Package/pcre2/description
  PCRE2 is a library for implementing regular expressions, compatible with Perl 5.
  It provides multiple coding options, including 8-bit, 16-bit, and 32-bit libraries.
endef

# 配置選項
CONFIGURE_ARGS += \
	--enable-pcre2-8 \
	$(if $(CONFIG_PACKAGE_pcre2_16),--enable-pcre2-16,--disable-pcre2-16) \
	$(if $(CONFIG_PACKAGE_pcre2_32),--enable-pcre2-32,--disable-pcre2-32) \
	$(if $(CONFIG_PACKAGE_pcre2_jit),--enable-jit,--disable-jit)

ifeq ($(CONFIG_USE_MMU),)
CONFIGURE_ARGS += --disable-pcre2grep-callout
endif

# Install development headers and libraries
define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include
	$(CP) $(PKG_BUILD_DIR)/include/*.h $(1)/usr/include/

	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/.libs/libpcre2*.so* $(1)/usr/lib/

	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/pcre2-config $(1)/usr/bin/
endef

define Package/pcre2/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/.libs/libpcre2-8.so* $(1)/usr/lib/
	$(if $(CONFIG_PACKAGE_pcre2_16), \
		$(CP) $(PKG_BUILD_DIR)/.libs/libpcre2-16.so* $(1)/usr/lib/)
	$(if $(CONFIG_PACKAGE_pcre2_32), \
		$(CP) $(PKG_BUILD_DIR)/.libs/libpcre2-32.so* $(1)/usr/lib/)
endef

define Host/Configure
	$(call Host/Configure/Default, \
		--enable-pcre2-16 \
		--disable-pcre2grep-callout)
endef

define Host/Compile
	$(MAKE) -C $(HOST_BUILD_DIR)
endef

define Host/Install
	$(INSTALL_DIR) $(STAGING_DIR_HOST)/bin
	$(INSTALL_BIN) $(HOST_BUILD_DIR)/pcre2-config $(STAGING_DIR_HOST)/bin/
endef

$(eval $(call BuildPackage,pcre2))
$(eval $(call HostBuild))
