# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2024 Bootlin
#

BOARDNAME:=STM32MP1 boards
ARCH:=arm
CPU_TYPE:=cortex-a7
CPU_SUBTYPE=neon-vfpv4
FEATURES+=fpu
KERNEL_IMAGES:=zImage

DEFAULT_PACKAGES += blockdev kmod-gpio-button-hotplug

HOST_BUILD_DEPENDS += python3/host python3-cryptography/host python3-pyelftools/host
