include $(TOPDIR)/rules.mk

PKG_NAME:=smack
PKG_RELEASE:=1

PKG_VERSION:=1.3.1
PKG_HASH:=1a607da3b1a661dc76b7a5b8571f4a2d56b4d61d78376088d19f2d8637dc6822

PKG_SOURCE_URL:=https://github.com/smack-team/smack/archive/refs/tags/
PKG_SOURCE:=v$(PKG_VERSION).tar.gz
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)

PKG_FIXUP:=autoreconf

include $(INCLUDE_DIR)/package.mk

define Package/smack
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=smack
  URL:=https://github.com/smack-team/
  DEPENDS:=+libc +libpthread +@KERNEL_SECURITY +@KERNEL_SECURITY_SMACK +@KERNEL_SECURITY_NETWORK
endef

TARGET_CFLAGS += $(FPIC)
CONFIGURE_ARGS += \
	--enable-shared \
	--enable-static \
	--disable-tests \
	--disable-xml-docs \
	--disable-doxygen-docs \

CONFIGURE_VARS+= \
	ac_cv_func_posix_getpwnam_r="yes" \
	ac_cv_have_abstract_sockets="yes" \
	CPPFLAGS="$$$$CPPFLAGS -I$(ICONV_PREFIX)/include" \
	CPPFLAGS="$$$$CPPFLAGS -I$(INTL_PREFIX)/include" \
	LDFLAGS="$$$$LDFLAGS -L$(ICONV_PREFIX)/lib -Wl,-rpath-link=$(ICONV_PREFIX)/lib" \
	LDFLAGS="$$$$LDFLAGS -L$(INTL_PREFIX)/lib -Wl,-rpath-link=$(INTL_PREFIX)/lib" \

define Build/Compile
	$(call Build/Compile/Default, \
		DESTDIR="$(PKG_INSTALL_DIR)" \
		CC="$(TARGET_CC)" \
	)
endef

define Package/smack/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/libsmack/.libs/*.{a,so*} $(1)/usr/lib/
endef

$(eval $(call BuildPackage,smack))
