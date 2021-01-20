#!/usr/bin/env python3

import cv2
import depthai as dai
import numpy as np

# Start defining a pipeline
pipeline = dai.Pipeline()

# Define a source - color camera
cam_rgb = pipeline.createColorCamera()
cam_rgb.setPreviewSize(300, 300)
cam_rgb.setBoardSocket(dai.CameraBoardSocket.RGB)
cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
cam_rgb.setInterleaved(False)

# Create output
xout_rgb = pipeline.createXLinkOut()
xout_rgb.setStreamName("rgb")
cam_rgb.preview.link(xout_rgb.input)

q_rgb_list = []
for i in range(2):
    found, device_info = dai.XLinkConnection.getFirstDevice(dai.XLinkDeviceState.X_LINK_UNBOOTED)
    if not found:
        print('Device', i + 1, 'not found!')
        continue
    device = dai.Device(pipeline, device_info)
    device.startPipeline()

    # Output queue will be used to get the rgb frames from the output defined above
    q_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
    q_rgb_list.append(q_rgb)

while True:
    for i, q_rgb in enumerate(q_rgb_list):
        in_rgb = q_rgb.tryGet()  # TODO wait for queue events instead
        if in_rgb is not None:
            # data is originally represented as a flat 1D array, it needs to be converted into HxWxC form
            shape = (3, in_rgb.getHeight(), in_rgb.getWidth())
            frame_rgb = in_rgb.getData().reshape(shape).transpose(1, 2, 0).astype(np.uint8)
            frame_rgb = np.ascontiguousarray(frame_rgb)
            # frame is transformed and ready to be shown
            cv2.imshow("rgb-" + str(i + 1), frame_rgb)

        if cv2.waitKey(1) == ord('q'):
            break
