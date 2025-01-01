# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2024 Bootlin
#

include $(TOPDIR)/rules.mk

ARCH:=arm
BOARD:=stm32
BOARDNAME:=STMicroelectronics STM32
FEATURES:=audio boot-part display ext4 fpu gpio rootfs-part rtc squashfs usb usbgadget
SUBTARGETS:=stm32mp1

KERNEL_PATCHVER:=5.15

define Target/Description
	Build firmware image for STM32 devices
endef

include $(INCLUDE_DIR)/target.mk

DEFAULT_PACKAGES := $(filter-out urngd,$(DEFAULT_PACKAGES))
DEFAULT_PACKAGES += \
	kmod-gpio-button-hotplug \
	kmod-usb-hid \
	kmod-sound-core \
	kmod-fs-vfat kmod-nls-cp437 kmod-nls-iso8859-1 \
	blockdev partx-utils mkf2fs e2fsprogs

KERNELNAME:=Image dtbs

$(eval $(call BuildTarget))
