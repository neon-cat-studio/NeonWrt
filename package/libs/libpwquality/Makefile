################################################################################
#
# libpwquality
#
################################################################################

include $(TOPDIR)/rules.mk

PKG_NAME:=libpwquality
PKG_VERSION:=1.4.5
PKG_RELEASE:=1

PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.bz2
PKG_SOURCE_URL:=https://github.com/libpwquality/libpwquality/releases/download/$(PKG_NAME)-$(PKG_VERSION)
PKG_HASH:=skip

PKG_LICENSE:=BSD-3-Clause OR GPL-2.0+
PKG_LICENSE_FILES:=COPYING
PKG_INSTALL:=1

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/autotools.mk

define Package/libpwquality
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=Password quality checking library
  URL:=https://github.com/libpwquality/libpwquality
  DEPENDS:=+cracklib $(if $(CONFIG_LIBPWQUALITY_PAM),+linux-pam)
endef

define Package/libpwquality/description
  libpwquality provides common functions for password quality checking
  and generation as well as PAM and Python bindings.
endef

define Package/libpwquality-tools
  SECTION:=utils
  CATEGORY:=Utilities
  TITLE:=Tools for libpwquality
  DEPENDS:=+libpwquality
endef

define Package/libpwquality-tools/description
  Utilities for password generation (pwmake) and password quality scoring (pwscore).
endef

ifeq ($(CONFIG_LIBPWQUALITY_PAM),y)
LIBPWQUALITY_CONF_OPTS += --enable-pam --with-securedir=/lib/security
else
LIBPWQUALITY_CONF_OPTS += --disable-pam
endif

ifeq ($(CONFIG_PACKAGE_PYTHON3),y)
PYTHON_VERSION := $(shell python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
LIBPWQUALITY_CONF_OPTS += --enable-python-bindings \
    --with-python=$(STAGING_DIR)/usr/include/$(PYTHON_VERSION)
LIBPWQUALITY_DEPENDENCIES += python3 host-python-setuptools
LIBPWQUALITY_MAKE_ENV += $(PKG_PYTHON_SETUPTOOLS_ENV)
LIBPWQUALITY_MAKE_ENV += \
    PYTHON_CPPFLAGS="-I$(STAGING_DIR)/usr/include/(PYTHON_VERSION)" \
    PYTHON_LDFLAGS="-L$(STAGING_DIR)/usr/lib" \
    PKG_CONFIG_PATH=$(STAGING_DIR)/usr/lib/pkgconfig
else
LIBPWQUALITY_CONF_OPTS += --disable-python-bindings
endif

# Remove tools if not selected
ifeq ($(CONFIG_LIBPWQUALITY_TOOLS),n)
define LIBPWQUALITY_REMOVE_TOOLS
	rm -f $(TARGET_DIR)/usr/bin/pwmake
	rm -f $(TARGET_DIR)/usr/bin/pwscore
endef
LIBPWQUALITY_POST_INSTALL_TARGET_HOOKS += LIBPWQUALITY_REMOVE_TOOLS
endif

define Package/libpwquality/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libpwquality.so* $(1)/usr/lib/
endef

define Package/libpwquality-tools/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/bin/pwmake $(1)/usr/bin/
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/bin/pwscore $(1)/usr/bin/
endef

$(eval $(call BuildPackage,libpwquality))
$(eval $(call BuildPackage,libpwquality-tools))
