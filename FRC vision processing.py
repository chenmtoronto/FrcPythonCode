from pyb import I2C
import sensor, image, time

# Color Tracking Thresholds (Grayscale Min, Grayscale Max)
# The below grayscale threshold is set to only find extremely bright white areas.
thresholds = (250, 255)

rightSideX = 0
leftSideX = 0
left = False
right = False

y = 320
i2c = I2C(2)                         # create on bus 2
i2c = I2C(2, I2C.SLAVE)             # create and init as a slave
i2c.init(I2C.SLAVE, addr=0x42)       # init as a slave with given address
sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.VGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock()

# Only blobs that with more pixels than "pixel_threshold" and more area than "area_threshold" are
# returned by "find_blobs" below. Change "pixels_threshold" and "area_threshold" if you change the
# camera resolution. "merge=True" merges all overlapping blobs in the image.

while(True):
    lefti=0
    righti=0
    leftTargetX = [0]
    rightTargetX = [0]
    leftTargetArea = [0]
    rightTargetArea = [0]
    center = [0]
    clock.tick()
    img = sensor.snapshot()
    for blob in img.find_blobs([thresholds], pixels_threshold=100, area_threshold=100, merge=True):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
        #print((blob.rotation()*57.2958)-90)
        if ((blob.rotation()*57.2958)-90 < 0):
            if righti > 0:
                rightTargetX.append(blob.cx())
                rightTargetArea.append(blob.area())
            else:
                rightTargetX[righti] = blob.cx()
                rightTargetArea[righti] = blob.area()
            righti += 1
            right = True
        if ((blob.rotation()*57.2958)-90 > 0):
            if lefti > 0:
                rightTargetX.append(blob.cx())
                rightTargetArea.append(blob.area())
            else:
                leftTargetX[lefti] = blob.cx()
                leftTargetArea[lefti] = blob.area()
            lefti+=1
            left = True

        left = False
        right = False

    r = len(rightTargetX)
    # Traverse through all array elements
    for i in range(r):
    # Last i elements are already in place
        for j in range(0, r-i-1):
            # traverse the array from 0 to n-i-1
            # Swap if the element found is greater
            # than the next element
            if rightTargetX[j] > rightTargetX[j+1] :
                rightTargetX[j], rightTargetX[j+1] = rightTargetX[j+1], rightTargetX[j]
                rightTargetArea[j], rightTargetArea[j+1] = rightTargetArea[j+1], rightTargetArea[j]

    l = len(leftTargetX)
    # Traverse through all array elements
    for i in range(l):
    # Last i elements are already in place
        for j in range(0, l-i-1):
            # traverse the array from 0 to n-i-1
            # Swap if the element found is greater
            # than the next element
            if leftTargetX[j] > leftTargetX[j+1]:
                leftTargetX[j], leftTargetX[j+1] = leftTargetX[j+1], leftTargetX[j]
                leftTargetArea[j], leftTargetArea[j+1] = leftTargetArea[j+1], leftTargetArea[j]

    if (rightTargetX[0] < leftTargetX[0]):
        rightTargetX.pop(0)
    if (len(rightTargetX) != len(leftTargetX)):
        leftTargetX.pop(len(leftTargetX)-1)

    num = len(leftTargetX)
    for i in range(0, num):
        if i>0:
            center.append((rightTargetX[i]-leftTargetX[i])/2 + leftTargetX[i])
        else:
            center[i] = ((rightTargetX[i]-leftTargetX[i])/2 + leftTargetX[i])
        img.draw_cross(int(center[i]),y)

    left = False
    right = False


