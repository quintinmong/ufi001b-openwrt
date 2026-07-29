# SPDX-License-Identifier: GPL-2.0-only

define Device/handsome_openstick-ufi001b
  DEVICE_VENDOR := Handsome
  DEVICE_MODEL := OpenStick UFI001B
  DEVICE_DTS := msm8916-handsome-openstick-ufi001b
  DEVICE_PACKAGES := ufi001b-base kmod-qcom-msm8916-remoteproc \
	 kmod-wcn36xx-msm8916 kmod-rmnet qrtr-ns rmtfs rpmsgexport \
	 iw iwinfo wifi-scripts
  SUPPORTED_DEVICES := handsome,openstick-ufi001b handsome,openstick
endef
TARGET_DEVICES += handsome_openstick-ufi001b
