import numpy as np
import cv2
import imutils
import pyimagesearch
from flask import Flask, render_template, Response
cap = cv2.VideoCapture(0)


class ShapeDetector:
	def __init__(self):
		pass
	def detect(self, c):
		shape = "unidentified"
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.04 * peri, True)
		area1 = cv2.contourArea(approx);
		if len(approx) == 4:
		    (x, y, w, h) = cv2.boundingRect(approx)
		    ar = w / float(h)
		    shape = "Stuff" if 10000 <= area1 else "unidentified"
		elif area1 >= 35000:
                    shape = "Intruder"
		return shape

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

def gen():
    while True:
        rval, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        median = cv2.medianBlur(gray,5)
        blurred = cv2.GaussianBlur(median, (5, 5), 0)
        thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        sd = ShapeDetector()

        for c in cnts:
                M = cv2.moments(c)
                (x,y,w,h) = cv2.boundingRect(c)
                cX = int(((M["m10"]+1) / (M["m00"]+1))*1)
                cY = int(((M["m01"]+1) / (M["m00"]+1))*1)
                shape = sd.detect(c)
                if shape != "unidentified":
                    c = c.astype("float")
                    c = c.astype("int")
                    if shape != "intruder":
                        cv2.rectangle(frame,(x,y),(x+w,y+h), (0, 255, 0), 2)
                        cv2.putText(frame, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (255, 255, 255), 2)
                    else:
                        cv2.rectangle(frame,(x,y),(x+w,y+h), (255, 0, 255), 2)
                        cv2.putText(frame, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (255, 0, 255), 2)
                    cv2.imwrite('stream.jpg', frame)
                else:
                    cv2.imwrite('stream.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open('stream.jpg', 'rb').read() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
        mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
