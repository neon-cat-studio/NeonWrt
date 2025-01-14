################################################################################
#
# cracklib
#
################################################################################

include $(TOPDIR)/rules.mk

PKG_NAME:=cracklib
PKG_VERSION:=2.9.11
PKG_RELEASE:=1

PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.xz
PKG_SOURCE_URL:=https://github.com/cracklib/cracklib/releases/download/v$(PKG_VERSION)
PKG_HASH:=skip

PKG_LICENSE:=LGPL-2.1
PKG_LICENSE_FILES:=COPYING.LIB
PKG_CPE_ID_VALID:=YES

PKG_INSTALL:=1
PKG_BUILD_FLAGS:=gc-sections lto

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/host-build.mk
include $(INCLUDE_DIR)/nls.mk

define Package/cracklib
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=Password validation library
  URL:=https://github.com/cracklib/cracklib
  DEPENDS:=$(TARGET_NLS_DEPENDS) zlib
endef

define Package/cracklib/description
  CrackLib is a library to enforce strong passwords by checking for weak or
  easily guessable passwords.
endef

define Package/cracklib-tools
  SECTION:=utils
  CATEGORY:=Utilities
  TITLE:=Password validation tools for cracklib
  DEPENDS:=+cracklib
endef

define Package/cracklib-tools/description
  Tools for password validation and dictionary management using cracklib.
endef

CRACKLIB_DEPENDENCIES := $(TARGET_NLS_DEPENDS)
CRACKLIB_CONF_ENV = LIBS=$(TARGET_NLS_LIBS)

ifeq ($(CONFIG_PACKAGE_ZLIB),y)
CRACKLIB_CONF_OPTS += --with-zlib
CRACKLIB_DEPENDENCIES += zlib
else
CRACKLIB_CONF_OPTS += --without-zlib
endif

ifeq ($(CONFIG_PACKAGE_PYTHON3),y)
CRACKLIB_AUTORECONF = YES
CRACKLIB_CONF_OPTS += --with-python
CRACKLIB_CONF_ENV += ac_cv_path_PYTHON=$(HOST_DIR)/bin/python3
CRACKLIB_DEPENDENCIES += python3
else
CRACKLIB_CONF_OPTS += --without-python
endif

HOST_CRACKLIB_CONF_OPTS += --without-python --without-zlib

ifeq ($(CONFIG_PACKAGE_CRACKLIB_FULL_DICT),y)
CRACKLIB_EXTRA_DOWNLOADS := cracklib-words-$(PKG_VERSION).xz
CRACKLIB_DICT_SOURCE := $(DL_DIR)/cracklib-words-$(PKG_VERSION).xz
else
CRACKLIB_DICT_SOURCE := $(@D)/dicts/cracklib-small
endif

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include
	$(CP) $(PKG_INSTALL_DIR)/usr/include/crack.h $(1)/usr/include/
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libcrack*.so* $(1)/usr/lib/
endef

ifeq ($(CONFIG_PACKAGE_CRACKLIB_TOOLS),n)
define CRACKLIB_REMOVE_TOOLS
	rm -f $(TARGET_DIR)/usr/sbin/*cracklib*
endef
CRACKLIB_POST_INSTALL_TARGET_HOOKS += CRACKLIB_REMOVE_TOOLS
endif

define CRACKLIB_BUILD_DICT
	mkdir -p $(TARGET_DIR)/usr/share/cracklib
	$(HOST_BUILD_DIR)/src/cracklib-format $(CRACKLIB_DICT_SOURCE) | \
		$(HOST_BUILD_DIR)/src/cracklib-packer $(TARGET_DIR)/usr/share/cracklib/pw_dict
endef
CRACKLIB_POST_INSTALL_TARGET_HOOKS += CRACKLIB_BUILD_DICT

define Package/cracklib/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libcrack.so* $(1)/usr/lib/
endef

define Package/cracklib-tools/install
	$(INSTALL_DIR) $(1)/usr/sbin
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/sbin/* $(1)/usr/sbin/
endef

$(eval $(call BuildPackage,cracklib))
$(eval $(call BuildPackage,cracklib-tools))
