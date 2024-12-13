include $(TOPDIR)/rules.mk

PKG_NAME:=mobile-broadband-provider-info
PKG_RELEASE:=1

PKG_VERSION:=20210805
PKG_HASH:=6bf8a1558ea5541afbc6f7b4415e74cc9f5aa9829b134ecab3ef1c87412568bc
PKG_SOURCE_URL:=http://ftp.gnome.org/pub/GNOME/sources/$(PKG_NAME)/$(PKG_VERSION)/
PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.xz
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/autotools.mk

define Package/mobile-broadband-provider-info
  SECTION:=net
  CATEGORY:=Network
  TITLE:=mobile-broadband-provider-info
  URL:=http://live.gnome.org/NetworkManager/MobileBroadband/ServiceProviders
  DEPENDS:=
endef

define Package/mobile-broadband-provider-info/description
Mobile broadband provider database.

http://live.gnome.org/NetworkManager/MobileBroadband/ServiceProviders
endef

TARGET_CFLAGS += $(if $(CONFIG_USE_UCLIBC),-D_BSD_SOURCE)

define Package/mobile-broadband-provider-info/install
	$(INSTALL_DIR) $(1)/usr/bin/xsltproc
	$(CP) $(PKG_BUILD_DIR)/apns-conf.xml $(1)/usr/bin/xsltproc
	$(CP) $(PKG_BUILD_DIR)/apns-conf.xsl $(1)/usr/bin/xsltproc
	$(CP) $(PKG_BUILD_DIR)/serviceproviders.xml $(1)/usr/bin/xsltproc
endef

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/bin/xsltproc
	$(CP) $(PKG_BUILD_DIR)/apns-conf.xml $(1)/usr/bin/xsltproc
	$(CP) $(PKG_BUILD_DIR)/apns-conf.xsl $(1)/usr/bin/xsltproc
	$(CP) $(PKG_BUILD_DIR)/serviceproviders.xml $(1)/usr/bin/xsltproc
endef

$(eval $(call BuildPackage,mobile-broadband-provider-info))
