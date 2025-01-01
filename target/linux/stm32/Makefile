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

DEFAULT_PACKAGES += uboot-envtools mkf2fs e2fsprogs blkid kmod-brcmfmac wpad-basic-wolfssl

KERNELNAME:=zImage dtbs

$(eval $(call BuildTarget))
