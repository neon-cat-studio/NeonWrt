################################################################################
#
# libqrencode
#
################################################################################

include $(TOPDIR)/rules.mk

PKG_NAME:=libqrencode
PKG_VERSION:=4.1.1
PKG_RELEASE:=1

PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.gz
PKG_SOURCE_URL:=http://fukuchi.org/works/qrencode
PKG_HASH:=skip

PKG_LICENSE:=LGPL-2.1+
PKG_LICENSE_FILES:=COPYING

PKG_BUILD_DEPENDS:=host-pkgconf
PKG_INSTALL:=1

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/autotools.mk

define Package/libqrencode
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=QR Code encoding library
  URL:=http://fukuchi.org/works/qrencode
  DEPENDS:=$(if $(CONFIG_LIBQRENCODE_PNG),+libpng)
endef

define Package/libqrencode/description
  libqrencode is a library for encoding data in a QR Code symbol.
endef

define Package/libqrencode-tools
  SECTION:=utils
  CATEGORY:=Utilities
  TITLE:=QR Code encoding tools
  URL:=http://fukuchi.org/works/qrencode
  DEPENDS:=+libqrencode
endef

define Package/libqrencode-tools/description
  Tools for generating QR Code images using libqrencode.
endef

ifeq ($(CONFIG_LIBQRENCODE_PNG),y)
LIBQRENCODE_CONF_OPTS += --with-png
else
LIBQRENCODE_CONF_OPTS += --without-png
endif

ifeq ($(CONFIG_LIBQRENCODE_TOOLS),y)
LIBQRENCODE_CONF_OPTS += --with-tools
else
LIBQRENCODE_CONF_OPTS += --without-tools
endif

ifeq ($(BR2_TOOLCHAIN_HAS_THREADS),y)
LIBQRENCODE_CONF_ENV += LIBS='-pthread'
else
LIBQRENCODE_CONF_OPTS += --disable-thread-safety
endif

define Package/libqrencode/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libqrencode.so* $(1)/usr/lib/
endef

define Package/libqrencode-tools/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/bin/qrencode $(1)/usr/bin/
endef

$(eval $(call BuildPackage,libqrencode))
$(eval $(call BuildPackage,libqrencode-tools))
