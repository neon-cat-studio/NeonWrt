include $(TOPDIR)/rules.mk

PKG_NAME:=docker-binary-aarch64
PKG_VERSION:=20.10.7
PKG_RELEASE:=1
PKG_FLAGS:=nonshared

PKG_BUILD_DIR:=$(BUILD_DIR)/docker
PKG_SOURCE:=docker-$(PKG_VERSION).tgz
PKG_SOURCE_URL:=https://download.docker.com/linux/static/stable/aarch64/
PKG_HASH:=be8c9a5a06ebec8fb1d36e867cd00fb5777746a9812a0cae2966778ff899c525

include $(INCLUDE_DIR)/package.mk
include ../docker/docker-common.mk

define Package/docker-binary-aarch64
	$(call Package/docker-binary-common/default)
	DEPENDS+=@aarch64
endef

define Package/docker-binary-aarch64/description
	$(call Pckage/docker-binary-common/description)
endef

define Package/docker-binary-aarch64/conffiles
	$(call Package/docker-common/conffiles)
endef

define Build/Compile
	ls
endef

define Package/docker-binary-aarch64/install
	$(call Package/docker-binary-common/install,$(1))
	$(INSTALL_DIR) $(1)/etc/config
	$(INSTALL_BIN) ../docker/files/dockerd.config $(1)/etc/config/docker
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ../docker/files/dockerd.init $(1)/etc/init.d/docker
endef

$(eval $(call BuildPackage,docker-binary-aarch64))
