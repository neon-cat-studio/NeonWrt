include $(TOPDIR)/rules.mk

PKG_NAME:=mongodb
PKG_RELEASE:=1

ifeq ($(CONFIG_MONGODB_V_3_0),y)
PKG_VERSION:=r3.0.11
PKG_HASH:=8b25bae2636960650246ea60f270f276b2ff8fc80f1776be252eb6ab20d74d15
PATCH_DIR:=./patches/v3.0
endif
ifeq ($(CONFIG_MONGODB_V_4_0),y)
PKG_VERSION:=r4.0.18
PKG_HASH:=c2b1ba40b2f132cce5fd0cdee26b5176aceeac2922b238874241d33f9920b50f
PATCH_DIR:=./patches/v4.0
endif
ifeq ($(CONFIG_MONGODB_V_4_4),y)
PKG_VERSION:=r4.4.0
PKG_HASH:=c948b8b6f1c4da4cac1c49a8f1367b88b5b036d9095cd205e875c53f09b41611
PATCH_DIR:=./patches/v4.4
endif

PKG_SOURCE_URL:=http://downloads.mongodb.org/src/
PKG_SOURCE:=$(PKG_NAME)-src-$(PKG_VERSION).tar.gz
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-src-$(PKG_VERSION)

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/scons.mk

define Package/mongodb
  SECTION:=base
  CATEGORY:=MongoDB
  TITLE:=MongoDB
  URL:=https://www.mongodb.com/
  DEPENDS:=+libc +libcurl +libpthread +librt +libstdcpp +zlib +zstd +gperftools-runtime\
	+libpcre +libpcrecpp +boost +boost-filesystem +boost-program_options +boost-log\
	+boost-iostreams +boost-thread +libyaml-cpp +libstemmer +libbenchmark +libsnappy\
	+sqlite3-cli +libopenssl +icu +icu-full-data
endef

define Package/mongodb/config
	menu "Configuration"
		depends on PACKAGE_mongodb

	choice
		prompt "Version Selection"
		default MONGODB_V_3_0
		help
		 Select MongoDB version.

		config MONGODB_V_3_0
			bool "MongoDB V3.0.11 With V8 JS Engine"

		config MONGODB_V_4_0
			bool "MongoDB V4.0.18 With MozillaJS-45 JS Engine"

		config MONGODB_V_4_4
			bool "MongoDB V4.4.0 With MozillaJS-60 JS Engine"
	endchoice

	endmenu
endef

TARGET_CFGS += \
	TARGET_OS=linux \
	TARGET_ARCH=$(ARCH)


USE_HW_CRC32:=y
ifneq ($(ARCH),aarch64)
ifneq ($(ARCH),x86_64)
ifneq ($(ARCH),x86)
ifneq ($(ARCH),power8)
USE_HW_CRC32:=n
endif
endif
endif
endif


ifeq ($(CONFIG_MONGODB_V_3_0),y)
BUILD_ARGS += \
	--ssl \
	--wiredtiger=off \
	--js-engine=v8-3.25 \
	--build-dir=$(PKG_BUILD_DIR)/build \
	--variant-dir=opt \
	--distarch="$(ARCH)" \
	--cc="$(TOOLCHAIN_DIR)/bin/$(TARGET_CROSS)gcc" \
	--cxx="$(TOOLCHAIN_DIR)/bin/$(TARGET_CROSS)g++" \
	--cpppath="$(STAGING_DIR)/usr/include" \
	--libpath="$(STAGING_DIR)/usr/lib" \
	--staging-dir="$(STAGING_DIR)" \
	--disable-warnings-as-errors \

BUILD_CXXFLAGS:= -std=gnu++11
endif

ifeq ($(CONFIG_MONGODB_V_4_0),y)
BUILD_ARGS += \
	--wiredtiger=on \
	--js-engine=mozjs \
	--ssl \
	--ssl-provider=openssl \
	--disable-warnings-as-errors
	
BUILD_CCFLAGS:=
ifeq ($(USE_HW_CRC32),y)
BUILD_ARGS += --use-s390x-crc32=on
ifeq ($(ARCH),aarch64)
BUILD_CCFLAGS += -march=armv8-a+crc -mtune=generic
endif
endif
ifeq ($(USE_HW_CRC32),n)
BUILD_ARGS += --use-s390x-crc32=off
endif

endif

ifeq ($(CONFIG_MONGODB_V_4_4),y)
BUILD_ARGS += \
	--wiredtiger=on \
	--js-engine=mozjs \
	--ssl \
	--disable-warnings-as-errors

BUILD_CCFLAGS:=
ifeq ($(USE_HW_CRC32),y)
BUILD_ARGS += --use-hardware-crc32=on
ifeq ($(ARCH),aarch64)
BUILD_CCFLAGS += -march=armv8-a+crc -mtune=generic
endif
endif
ifeq ($(USE_HW_CRC32),n)
BUILD_ARGS += --use-hardware-crc32=off
endif

endif

TOOLCHAIN_PREFIX:=$(TOOLCHAIN_DIR)/bin/$(TARGET_CROSS)

ifeq ($(CONFIG_MONGODB_V_3_0),y)
define Build/Configure
(\
	sh ./scripts/v3.0/replace_files.sh $(PKG_BUILD_DIR); \
	cd $(PKG_BUILD_DIR); \
	$(SCONS_VARS) scons core -j4 $(BUILD_ARGS)\
		$(SCONS_OPTIONS); \
		CXXFLAGS="$(BUILD_CXXFLAGS)"; \
	cd $(PKG_BUILD_DIR)/build/opt/mongo; \
	$(TOOLCHAIN_PREFIX)strip -s mongo; \
	$(TOOLCHAIN_PREFIX)strip -s mongod; \
	$(TOOLCHAIN_PREFIX)strip -s mongos; \
)
endef
endif

ifeq ($(CONFIG_MONGODB_V_4_0),y)
define Build/Configure
(\
	sh ./scripts/v4.0/replace_files.sh $(PKG_BUILD_DIR); \
	cd $(PKG_BUILD_DIR); \
	pip install -r buildscripts/requirements.txt; \
	cd $(PKG_BUILD_DIR)/src/third_party/wiredtiger; \
	sh autogen.sh; \
	cd $(PKG_BUILD_DIR)/src/third_party/mozjs-45; \
	sh get-sources.sh; \
	sh gen-config.sh $(ARCH); \
	cd $(PKG_BUILD_DIR); \
	$(SCONS_VARS) scons core -j4 \
		$(TARGET_CFGS) $(BUILD_ARGS)\
		AR="$(TOOLCHAIN_PREFIX)ar" \
		CC="$(TOOLCHAIN_PREFIX)gcc" \
		CXX="$(TOOLCHAIN_PREFIX)g++" \
		CPPPATH="$(STAGING_DIR)/usr/include" \
		LIBPATH="$(STAGING_DIR)/usr/lib" \
		CCFLAGS="$(BUILD_CCFLAGS)" \
		$(SCONS_OPTIONS); \
	cd $(PKG_BUILD_DIR)/build/opt/mongo; \
	$(TOOLCHAIN_PREFIX)strip -s mongo; \
	$(TOOLCHAIN_PREFIX)strip -s mongod; \
	$(TOOLCHAIN_PREFIX)strip -s mongos; \
)
endef
endif

ifeq ($(CONFIG_MONGODB_V_4_4),y)
define Build/Configure
(\
	sh ./scripts/v4.4/replace_files.sh $(PKG_BUILD_DIR); \
	cd $(PKG_BUILD_DIR); \
	pip3 install setuptools==45; \
	pip3 install -r buildscripts/requirements.txt; \
	cd $(PKG_BUILD_DIR)/src/third_party/wiredtiger; \
	sh autogen.sh; \
	cd $(PKG_BUILD_DIR)/src/third_party/mozjs-60; \
	sh get-sources.sh; \
	sh gen-config.sh $(ARCH) $(TOOLCHAIN_PREFIX); \
	cd $(PKG_BUILD_DIR); \
	python3 buildscripts/scons.py install-core -j4 \
		$(TARGET_CFGS) $(BUILD_ARGS) \
		AR="$(TOOLCHAIN_PREFIX)ar" \
		CC="$(TOOLCHAIN_PREFIX)gcc" \
		CXX="$(TOOLCHAIN_PREFIX)g++" \
		CPPPATH="$(STAGING_DIR)/usr/include" \
		LIBPATH="$(STAGING_DIR)/usr/lib" \
		CCFLAGS="$(BUILD_CCFLAGS)"; \
	cd $(PKG_BUILD_DIR)/build/opt/mongo; \
	$(TOOLCHAIN_PREFIX)strip -s mongo; \
	$(TOOLCHAIN_PREFIX)strip -s mongod; \
	$(TOOLCHAIN_PREFIX)strip -s mongos; \
)
endef
endif

define Build/Compile
endef

define Package/mongodb/install
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ./files/mongod.init $(1)/etc/init.d/mongod
	chmod 777 $(1)/etc/init.d/mongod
	chmod +x $(1)/etc/init.d/mongod
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/build/opt/mongo/mongo $(1)/usr/bin/mongo
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/build/opt/mongo/mongod $(1)/usr/bin/mongod
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/build/opt/mongo/mongos $(1)/usr/bin/mongos
endef

$(eval $(call BuildPackage,mongodb))
