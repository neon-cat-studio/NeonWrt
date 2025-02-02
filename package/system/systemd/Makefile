include $(TOPDIR)/rules.mk

PKG_NAME:=systemd
PKG_VERSION:=256.7
PKG_RELEASE:=1

PKG_SOURCE:=$(PKG_NAME)-v$(PKG_VERSION).tar.gz
PKG_SOURCE_URL:=https://github.com/systemd/systemd/archive/v$(PKG_VERSION)
PKG_HASH:=skip

PKG_LICENSE:=LGPL-2.1+ GPL-2.0+
PKG_LICENSE_FILES:=LICENSE.GPL2 LICENSE.LGPL2.1

PKG_BUILD_DEPENDS:=intltool/host gperf/host python-jinja2/host python-pyelftools/host python-pefile/host
PKG_BUILD_PARALLEL:=1
PKG_INSTALL:=1

include systemd-common.mk
include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/meson.mk

TARGET_CFLAGS += --std=gnu99

SYSTEMD_DISABLE_PKG = $(if $(CONFIG_PACKAGE_systemd-$(1)),,--disable-$(2))

CONFIGURE_ARGS_FAST_BUILD = \
	--enable-gtk-doc \
	--enable-gtk-doc-html \
	--enable-manpages

CONFIGURE_ARGS_EMBEDDED = \
	--enable-backlight \
	--disable-binfmt \
	--enable-firstboot \
	--disable-hibernate \
	--enable-ldconfig \
	--disable-microhttpd \
	--enable-nls \
	--enable-qrencode \
	--enable-quotacheck \
	--enable-vconsole \
	--disable-xkbcommon

CONFIGURE_ARGS += \
	--prefix=/usr \
	--sysconfdir=/etc \
	-Dc_link_args="-Wl,--disable-new-dtags -Wl,-rpath=/usr/lib" \
	--enable-dbus \
	--enable-shutdown \
	--enable-pam \
	--enable-logind \
	--enable-seccomp \
	$(CONFIGURE_ARGS_FAST_BUILD) \
	$(CONFIGURE_ARGS_EMBEDDED) \
	--enable-apparmor \
	--enable-introspection \
	--enable-gudev \
	--enable-chkconfig \
	--enable-ima \
	--enable-selinux \
	--enable-audit \
	--enable-smack \
	--enable-xz \
	--enable-acl \
	--enable-gcrypt \
	--enable-myhostname \
	--enable-libcryptsetup \
	--enable-polkit \
	--enable-elfutils \
	--enable-gnutls \
	--enable-libcurl \
	--enable-switch-root \
	--enable-sulogin \
#	$(call SYSTEMD_DISABLE_PKG,bootchart,bootchart) \
	$(call SYSTEMD_DISABLE_PKG,coredump,coredump) \
	$(call SYSTEMD_DISABLE_PKG,hostnamed,hostnamed) \
	$(call SYSTEMD_DISABLE_PKG,localed,localed) \
	$(call SYSTEMD_DISABLE_PKG,modules-load,kmod) \
	$(call SYSTEMD_DISABLE_PKG,networkd,networkd) \
	$(call SYSTEMD_DISABLE_PKG,random-seed,randomseed) \
	$(call SYSTEMD_DISABLE_PKG,resolved,resolved) \
	$(call SYSTEMD_DISABLE_PKG,rfkill,rfkill) \
	$(call SYSTEMD_DISABLE_PKG,timedated,timedated) \
	$(call SYSTEMD_DISABLE_PKG,timesyncd,timesyncd) \
	$(call SYSTEMD_DISABLE_PKG,tmpfiles,tmpfiles) \
	$(call SYSTEMD_DISABLE_PKG,update-utmp,utmp)

MESON_ARGS += \
	-Dlibdir=/usr/lib \
	-Dutmp=true \
	-Dlogind=true \
	-Dpam=enabled \
	-Dseccomp=enabled \
	-Dstatic-libsystemd=false \
	-Dlink-executor-shared=true \
	-Ddefault-dnssec=allow-downgrade \
	-Ddefault-user-shell=/bin/sh \
	-Dinstall-tests=false

define Package/systemd
  SECTION:=base
  CATEGORY:=Base system
  TITLE:=Systemd init system
  DEPENDS:=+libc +libcap +libselinux +libkmod +libgcrypt +libseccomp +libpam +libarchive +libacl +liblz4\
	+libxkbcommon +libapparmor +libfido2 +libbpf +libmicrohttpd +libcurl +libidn +libidn2 +liblzma +libzstd +libxkbcommon\
  	+valgrind +audit +p11-kit +bzip2 +block-mount +fstools +mount-utils +fdisk +lsblk +blkid +logger +agetty +cryptsetup +gnutls-utils +openssl-util
endef
#+kexec +dbus +p11-kit
define Package/systemd/description
  systemd is a modern init system and system manager for Linux.
  (Only Support for GLIBC, Musl not Support!)
endef

define Package/systemd/conffiles
/etc/hostname
/etc/machine-id
/etc/systemd/system.conf
/etc/systemd/user.conf
endef

define Package/systemd-executor
$(call Package/systemd/Default)
	TITLE:=systemd executor component
	DEPENDS+= systemd +libapparmor +libpam +libselinux +libseccomp
endef

define Package/systemd-tmpfiles
$(call Package/systemd/Default)
	TITLE:=systemd tmpfiles component
	DEPENDS+= systemd +libacl
endef

define Package/systemd/install
	$(INSTALL_DIR) $(1)/etc/systemd
	$(CP) \
		$(PKG_INSTALL_DIR)/etc/systemd/{journald,system,user}.conf \
		$(1)/etc/systemd
	$(INSTALL_DIR) $(1)/etc/systemd
	echo "LogLevel=debug" > $(1)/etc/systemd/system.conf
	echo "ForwardToConsole=yes" >> $(1)/etc/systemd/journald.conf

	$(INSTALL_DIR) $(1)/etc/systemd/system/multi-user.target.wants
	ln -sf \
		/usr/lib/systemd/system/remote-fs.target \
		$(1)/etc/systemd/system/multi-user.target.wants/.

	$(INSTALL_DIR) $(1)/etc/systemd/network
	$(INSTALL_DIR) $(1)/etc/systemd/user
	$(INSTALL_DIR) $(1)/etc/network

	# 確保 dbus-1 目錄存在
	$(INSTALL_DIR) $(1)/etc/dbus-1/system.d
	# 複製 org.freedesktop.systemd1.conf 到 dbus-1/system.d
	$(INSTALL_DATA) \
		$(PKG_BUILD_DIR)/src/core/org.freedesktop.systemd1.conf \
		$(1)/etc/dbus-1/system.d/org.freedesktop.systemd1.conf
		
	$(INSTALL_DIR) $(1)/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libsystemd.so* $(1)/lib

	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) \
		$(addprefix $(PKG_INSTALL_DIR)/usr/bin/, \
			$(SYSTEMD_BIN)) \
		$(1)/usr/bin

	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libsystemd.so* $(1)/usr/lib
	ln -sf libsystemd.so.0 $(1)/usr/lib/libsystemd.so
	$(INSTALL_BIN) \
		$(PKG_INSTALL_DIR)/usr/lib/systemd/libsystemd-core-*.so $(1)/usr/lib/
	ln -s libsystemd-core-256.so $(1)/usr/lib/libsystemd-core.so
	$(INSTALL_BIN) \
		$(PKG_INSTALL_DIR)/usr/lib/systemd/libsystemd-shared-*.so $(1)/usr/lib/
	ln -s libsystemd-shared-256.so $(1)/usr/lib/libsystemd-shared.so

	$(INSTALL_DIR) $(1)/etc/sysctl.d
	$(INSTALL_DIR) $(1)/usr/lib/sysctl.d
	$(INSTALL_DATA) \
		$(PKG_INSTALL_DIR)/usr/lib/sysctl.d/50-default.conf \
		$(1)/usr/lib/sysctl.d

	$(INSTALL_DIR) $(1)/usr/lib/sysusers.d
	$(INSTALL_DATA) \
		$(PKG_INSTALL_DIR)/usr/lib/sysusers.d/*.conf \
		$(1)/usr/lib/sysusers.d

	$(INSTALL_DIR) $(1)/usr/lib/systemd
	$(INSTALL_BIN) \
		$(addprefix $(PKG_INSTALL_DIR)/usr/lib/systemd/, \
			$(SYSTEMD_LIB)) \
		$(1)/usr/lib/systemd

	$(INSTALL_DIR) $(1)/usr/lib/systemd/system
	$(CP) \
		$(addprefix $(PKG_INSTALL_DIR)/usr/lib/systemd/system/, \
			$(SYSTEMD_SYSTEM_TARGET_WANTS) \
			$(SYSTEMD_SYSTEM_TARGETS) \
			$(SYSTEMD_SYSTEM_SLICES) \
			$(SYSTEMD_SYSTEM_SOCKETS) \
			$(SYSTEMD_SYSTEM_PATHS) \
			$(SYSTEMD_SYSTEM_SERVICES) \
			$(SYSTEMD_SYSTEM_MOUNTS)) \
		$(1)/usr/lib/systemd/system

	$(INSTALL_DIR) $(1)/usr/lib/systemd/system-shutdown
	$(INSTALL_DIR) $(1)/usr/lib/systemd/system-sleep
	$(INSTALL_DIR) $(1)/usr/lib/systemd/system-generators
	$(INSTALL_DIR) $(1)/usr/lib/systemd/user-generators

	$(INSTALL_BIN) \
		$(PKG_INSTALL_DIR)/usr/lib/systemd/system-generators/systemd-* \
		$(1)/usr/lib/systemd/system-generators

	$(INSTALL_DIR) $(1)/usr/lib/systemd/catalog
	$(CP) \
		$(PKG_INSTALL_DIR)/usr/lib/systemd/catalog/systemd.catalog \
		$(1)/usr/lib/systemd/catalog

	$(INSTALL_DIR) $(1)/usr/lib/systemd/user
	$(CP) \
		$(PKG_INSTALL_DIR)/usr/lib/systemd/user/* \
		$(1)/usr/lib/systemd/user

	$(INSTALL_DIR) $(1)/usr/share/dbus-1/services
	$(INSTALL_DIR) $(1)/usr/share/dbus-1/system-services
	$(CP) \
		$(PKG_INSTALL_DIR)/usr/share/dbus-1/system-services/org.freedesktop.systemd1.service \
		$(1)/usr/share/dbus-1/system-services
	ln -sf \
		/usr/share/dbus-1/system-services/org.freedesktop.systemd1.service \
		$(1)/usr/share/dbus-1/services/.

	$(INSTALL_DIR) $(1)/var/log/journal
	$(INSTALL_DIR) $(1)/etc/systemd/system/getty.target.wants
	$(INSTALL_DATA) \
		./files/etc/systemd/system/getty.target.wants/getty@tty1.service \
		$(1)/etc/systemd/system/getty.target.wants/

	$(INSTALL_DIR) $(1)/sbin
	ln -sf \
		/usr/lib/systemd/systemd \
		$(1)/sbin/init

	$(CP) ./files/* $(1)/
	
	$(INSTALL_DIR) $(1)/etc
	$(INSTALL_DATA) ./files/etc/os-release $(1)/etc/os-release
	$(INSTALL_DATA) ./files/etc/machine-id $(1)/etc/machine-id
	$(INSTALL_DATA) ./files/etc/hostname $(1)/etc/hostname

	$(INSTALL_DIR) $(1)/run
	ln -sf /run $(1)/var/run

	$(INSTALL_DIR) $(1)/sys/fs/cgroup

	# FIXME: make DEFAULT_TARGET option
	ln -sf \
		/usr/lib/systemd/system/initrd.target \
		$(1)/etc/systemd/system/default.target

	# FIXME: ifeq ($(DEFAULT_TARGET),initrd)
	touch $(1)/etc/initrd-release
	$(INSTALL_DIR) $(1)/sysroot

	# 安裝自定義 init 腳本
	$(INSTALL_BIN) ./files/init $(1)/init

	# 確保 overlay 目錄存在
	$(INSTALL_DIR) $(1)/overlay
	mkdir -p $(1)/overlay/upper $(1)/overlay/work
	mkdir -p $(1)/overlay/etc_upper $(1)/overlay/etc_work

	# 安裝 systemd mount 單元文件
	$(INSTALL_DIR) $(1)/usr/lib/systemd/system
	$(INSTALL_DATA) ./files/etc/systemd/system/overlay.mount $(1)/usr/lib/systemd/system/overlay.mount
	$(INSTALL_DATA) ./files/etc/systemd/system/sysroot.mount $(1)/usr/lib/systemd/system/sysroot.mount

	# 建立 symlink，確保 overlay.mount 和 sysroot.mount 啟動
	$(INSTALL_DIR) $(1)/etc/systemd/system/initrd-root-fs.target.wants
	ln -sf /usr/lib/systemd/system/overlay.mount \
		$(1)/etc/systemd/system/initrd-root-fs.target.wants/overlay.mount
	ln -sf /usr/lib/systemd/system/sysroot.mount \
		$(1)/etc/systemd/system/initrd-root-fs.target.wants/sysroot.mount

	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/lib/systemd/systemd-executor $(1)/usr/lib/systemd
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/bin/systemd-tmpfiles $(1)/usr/bin
endef

define Package/systemd-executor/install
	$(INSTALL_DIR) $(1)/usr/lib/systemd
	$(INSTALL_BIN) \
		$(PKG_INSTALL_DIR)/usr/lib/systemd/systemd-executor \
		$(1)/usr/lib/systemd
endef

define Package/systemd-tmpfiles/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) \
		$(PKG_INSTALL_DIR)/usr/bin/systemd-tmpfiles \
		$(1)/usr/bin
endef

define Package/systemd-coredump
$(call Package/systemd/Default)
	TITLE:=systemd coredump support
	DEPENDS+= systemd +@KERNEL_ELF_CORE
endef

define Package/systemd-coredump/description
$(call Package/systemd/description/Default)
This package contains the systemd coredump support.
endef

define Package/systemd-coredump/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) \
		$(PKG_INSTALL_DIR)/usr/bin/coredumpctl \
		$(1)/usr/bin

	$(INSTALL_DIR) $(1)/usr/lib/systemd
	$(INSTALL_BIN) \
		$(PKG_INSTALL_DIR)/usr/lib/systemd/systemd-coredump \
		$(1)/usr/lib/systemd

	$(INSTALL_DIR) $(1)/etc/systemd
	$(INSTALL_DATA) \
		$(PKG_INSTALL_DIR)/etc/systemd/coredump.conf \
		$(1)/etc/systemd

	$(INSTALL_DIR) $(1)/usr/lib/sysctl.d
	$(INSTALL_DATA) \
		$(PKG_INSTALL_DIR)/usr/lib/sysctl.d/50-coredump.conf \
		$(1)/usr/lib/sysctl.d
endef


define Package/systemd-nspawn
$(call Package/systemd/Default)
	TITLE:=systemd namespace container support
	DEPENDS+= systemd +iptables
endef

define Package/systemd-nspawn/description
$(call Package/systemd/description/Default)
This package contains the systemd namespace container support.
endef

define Package/systemd-nspawn/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) \
		$(PKG_INSTALL_DIR)/usr/bin/systemd-nspawn \
		$(1)/usr/bin

	$(INSTALL_DIR) $(1)/usr/lib/systemd/system
	$(INSTALL_DATA) \
		$(PKG_INSTALL_DIR)/usr/lib/systemd/system/systemd-nspawn@.service \
		$(1)/usr/lib/systemd/system
endef


define Package/systemd-tmpfiles
$(call Package/systemd/Default)
	TITLE:=systemd temporary file management support
	DEPENDS+= systemd
endef

define Package/systemd-tmpfiles/description
$(call Package/systemd/description/Default)
This package contains the systemd temporary file management support.
endef

define Package/systemd-tmpfiles/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) \
		$(PKG_INSTALL_DIR)/usr/bin/systemd-tmpfiles \
		$(1)/usr/bin

	$(INSTALL_DIR) $(1)/usr/lib/systemd/system
	$(INSTALL_DATA) \
		$(wildcard $(PKG_INSTALL_DIR)/usr/lib/systemd/system/systemd-tmpfiles-*) \
		$(1)/usr/lib/systemd/system

	$(INSTALL_DIR) $(1)/usr/lib/systemd/system/sysinit.target.wants
	$(CP) \
		$(addprefix $(PKG_INSTALL_DIR)/usr/lib/systemd/system/sysinit.target.wants/,
			systemd-tmpfiles-setup.service \
			systemd-tmpfiles-setup-dev.service ) \
		$(1)/usr/lib/systemd/system/sysinit.target.wants

	$(INSTALL_DIR) $(1)/usr/lib/systemd/system/timers.target.wants
	$(CP) \
		$(PKG_INSTALL_DIR)/usr/lib/systemd/system/timers.target.wants/systemd-tmpfiles-clean.timer \
		$(1)/usr/lib/systemd/system/timers.target.wants

	$(INSTALL_DIR) $(1)/etc/tmpfiles.d	
	$(INSTALL_DIR) $(1)/usr/lib/tmpfiles.d
	$(CP) \
		$(PKG_INSTALL_DIR)/usr/lib/tmpfiles.d/*.conf \
		$(1)/usr/lib/tmpfiles.d
endef


define Package/systemd-udev-hwdb
$(call Package/systemd/Default)
  TITLE+= (udev hwdb)
  DEPENDS:=+systemd-udevd
endef

define Package/systemd-udev-hwdb/description
$(call Package/systemd/description/Default)
  This package contains the udev hardware database files.
endef

define Package/systemd-udev-hwdb/install
	$(INSTALL_DIR) $(1)/etc/udev/hwdb.d
	$(INSTALL_DIR) $(1)/usr/lib/udev/hwdb.d
	$(CP) \
		$(PKG_INSTALL_DIR)/usr/lib/udev/hwdb.d/*.hwdb \
		$(1)/usr/lib/udev/hwdb.d
endef


define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libudev.so* $(1)/usr/lib
#	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libgudev-1.0.so* $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libsystemd.so* $(1)/usr/lib

	$(INSTALL_DIR) $(1)/usr/include
	$(CP) $(PKG_INSTALL_DIR)/usr/include/* $(1)/usr/include

	$(INSTALL_DIR) $(1)/usr/share/pkgconfig
	$(CP) $(PKG_INSTALL_DIR)/usr/share/pkgconfig/*.pc $(1)/usr/share/pkgconfig
	$(INSTALL_DIR) $(1)/usr/lib/pkgconfig
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/pkgconfig/*.pc $(1)/usr/lib/pkgconfig
endef


define SystemdBuildLib
  define Package/systemd-$(1)
	$(call Package/systemd/Default)
	TITLE:=systemd $(2)
	DEPENDS+= systemd $(3)
  endef

  define Package/systemd-$(1)/description
  $(call Package/systemd/description/Default)
  This package contains the systemd $(2).
  endef

  define Package/systemd-$(1)/install
	# daemon
	$(INSTALL_DIR) $$(1)/usr/lib/systemd
	$(INSTALL_BIN) \
		$(PKG_INSTALL_DIR)/usr/lib/systemd/systemd-$(1)* \
		$$(1)/usr/lib/systemd
	# service (systemd)
	$(INSTALL_DIR) $$(1)/usr/lib/systemd/system
	$(INSTALL_DATA) \
		$(PKG_INSTALL_DIR)/usr/lib/systemd/system/systemd-$(1)*.service \
		$$(1)/usr/lib/systemd/system
	# custom
	$(call Plugin/$(1)/install,$$(1))
  endef

  $$(eval $$(call BuildPackage,systemd-$(1)))
endef

define SystemdDbusService
	$(INSTALL_DIR) $(1)/usr/lib/systemd/system
	$(CP) \
		$(PKG_INSTALL_DIR)/usr/lib/systemd/system/dbus-org.freedesktop.$(2).service \
		$(1)/usr/lib/systemd/system

	$(INSTALL_DIR) $(1)/etc/dbus-1/system.d
	$(INSTALL_DATA) \
		$(PKG_INSTALL_DIR)/etc/dbus-1/system.d/org.freedesktop.$(2).conf \
		$(1)/etc/dbus-1/system.d

	$(INSTALL_DIR) $(1)/usr/share/dbus-1/system-services
	$(INSTALL_DATA) \
		$(PKG_INSTALL_DIR)/usr/share/dbus-1/system-services/org.freedesktop.$(2).service \
		$(1)/usr/share/dbus-1/system-services
endef


define Plugin/bootchart/install
	$(INSTALL_DIR) $(1)/etc/systemd
	$(INSTALL_DATA) \
		$(PKG_INSTALL_DIR)/etc/systemd/bootchart.conf \
		$(1)/etc/systemd
endef


define Plugin/hostnamed/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) \
		$(PKG_INSTALL_DIR)/usr/bin/hostnamectl \
		$(1)/usr/bin

	$(call SystemdDbusService,$$(1),hostname1)
endef


define Plugin/localed/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) \
		$(PKG_INSTALL_DIR)/usr/bin/localectl \
		$(1)/usr/bin

	$(call SystemdDbusService,$$(1),locale1)
endef


define Plugin/modules-load/install
	$(INSTALL_DIR) $(1)/etc/modules-load.d
	$(INSTALL_DIR) $(1)/usr/lib/modules-load.d

	$(INSTALL_DIR) $(1)/usr/lib/systemd/system/sysinit.target.wants
	$(CP) \
		$(PKG_INSTALL_DIR)/usr/lib/systemd/system/sysinit.target.wants/systemd-modules-load.service \
		$(1)/usr/lib/systemd/system/sysinit.target.wants
endef


define Plugin/networkd/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) \
		$(PKG_INSTALL_DIR)/usr/bin/networkctl \
		$(1)/usr/bin

	$(INSTALL_DIR) $(1)/usr/lib/systemd/system
	$(INSTALL_DATA) \
		$(addprefix $(PKG_INSTALL_DIR)/usr/lib/systemd/system/, \
			network.target \
			network-pre.target \
			network-online.target \
			systemd-networkd.socket ) \
		$(1)/usr/lib/systemd/system

	$(INSTALL_DIR) $(1)/usr/lib/systemd/network
	$(INSTALL_DATA) \
		$(addprefix $(PKG_INSTALL_DIR)/usr/lib/systemd/network/, \
			80-container-host0.network \
			80-container-ve.network \
			99-default.link ) \
		$(1)/usr/lib/systemd/network

	$(INSTALL_DIR) $(1)/etc/systemd/system/multi-user.target.wants
	$(CP) \
		$(PKG_INSTALL_DIR)/etc/systemd/system/multi-user.target.wants/systemd-networkd.service \
		$(1)/etc/systemd/system/multi-user.target.wants

	$(INSTALL_DIR) $(1)/etc/systemd/system/network-online.target.wants
	$(CP) \
		$(PKG_INSTALL_DIR)/etc/systemd/system/network-online.target.wants/systemd-networkd-wait-online.service \
		$(1)/etc/systemd/system/network-online.target.wants

	$(INSTALL_DIR) $(1)/etc/systemd/system/sockets.target.wants
	$(CP) \
		$(PKG_INSTALL_DIR)/etc/systemd/system/sockets.target.wants/systemd-networkd.socket \
		$(1)/etc/systemd/system/sockets.target.wants

	$(call SystemdDbusService,$$(1),network1)
endef


define Plugin/random-seed/install
	$(INSTALL_DIR) $(1)/usr/lib/systemd/system/sysinit.target.wants
	$(CP) \
		$(PKG_INSTALL_DIR)/usr/lib/systemd/system/sysinit.target.wants/systemd-random-seed.service \
		$(1)/usr/lib/systemd/system/sysinit.target.wants
endef


define Plugin/resolved/install
	$(INSTALL_DIR) $(1)/etc/systemd
	$(INSTALL_DATA) \
		$(PKG_INSTALL_DIR)/etc/systemd/resolved.conf \
		$(1)/etc/systemd

	$(INSTALL_DIR) $(1)/etc/systemd/system/multi-user.target.wants
	$(CP) \
		$(PKG_INSTALL_DIR)/etc/systemd/system/multi-user.target.wants/systemd-resolved.service \
		$(1)/etc/systemd/system/multi-user.target.wants

	$(INSTALL_DIR) $(1)/lib
	$(INSTALL_BIN) \
		$(PKG_INSTALL_DIR)/usr/lib/libnss_resolve.so* \
		$(1)/lib

	$(INSTALL_DIR) $(1)/usr/lib/systemd
	$(INSTALL_BIN) \
		$(PKG_INSTALL_DIR)/usr/lib/systemd/systemd-resolve-host \
		$(1)/usr/lib/systemd

	$(call SystemdDbusService,$$(1),resolve1)
endef

define Package/systemd-resolved/conffiles
/etc/systemd/resolved.conf
endef


define Plugin/timedated/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) \
		$(PKG_INSTALL_DIR)/usr/bin/timedatectl \
		$(1)/usr/bin

	$(call SystemdDbusService,$$(1),timedate1)
endef


define Plugin/timesyncd/install
	$(INSTALL_DIR) $(1)/etc/systemd
	$(INSTALL_DATA) \
		$(PKG_INSTALL_DIR)/etc/systemd/timesyncd.conf \
		$(1)/etc/systemd

	$(INSTALL_DIR) $(1)/etc/systemd/system/sysinit.target.wants
	$(CP) \
		$(PKG_INSTALL_DIR)/etc/systemd/system/sysinit.target.wants/systemd-timesyncd.service \
		$(1)/etc/systemd/system/sysinit.target.wants
endef

define Package/systemd-timesyncd/conffiles
/etc/systemd/timesyncd.conf
endef


define Plugin/udevd/install
	$(INSTALL_DIR) $(1)/etc/udev/rules.d
	$(INSTALL_DATA) \
		$(PKG_INSTALL_DIR)/etc/udev/udev.conf \
		$(1)/etc/udev

	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) \
		$(PKG_INSTALL_DIR)/usr/bin/udevadm \
		$(1)/usr/bin

	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) \
		$(PKG_INSTALL_DIR)/usr/bin/systemd-hwdb \
		$(1)/usr/bin

	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) \
		$(PKG_INSTALL_DIR)/usr/lib/libudev.so* \
		$(1)/usr/lib

	$(INSTALL_DIR) $(1)/usr/lib/systemd/system
	$(INSTALL_DATA) \
		$(addprefix $(PKG_INSTALL_DIR)/usr/lib/systemd/system/, \
			$(SYSTEMD_UDEVD_SYSTEM_SERVICES) \
			$(SYSTEMD_UDEVD_SYSTEM_SOCKETS)) \
		$(1)/usr/lib/systemd/system

	$(INSTALL_DIR) $(1)/usr/lib/udev
	$(INSTALL_BIN) \
		$(addprefix $(PKG_INSTALL_DIR)/usr/lib/udev/, \
			$(SYSTEMD_UDEVD_LIBS)) \
		$(1)/usr/lib/udev

	$(INSTALL_DIR) $(1)/usr/lib/udev/rules.d
	$(CP) \
		$(PKG_INSTALL_DIR)/usr/lib/udev/rules.d/* \
		$(1)/usr/lib/udev/rules.d

	$(INSTALL_DIR) $(1)/usr/lib/systemd/system/sysinit.target.wants
	$(CP) \
		$(addprefix $(PKG_INSTALL_DIR)/usr/lib/systemd/system/sysinit.target.wants/, \
			systemd-udevd.service \
			systemd-udev-trigger.service ) \
		$(1)/usr/lib/systemd/system/sysinit.target.wants

	$(INSTALL_DIR) $(1)/usr/lib/systemd/system/sockets.target.wants
	$(CP) \
		$(addprefix $(PKG_INSTALL_DIR)/usr/lib/systemd/system/sockets.target.wants/, \
			systemd-udevd-control.socket \
			systemd-udevd-kernel.socket ) \
		$(1)/usr/lib/systemd/system/sockets.target.wants
endef

define Package/systemd-udevd/conffiles
/etc/udev/udev.conf
endef


define Plugin/update-utmp/install
	$(INSTALL_DIR) $(1)/usr/lib/systemd/system/sysinit.target.wants
	$(CP) \
		$(PKG_INSTALL_DIR)/usr/lib/systemd/system/sysinit.target.wants/systemd-update-utmp.service \
		$(1)/usr/lib/systemd/system/sysinit.target.wants

# FIXME: /usr/lib/systemd/system/runlevel$(seq 1 5).target.wants/systemd-update-utmp-runlevel.service
# directories and symlinks
#	$(INSTALL_DIR) \
#		$(foreach D, $(shell seq 1 5), $(1)/usr/lib/systemd/system/runlevel$(D).target.wants)
endef

$(eval $(call BuildPackage,systemd))
$(eval $(call BuildPackage,systemd-coredump))
$(eval $(call BuildPackage,systemd-nspawn))
#$(eval $(call BuildPackage,systemd-tmpfiles))
$(eval $(call BuildPackage,systemd-udev-hwdb))

$(eval $(call SystemdBuildLib,bootchart,bootchart tool,))
$(eval $(call SystemdBuildLib,hostnamed,hostname daemon,))
$(eval $(call SystemdBuildLib,localed,locale daemon,))
$(eval $(call SystemdBuildLib,modules-load,module loader,+libkmod))
$(eval $(call SystemdBuildLib,networkd,network daemon,+iptables))
$(eval $(call SystemdBuildLib,random-seed,randomseed tools,))
$(eval $(call SystemdBuildLib,resolved,name resolver,+@EGLIBC_OPTION_EGLIBC_NSSWITCH))
$(eval $(call SystemdBuildLib,rfkill,rfkill tools,+@USE_RFKILL))
$(eval $(call SystemdBuildLib,timedated,timedate daemon,))
$(eval $(call SystemdBuildLib,timesyncd,network time synchronization,))
$(eval $(call SystemdBuildLib,udevd,device manager,))
$(eval $(call SystemdBuildLib,update-utmp,utmp/wtmp log handling,))