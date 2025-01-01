# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2024 Bootlin
#
# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2024 Bootlin
#

include $(TOPDIR)/rules.mk

BOARD:=stm32
BOARDNAME:=STMicroelectronics STM32
FEATURES:=boot-part emmc ext4 gpio rtc usb python3 python3-cryptography python3-pyelftools
SUBTARGETS:=stm32mp1
CPU_TYPE:=

KERNEL_PATCHVER:=5.15

DEFAULT_PACKAGES += python3 python3-cryptography python3-pyelftools

HOST_BUILD_DEPENDS += python3/host python3-cryptography/host python3-pyelftools/host

include $(INCLUDE_DIR)/target.mk

define Target/Description
	Build firmware image for STM32 devices with Python tools support:
	- python3
	- python3-cryptography
	- python3-pyelftools
endef

$(eval $(call BuildTarget))
