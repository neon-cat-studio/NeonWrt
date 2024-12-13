include $(TOPDIR)/rules.mk

MESON=tools/meson/meson
NINJA=tools/ninja/ninja

PKG_NAME:=networkmanager
PKG_RELEASE:=1

PKG_VERSION:=1.32.10
PKG_HASH:=72cb2a738127a05f69302f5df098304cc2da45d352391a26b9534c97bef22ca5

PKG_SOURCE_URL:=https://github.com/NetworkManager/NetworkManager/archive/refs/tags/
PKG_SOURCE:=$(PKG_VERSION).tar.gz
PKG_BUILD_DIR:=$(BUILD_DIR)/NetworkManager-$(PKG_VERSION)
PKG_BUILD_DEPENDS:=meson/host ninja/host intltool/host glib2/host

include $(INCLUDE_DIR)/package.mk
include $(TOPDIR)/feeds/packages/devel/meson/meson.mk

NWK_MGR_DEPENDS:=+dbus +gnutls-utils +glib2 +libgcrypt +libreadline +libndp +libuuid \
				+libaudit +libselinux +libnewt +libpsl +libudev-zero +wireless-tools +modemmanager \
				+mobile-broadband-provider-info

define Package/networkmanager
  SECTION:=net
  CATEGORY:=Network
  SUBMENU:=NetworkManager
  TITLE:=networkmanager
  URL:=https://github.com/NetworkManager/NetworkManager/
  DEPENDS:=$(NWK_MGR_DEPENDS)
endef

define Package/networkmanager/description
NetworkManager is a set of co-operative tools that make
networking simple and straightforward. Whether WiFi, wired,
3G, or Bluetooth, NetworkManager allows you to quickly move
from one network to another: once a network has been
configured and joined once, it can be detected and re-joined
automatically the next time it's available.

http://projects.gnome.org/NetworkManager/
endef

define Package/networkmanager-nmtui
  SECTION:=net
  CATEGORY:=Network
  SUBMENU:=NetworkManager
  TITLE:=networkmanager-tui
  DEPENDS:=+networkmanager +libnewt
endef

define Package/networkmanager-nmtui/description
This option enables terminal based UI
endef

define Package/networkmanager-modemmanager
  SECTION:=net
  CATEGORY:=Network
  SUBMENU:=NetworkManager
  TITLE:=networkmanager-pppd
  DEPENDS:=+networkmanager +modemmanager
endef

define Package/networkmanager-modemmanager/description
This option enables support for ModemManager
endef

define Package/networkmanager-pppd
  SECTION:=net
  CATEGORY:=Network
  SUBMENU:=NetworkManager
  TITLE:=networkmanager-pppd
  DEPENDS:=+networkmanager +ppp
endef

define Package/networkmanager-pppd/description
This option enables support for PPPD daemon
endef

define Package/networkmanager-openvswitch
  SECTION:=net
  CATEGORY:=Network
  SUBMENU:=NetworkManager
  TITLE:=networkmanager-openvswitch
  DEPENDS:=+networkmanager +jansson
endef

define Package/networkmanager-openvswitch/description
This option enables support for OpenVSwitch
endef

TARGET_CFLAGS += $(if $(CONFIG_USE_UCLIBC),-D_BSD_SOURCE)

MESON_VARS = \
	ac_cv_path_LIBGCRYPT_CONFIG=$(STAGING_DIR)/usr/bin/libgcrypt-config \
	ac_cv_file__etc_fedora_release=no \
	ac_cv_file__etc_mandriva_release=no \
	ac_cv_file__etc_debian_version=no \
	ac_cv_file__etc_redhat_release=no \
	ac_cv_file__etc_SuSE_release=no

MESON_ARGS = \
	-Dpolkit=false \
	-Dsession_tracking=no \
	-Dsystemdsystemunitdir=no \
	-Dsystemd_journal=false \
	-Dudev_dir=$(STAGING_DIR)/usr/lib \
	-Dintrospection=false \
	-Dtests=no \
	-Dqt=false \
	-Dcrypto=gnutls \
	-Diptables=/usr/sbin/iptables \
	-Difupdown=false \
	-Dnm_cloud_setup=false

ifeq ($(CONFIG_PACKAGE_ofono),y)
NWK_MGR_DEPENDS += ofono
MESON_ARGS += -Dofono=true
else
MESON_ARGS += -Dofono=false
endif

ifeq ($(CONFIG_PACKAGE_libcurl),y)
NWK_MGR_DEPENDS += libcurl
MESON_ARGS += -Dconcheck=true
else
MESON_ARGS += -Dconcheck=false
endif

ifeq ($(CONFIG_PACKAGE_networkmanager-nmtui),y)
MESON_ARGS += -Dnmtui=true
else
MESON_ARGS += -Dnmtui=false
endif

ifeq ($(CONFIG_PACKAGE_networkmanager-modemmanager),y)
MESON_ARGS += -Dmodem_manager=true
else
MESON_ARGS += -Dmodem_manager=false
endif

ifeq ($(CONFIG_PACKAGE_networkmanager-pppd),y)
MESON_ARGS += -Dppp=true
else
MESON_ARGS += -Dppp=false
endif

ifeq ($(CONFIG_PACKAGE_networkmanager-openvswitch),y)
MESON_ARGS += -Dovs=true
else
MESON_ARGS += -Dovs=false
endif

NWK_MGR_CONFIG_DHCP_CLIENT:=n
ifeq ($(CONFIG_PACKAGE_isc-dhcp-client-ipv4),y)
NWK_MGR_CONFIG_DHCP_CLIENT:=y
endif
ifeq ($(CONFIG_PACKAGE_isc-dhcp-client-ipv6),y)
NWK_MGR_CONFIG_DHCP_CLIENT:=y
endif

ifeq ($(NWK_MGR_CONFIG_DHCP_CLIENT),y)
MESON_ARGS += -Ddhclient=/sbin/dhclient
endif

ifeq ($(CONFIG_PACKAGE_dnsmasq),y)
MESON_ARGS += -Ddhcpcd=/sbin/dhcpcd
endif

define Package/networkmanager/install
	$(INSTALL_DIR) $(1)/etc/NetworkManager/conf.d \
	$(1)/etc/NetworkManager/dispatcher.d/no-wait.d \
	$(1)/etc/NetworkManager/dispatcher.d/pre-down.d \
	$(1)/etc/NetworkManager/dispatcher.d/pre-up.d \
	$(1)/etc/NetworkManager/dnsmasq.d \
	$(1)/etc/NetworkManager/dnsmasq-shared.d \
	$(1)/etc/NetworkManager/system-connections

	$(INSTALL_DIR) $(1)/usr/bin/
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/bin/nmcli $(1)/usr/bin/nmcli
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/bin/nm-online $(1)/usr/bin/nm-online

	$(INSTALL_DIR) $(1)/usr/include/libnm/
	$(CP) $(PKG_INSTALL_DIR)/usr/include/libnm/*.h $(1)/usr/include/libnm

	$(INSTALL_DIR) $(1)/usr/lib/
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libnm.so* $(1)/usr/lib

	$(INSTALL_DIR) $(1)/usr/lib/firewalld/zones
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/firewalld/zones/*.xml $(1)/usr/lib/firewalld/zones

	$(INSTALL_DIR) $(1)/usr/lib/NetworkManager/$(PKG_VERSION)/
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/NetworkManager/$(PKG_VERSION)/libnm-device-plugin-adsl.so \
		$(1)/usr/lib/NetworkManager/$(PKG_VERSION)/
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/NetworkManager/$(PKG_VERSION)/libnm-device-plugin-wifi.so \
		$(1)/usr/lib/NetworkManager/$(PKG_VERSION)/
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/NetworkManager/$(PKG_VERSION)/libnm-settings-plugin-ifupdown.so \
		$(1)/usr/lib/NetworkManager/$(PKG_VERSION)/

	$(INSTALL_DIR) $(1)/usr/lib/NetworkManager/conf.d
	$(INSTALL_DIR) $(1)/usr/lib/NetworkManager/dispatcher.d/no-wait.d
	$(INSTALL_DIR) $(1)/usr/lib/NetworkManager/dispatcher.d/pre-down.d
	$(INSTALL_DIR) $(1)/usr/lib/NetworkManager/dispatcher.d/pre-up.d
	$(INSTALL_DIR) $(1)/usr/lib/NetworkManager/system-connections
	$(INSTALL_DIR) $(1)/usr/lib/NetworkManager/VPN

	$(INSTALL_DIR) $(1)/usr/libexec/
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/libexec/nm-daemon-helper $(1)/usr/libexec/nm-daemon-helper
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/libexec/nm-dhcp-helper $(1)/usr/libexec/nm-dhcp-helper
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/libexec/nm-dispatcher $(1)/usr/libexec/nm-dispatcher
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/libexec/nm-iface-helper $(1)/usr/libexec/nm-iface-helper
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/libexec/nm-initrd-generator $(1)/usr/libexec/nm-initrd-generator

	$(INSTALL_DIR) $(1)/usr/sbin/
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/sbin/NetworkManager  $(1)/usr/sbin/NetworkManager

	$(INSTALL_DIR) $(1)/usr/share/bash-completion/completions
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/share/bash-completion/completions/nmcli $(1)/usr/share/bash-completion/completions/nmcli

	$(INSTALL_DIR) $(1)/usr/share/dbus-1/interfaces
	$(CP) $(PKG_INSTALL_DIR)/usr/share/dbus-1/interfaces/*.xml $(1)/usr/share/dbus-1/interfaces

	$(INSTALL_DIR) $(1)/usr/share/dbus-1/system.d
	$(CP) $(PKG_INSTALL_DIR)/usr/share/dbus-1/system.d/*.conf $(1)/usr/share/dbus-1/system.d

	$(INSTALL_DIR) $(1)/usr/share/dbus-1/system-services
	$(CP) $(PKG_INSTALL_DIR)/usr/share/dbus-1/system-services/*.service $(1)/usr/share/dbus-1/system-services

	$(INSTALL_DIR) $(1)/usr/share/doc
	$(CP) -R $(PKG_INSTALL_DIR)/usr/share/doc/* $(1)/usr/share/doc

	$(INSTALL_DIR) $(1)/usr/share/locale
	$(CP) -R $(PKG_INSTALL_DIR)/usr/share/locale/* $(1)/usr/share/locale

	$(INSTALL_DIR) $(1)/usr/lib/rules.d
	$(CP) $(PKG_INSTALL_DIR)/$(STAGING_DIR)/usr/lib/rules.d/*.rules $(1)/usr/lib/rules.d

	$(INSTALL_DATA) -m 0755 -D ./files/S45network-manager $(1)/etc/init.d/S45network-manager
endef

define Package/networkmanager-nmtui/install
	$(INSTALL_DIR) $(1)/usr/bin/
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/bin/nmtui $(1)/usr/bin/nmtui
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/bin/nmtui-connect $(1)/usr/bin/nmtui-connect
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/bin/nmtui-edit $(1)/usr/bin/nmtui-edit
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/bin/nmtui-hostname $(1)/usr/bin/nmtui-hostname
endef

define Package/networkmanager-modemmanager/install
	$(INSTALL_DIR) $(1)/usr/lib/NetworkManager/$(PKG_VERSION)/
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/NetworkManager/$(PKG_VERSION)/libnm-device-plugin-bluetooth.so \
		$(1)/usr/lib/NetworkManager/$(PKG_VERSION)
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/NetworkManager/$(PKG_VERSION)/libnm-device-plugin-wwan.so \
		$(1)/usr/lib/NetworkManager/$(PKG_VERSION)
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/NetworkManager/$(PKG_VERSION)/libnm-wwan.so \
		$(1)/usr/lib/NetworkManager/$(PKG_VERSION)
endef

define Package/networkmanager-pppd/install
	$(INSTALL_DIR) $(1)/usr/lib/NetworkManager/$(PKG_VERSION)/
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/NetworkManager/$(PKG_VERSION)/libnm-ppp-plugin.so \
		$(1)/usr/lib/NetworkManager/$(PKG_VERSION)
		
	$(INSTALL_DIR) $(1)/usr/lib/pppd/
	$(CP) -R $(PKG_INSTALL_DIR)/usr/lib/pppd/* $(1)/usr/lib/pppd
endef

define Package/networkmanager-openvswitch/install
	$(INSTALL_DIR) $(1)/usr/lib/NetworkManager/$(PKG_VERSION)/
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/NetworkManager/$(PKG_VERSION)/libnm-device-plugin-ovs.so \
		$(1)/usr/lib/NetworkManager/$(PKG_VERSION)
endef

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/lib/
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libnm.so* $(1)/usr/lib

	$(INSTALL_DIR) $(1)/usr/include/libnm/
	$(CP) $(PKG_INSTALL_DIR)/usr/include/libnm/*.h $(1)/usr/include/libnm

	$(INSTALL_DIR) $(1)/usr/lib/pkgconfig/
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/pkgconfig/*.pc $(1)/usr/lib/pkgconfig
endef

$(eval $(call BuildPackage,networkmanager))
$(eval $(call BuildPackage,networkmanager-nmtui))
$(eval $(call BuildPackage,networkmanager-modemmanager))
$(eval $(call BuildPackage,networkmanager-pppd))
$(eval $(call BuildPackage,networkmanager-openvswitch))
