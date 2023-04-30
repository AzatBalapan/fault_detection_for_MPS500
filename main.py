import cv2
import numpy as np
import snap7
import time
from snap7 import util
import struct

masterplc = snap7.client.Client()
masterplc.connect('10.1.1.6', 0, 1)  # IP address, rack, slot (from HW settings)

master_db_number = 3
master_start_offset = False
master_bit_offset = 0

slaveplc = snap7.client.Client()
slaveplc.connect('10.1.1.156', 0, 1)  # IP address, rack, slot (from HW settings)

slave_db_number = 1
slave_start_offset = False
slave_bit_offset = 0


def writeBool(plc, db_number, start_offset, bit_offset, value):
    reading = plc.db_read(db_number, start_offset, 1)  # (db number, start offset, read 1 byte)
    snap7.util.set_bool(reading, 0, bit_offset, value)  # (value 1= true;0=false) (bytearray_: bytearray, byte_index: int, bool_index: int, value: bool)
    plc.db_write(db_number, start_offset, reading)  # write back the bytearray and now the boolean value is changed in the PLC.
    return None


def readBool(plc, db_number, start_offset, bit_offset):
    reading = plc.db_read(db_number, start_offset, 1)
    a = snap7.util.get_bool(reading, 0, bit_offset)
    return bool(a)

cap = cv2.VideoCapture(1)

# define callback function for mouse events
def select_roi(event, x, y, flags, param):
    global roi_x, roi_y, roi_w, roi_h, roi_selected
    if event == cv2.EVENT_LBUTTONDOWN:
        roi_x, roi_y = x, y
        roi_selected = False
    elif event == cv2.EVENT_LBUTTONUP:
        roi_w, roi_h = x - roi_x, y - roi_y
        roi_selected = True

# create window and set mouse callback
cv2.namedWindow("Camera Stream")
cv2.setMouseCallback("Camera Stream", select_roi)

# initialize variables
roi_selected = False
fixed_center = None

while True:
    # read frame from camera
    ret, frame = cap.read()

    # check if ROI is selected and find edges and contours
    if roi_selected:
        # extract ROI from frame
        roi = frame[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]

        # convert ROI to HSV and apply blur
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        blurred = cv2.GaussianBlur(hsv, (5, 5), 0)

        # filter red color from ROI
        lower_red = np.array([0, 120, 70])
        upper_red = np.array([10, 255, 255])
        mask1 = cv2.inRange(blurred, lower_red, upper_red)

        lower_red = np.array([170, 120, 70])
        upper_red = np.array([180, 255, 255])
        mask2 = cv2.inRange(blurred, lower_red, upper_red)

        mask = cv2.add(mask1, mask2)

        # find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # find center of largest bounding rectangle of contours
        if len(contours) > 0:
            # get contour with largest bounding rectangle
            c = max(contours, key=cv2.contourArea)

            # get bounding rectangle and draw on ROI
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(roi, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # calculate center of the bounding rectangle
            center = (int(x + w/2), int(y + h/2))

            # if fixed center not yet found, use current center
            if fixed_center is None:
                fixed_center = center

            # compute distance between fixed center and current center
            dist = np.sqrt((center[0] - fixed_center[0])**2 + (center[1] - fixed_center[1])**2)
            print(f"Distance between fixed center and current center: {dist:.6f}px")
            if dist < 80:
                if dist > 8:
                    writeBool(slaveplc, slave_db_number, slave_start_offset, slave_bit_offset+1, False)
                elif dist <= 8:
                    writeBool(slaveplc, slave_db_number, slave_start_offset, slave_bit_offset + 1, True)
            temp = readBool(masterplc, master_db_number, master_start_offset, master_bit_offset)
            writeBool(slaveplc, slave_db_number, slave_start_offset, slave_bit_offset, temp)
            print(f'sensor = {temp}')
            print(f'camera state = {readBool(slaveplc, slave_db_number, slave_start_offset, slave_bit_offset + 1)}')
        # draw ROI rectangle on frame
        cv2.rectangle(frame, (roi_x, roi_y), (roi_x+roi_w, roi_y+roi_h), (0, 255, 0), 2)

    # display frame
    cv2.imshow("Camera Stream", frame)
    # check for key press
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

# release resources
cap.release()
cv2.destroyAllWindows()