include $(TOPDIR)/rules.mk

PKG_NAME:=docker-binary-x86_64
PKG_VERSION:=20.10.7
PKG_RELEASE:=1
PKG_FLAGS:=nonshared

PKG_BUILD_DIR:=$(BUILD_DIR)/docker
PKG_SOURCE:=docker-$(PKG_VERSION).tgz
PKG_SOURCE_URL:=https://download.docker.com/linux/static/stable/x86_64/
PKG_HASH:=34ad50146fce29b28e5115a1e8510dd5232459c9a4a9f28f65909f92cca314d9

include $(INCLUDE_DIR)/package.mk
include ../docker/docker-common.mk

define Package/docker-binary-x86_64
	$(call Package/docker-binary-common/default)
	DEPENDS+=@TARGET_x86_64
endef

define Package/docker-binary-x86_64/description
 Docker daemon (pre-compiled static binary)
endef

define Build/Compile
	ls
endef

define Package/docker-binary-x86_64/install
	$(call Package/docker-binary-common/install,$(1))
	$(INSTALL_DIR) $(1)/etc/config
	$(INSTALL_BIN) ../docker/files/dockerd.config $(1)/etc/config/docker
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ../docker/files/dockerd.init $(1)/etc/init.d/docker
endef

$(eval $(call BuildPackage,docker-binary-x86_64))
