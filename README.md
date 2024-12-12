# NeonWrt
基於 OpenWrt 開發之智慧家庭中樞

Run ./scripts/feeds update -a to obtain all the latest package definitions defined in feeds.conf / feeds.conf.default

Run ./scripts/feeds install -a to install symlinks for all obtained packages into package/feeds/

Run make menuconfig to select your preferred configuration for the toolchain, target system & firmware packages.

Run make to build your firmware. This will download all sources, build the cross-compile toolchain and then cross-compile the GNU/Linux kernel & all chosen applications for your target system.