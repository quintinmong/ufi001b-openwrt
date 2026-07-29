# SPDX-License-Identifier: GPL-2.0-only

define KernelPackage/qcom-msm8916-usb
  SUBMENU:=USB Support
  TITLE:=Qualcomm MSM8916 ChipIdea USB device controller
  DEPENDS:=@TARGET_msm89xx_msm8916 +kmod-usb-gadget +kmod-usb-roles
  KCONFIG:= \
	CONFIG_USB_CHIPIDEA \
	CONFIG_USB_CHIPIDEA_UDC=y \
	CONFIG_USB_CHIPIDEA_HOST=n \
	CONFIG_USB_CHIPIDEA_MSM \
	CONFIG_USB_CHIPIDEA_DEBUG=n
  FILES:= \
	$(LINUX_DIR)/drivers/usb/chipidea/ci_hdrc.ko \
	$(LINUX_DIR)/drivers/usb/chipidea/ci_hdrc_msm.ko
  AUTOLOAD:=$(call AutoProbe,ci_hdrc ci_hdrc_msm)
endef

define KernelPackage/qcom-msm8916-usb/description
 ChipIdea UDC and MSM glue used by the UFI001B USB device port.
endef

$(eval $(call KernelPackage,qcom-msm8916-usb))

define KernelPackage/qcom-msm8916-remoteproc
  SUBMENU:=$(OTHER_MENU)
  TITLE:=Qualcomm MSM8916 modem and WCNSS remote processors
  DEPENDS:=@TARGET_msm89xx_msm8916 +kmod-rmnet +qrtr-ns +rmtfs +rpmsgexport
  KCONFIG:= \
	CONFIG_QCOM_Q6V5_MSS \
	CONFIG_QCOM_WCNSS_PIL \
	CONFIG_QCOM_WCNSS_CTRL \
	CONFIG_QCOM_BAM_DMUX
  FILES:= \
	$(LINUX_DIR)/drivers/soc/qcom/mdt_loader.ko \
	$(LINUX_DIR)/drivers/soc/qcom/wcnss_ctrl.ko \
	$(LINUX_DIR)/drivers/remoteproc/qcom_pil_info.ko \
	$(LINUX_DIR)/drivers/remoteproc/qcom_common.ko \
	$(LINUX_DIR)/drivers/remoteproc/qcom_q6v5.ko \
	$(LINUX_DIR)/drivers/remoteproc/qcom_q6v5_mss.ko \
	$(LINUX_DIR)/drivers/remoteproc/qcom_wcnss_pil.ko \
	$(LINUX_DIR)/drivers/net/wwan/qcom_bam_dmux.ko
  AUTOLOAD:=$(call AutoProbe,mdt_loader qcom_pil_info qcom_common qcom_q6v5 wcnss_ctrl qcom_wcnss_pil qcom_q6v5_mss qcom_bam_dmux)
endef

define KernelPackage/qcom-msm8916-remoteproc/description
 Drivers needed to boot the MSM8916 MPSS and WCNSS firmware after rootfs is available.
endef

$(eval $(call KernelPackage,qcom-msm8916-remoteproc))

define KernelPackage/wcn36xx-msm8916
  SUBMENU:=Wireless Drivers
  TITLE:=Qualcomm WCN36xx Wi-Fi for MSM8916
  DEPENDS:=@TARGET_msm89xx_msm8916 +kmod-qcom-msm8916-remoteproc
  KCONFIG:= \
	CONFIG_WCN36XX \
	CONFIG_WCN36XX_DEBUGFS=n
  FILES:=$(LINUX_DIR)/drivers/net/wireless/ath/wcn36xx/wcn36xx.ko
  AUTOLOAD:=$(call AutoProbe,wcn36xx)
endef

define KernelPackage/wcn36xx-msm8916/description
 In-kernel WCN36xx WLAN driver using the MSM8916 SMD transport.
endef

$(eval $(call KernelPackage,wcn36xx-msm8916))
