import cv2
import numpy as np
from collections import deque

#default function
def fun(x):
	print("")

#Creating trackbars for adjusting marker color
cv2.namedWindow('marker detector')
cv2.createTrackbar('upper hue','marker detector',150,180,fun)
cv2.createTrackbar('upper saturation','marker detector',255,255,fun)
cv2.createTrackbar('upper value','marker detector',255,255,fun)
cv2.createTrackbar('lower hue','marker detector',64,180,fun)
cv2.createTrackbar('lower saturation','marker detector',72,255,fun)
cv2.createTrackbar('lower value','marker detector',49,255,fun)

#different arrays to handle color points of different color
bp=[deque(maxlen=1024)]
gp=[deque(maxlen=1024)]
rp=[deque(maxlen=1024)]
yp=[deque(maxlen=1024)]

#indexes
bi=0
gi=0
ri=0
yi=0

#kernel used for dilation purpose
kernel=np.ones((5,5),np.uint8)

colors=[(255,0,0),(0,255,0),(0,0,255),(0,255,255)]
ci=0

#canvas setup
p=np.zeros((400,650,3))+255
p=cv2.rectangle(p,(30,1),(130,60),(0,0,0),2)
p=cv2.rectangle(p,(150,1),(250,60),colors[0],-1)
p=cv2.rectangle(p,(270,1),(370,60),colors[1],-1)
p=cv2.rectangle(p,(390,1),(490,60),colors[2],-1)
p=cv2.rectangle(p,(510,1),(610,60),colors[3],-1)

cv2.putText(p,"CLEAR",(39,33),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),2,cv2.LINE_AA)
cv2.putText(p,"BLUE",(170,33),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2,cv2.LINE_AA)
cv2.putText(p,"GREEN",(290,33),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2,cv2.LINE_AA)
cv2.putText(p,"RED",(410,33),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2,cv2.LINE_AA)
cv2.putText(p,"YELLOW",(520,33),cv2.FONT_HERSHEY_SIMPLEX,0.5,(150,150,150),2,cv2.LINE_AA)
cv2.namedWindow('paint',cv2.WINDOW_AUTOSIZE)

#loading the default webcam 
cap=cv2.VideoCapture(0)

#keep looping
while True:
	#reading the frame from the camera
	ret,frame=cap.read()
	#flipping the frame to see same side of yours(1:along y axis)
	frame=cv2.flip(frame,1)
	hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

	u_hue=cv2.getTrackbarPos('upper hue','marker detector')
	u_saturation=cv2.getTrackbarPos('upper saturation','marker detector')
	u_value=cv2.getTrackbarPos('upper value','marker detector')
	l_hue=cv2.getTrackbarPos('lower hue','marker detector')
	l_saturation=cv2.getTrackbarPos('lower saturation','marker detector')
	l_value=cv2.getTrackbarPos('lower value','marker detector')
	upper_hsv=np.array([u_hue,u_saturation,u_value])
	lower_hsv=np.array([l_hue,l_saturation,l_value])

	#Adding the color buttons to the live frame for color access
	
	frame=cv2.rectangle(frame,(30,1),(130,60),(122,122,122),2)
	frame=cv2.rectangle(frame,(150,1),(250,60),colors[0],-1)
	frame=cv2.rectangle(frame,(270,1),(370,60),colors[1],-1)
	frame=cv2.rectangle(frame,(390,1),(490,60),colors[2],-1)
	frame=cv2.rectangle(frame,(510,1),(610,60),colors[3],-1)

	cv2.putText(frame,"CLEAR",(39,33),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),2,cv2.LINE_AA)
	cv2.putText(frame,"BLUE",(170,33),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2,cv2.LINE_AA)
	cv2.putText(frame,"GREEN",(290,33),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2,cv2.LINE_AA)
	cv2.putText(frame,"RED",(410,33),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2,cv2.LINE_AA)
	cv2.putText(frame,"YELLOW",(520,33),cv2.FONT_HERSHEY_SIMPLEX,0.5,(150,150,150),2,cv2.LINE_AA)

	#Identify marker
	mask=cv2.inRange(hsv,lower_hsv,upper_hsv)
	mask=cv2.erode(mask,kernel,iterations=1)
	mask=cv2.dilate(mask,kernel,iterations=1)

	#find contour
	cnts,_=cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	center=None

	#if contours are formed
	if len(cnts)>0:
		#sorting contours to find biggest
		cnt=sorted(cnts,key=cv2.contourArea,reverse=True)[0]

		#get the radius enclosing circle around the found contour
		((x,y),radius)=cv2.minEnclosingCircle(cnt)

		#draw the circle around contour
		cv2.circle(frame,(int(x),int(y)),int(radius),(255,0,0),2)

		#Calculate the center of the detected contour
		M=cv2.moments(cnt)
		center=(int(M['m10']/M['m00']),int( M['m01']/M['m00']))

		#Now check if the user want to perform any action
		if center[1]<=60:
			if 30<=center[0]<=130:
				bp=[deque(maxlen=512)]
				gp=[deque(maxlen=512)]
				rp=[deque(maxlen=512)]
				yp=[deque(maxlen=512)]
				bi=0
				gi=0
				ri=0
				yi=0
				p[62:,:,:]=255
			elif 150<=center[0]<=250:
				ci=0
			elif 270<=center[0]<=370:
				ci=1
			elif 390<=center[0]<=490:
				ci=2
			elif 510<=center[0]<=610:
				ci=3
		else:
			if ci==0:
				bp[bi].appendleft(center)
			elif ci==1:
				gp[gi].appendleft(center)
			elif ci==2:
				rp[ri].appendleft(center)
			elif ci==3:
				yp[yi].appendleft(center)
	#append the next deques when ntg is detected to avoid messing up
	else:
		bp.append(deque(maxlen=512))
		bi+=1
		gp.append(deque(maxlen=512))
		gi+=1
		rp.append(deque(maxlen=512))
		ri+=1
		yp.append(deque(maxlen=512))
		yi+=1

	#draw lines on canvas and frame
	points=[bp,gp,rp,yp]
	for i in range(len(points)):
		for j in range(len(points[i])):
			for k in range(1,len(points[i][j])):
				if points[i][j][k-1] is None or points[i][j][k] is None:
					continue
				cv2.line(frame,points[i][j][k-1],points[i][j][k],colors[i],2)
				cv2.line(p,points[i][j][k-1],points[i][j][k],colors[i],2)
	#show all windows
	cv2.imshow('Tracking',frame)
	cv2.imshow('Paint',p)

	if cv2.waitKey(1)& 0xFF==ord('q'):
		break
#release camera and all resources
cap.release()
cv2.destroyAllWindows()

