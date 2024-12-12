include $(TOPDIR)/rules.mk

PKG_NAME:=stemmer
PKG_VERSION:=0.5.2
PKG_RELEASE:=1
PKG_SOURCE:=v$(PKG_VERSION).tar.gz
PKG_SOURCE_URL:=https://github.com/bgamari/stemmer/archive
PKG_HASH:=c14a2172538742e0ce0253edba2fab8a4d1d0164ce6e1851c4e74a6cf6312304

include $(INCLUDE_DIR)/package.mk

ifeq ($(CONFIG_BIG_ENDIAN),y)
TARGET_CFLAGS+= -DHAVE_BIG_ENDIAN=1
endif
TARGET_CFLAGS+= -D_GNU_SOURCE

define Package/libstemmer
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=libstemmer_c
  URL:=https://github.com/bgamari/stemmer
endef

TARGET_CFLAGS += -I$(PKG_BUILD_DIR)/libstemmer_c/include

define Build/Compile
	rm -rf $(PKG_BUILD_DIR)/libstemmer_c/Makefile
	cp ./files/libstemmer_c/Makefile $(PKG_BUILD_DIR)/libstemmer_c/
	$(MAKE) -C $(PKG_BUILD_DIR)/libstemmer_c/ \
		$(TARGET_CONFIGURE_OPTS) \
		CFLAGS="$(TARGET_CFLAGS) $(TARGET_CPPFLAGS)" \
		LDFLAGS="$(TARGET_LDFLAGS)"
endef

define Package/libstemmer/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/libstemmer_c/*.{a,so*} $(1)/usr/lib/
endef

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include
	$(CP) $(PKG_BUILD_DIR)/libstemmer_c/include/libstemmer.h $(1)/usr/include
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_BUILD_DIR)/libstemmer_c/*.{a,so*} $(1)/usr/lib/
endef

$(eval $(call BuildPackage,libstemmer))