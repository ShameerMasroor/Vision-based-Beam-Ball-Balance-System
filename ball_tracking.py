import numpy as np
import cv2
import serial

#Defining PID gains
kp = 0.7
kd = 0.1     #best results at Kp=0.7 and Kd=0.1
ki  =0.001
last_error =0 
stepper_pos=0
integral=0
ser = serial.Serial('com15', 115200)
def measure_distance(frame, center):
  """Measures the distance between the center of the frame and the red object.

  Args:
    frame: A numpy array representing the frame.
    center: A tuple (x, y) representing the center of the frame.

  Returns:
    A float representing the distance between the center of the frame and the red object.
  """

  # Convert the frame to HSV color space.
  hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#   cv2.imshow("HSV",hsv)
  # Define the HSV range for red color.
  redLower1 = (50, 100, 100)
  redUpper1 = (10, 255, 255)
  redLower2 = (160, 100, 100)
  redUpper2 = (180, 255, 255)

  # Create masks for both red color ranges.
  mask1 = cv2.inRange(hsv, redLower1, redUpper1)
  mask2 = cv2.inRange(hsv, redLower2, redUpper2)
  mask = cv2.bitwise_or(mask1, mask2)

  # Erode and dilate the mask to remove noise.
  mask = cv2.erode(mask, None, iterations=2)
  mask = cv2.dilate(mask, None, iterations=2)
  cv2.imshow("mask",mask)
  # Find the contours of the red object.
  cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

  # Find the center of the red object.
  if len(cnts) > 0:
    c = max(cnts, key=cv2.contourArea)
    ((x, y), radius) = cv2.minEnclosingCircle(c)

    # Calculate the distance between the center of the frame and the red object.
    distance = np.linalg.norm(np.array([x, y]) - center)
    distance = round(distance, 0)
    # Draw a circle around the red object.
    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 0, 255), 2)
    cv2.circle(frame, (int(x), int(y)), 4, (0, 255, 255), 1)
    if y > center[1]:   #uncomment if using
        distance *= -1
    # Print the distance to the console.
    # print("Distance to red object:", distance)
    if (distance > 200):
      distance=200
    elif distance <-200:
      distance = -200
    
    return (distance//4)   #dividing by 4 to convert pixels to another unit. Trial and error basis
  else:
    return None

# Capture the frame from the camera.
cap = cv2.VideoCapture(0)

# Get the center of the frame.
center = (cap.get(cv2.CAP_PROP_FRAME_WIDTH) // 2, cap.get(cv2.CAP_PROP_FRAME_HEIGHT) // 2)

while True:
  # Read the next frame from the camera.
  ret, frame = cap.read()
  
  # If the frame is not empty, measure the distance of the red object from the center of the frame.
  if ret:
    
    distance = measure_distance(frame, center)
    if (distance!=None):
      error = distance
      integral+=error
      difference=error - last_error
      if(error!=0):
        if(difference==0) and (-15<error<15):
          difference=4
          kd = 1
        else:
          kd = 0.1
      else:
        kd=0.1
      control_signal = (kp * error) + kd*(difference) + (ki*integral)  #first it was - with kd
      last_error = error

      control_signal = round(control_signal,0)
    #writing the position_output to the motor controller
      ser.write(str(control_signal).encode())  #%45 to restrict the range of motion. Determined thru trial and error
      # ser.flush()
      print(control_signal)  #for testing

    # If the distance is not None, print it to the screen and draw a circle around the red object.
    if distance is not None:
      # Print the distance to the screen.
      cv2.putText(frame, "Distance to red object: {}".format(distance), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
      center = (int(center[0]), int(center[1]))
      center_x=center[0]
      center_y=center[1]
      
      # Draw a circle around the red object.
      cv2.circle(frame, center, 5, (0, 255, 0), 2)

  # Display the frame.
  # cv2.resize("Frame", frame,200,300)
  cv2.imshow("Frame", frame)
  
  # If the 'q' key is pressed, break the loop.
  if cv2.waitKey(1) & 0xFF == ord("q"):
    break

# Release the camera and close all windows.
# img = cv2.imread(r"path\to\img")
# cv2.line(img, (0, 0), (255, 255), (255, 0, 0), 1, 1)

cap.release()
cv2.destroyAllWindows()