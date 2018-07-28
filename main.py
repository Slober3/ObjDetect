import cv2
import imutils
import argparse
from flask import Flask, Response
cap = cv2.VideoCapture(0)

parser = argparse.ArgumentParser(description="Command line arguments")
parser.add_argument('-i',action='store', metavar='<ip>', default='0.0.0.0', help='The ip to bind default 0.0.0.0')
parser.add_argument('-p',action='store', metavar='<port>', default='5000', help='The port to listen on default 5000')
args = parser.parse_args()

class ShapeDetector:
	def __init__(self):
		pass
	@classmethod
	def detect(self, c):
		shape = "unidentified"
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.04 * peri, True)
		(x, y, w, h) = cv2.boundingRect(approx)
		ar = w / float(h)
		area1 = cv2.contourArea(approx);
		if len(approx) == 4 and 11000 <= area1 <= 27500:
		    shape = "Stuff"+" "+" area "+str(area1) if  0.725 <= ar <= 1.966  else "Intruder"
		elif area1 >= 22000:
                    shape = "Intruder"
		return shape

app = Flask(__name__)
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
                    if shape != "Intruder":
                        '''
                        Drawing rectangle around the stuff
                        cv2.rectangle(frame,(x,y),(x+w,y+h), (0, 255, 0), 2)
                        '''
                        cv2.drawContours(frame, [c], 0, (0,255,0), 3)
                        cv2.putText(frame, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (255, 255, 255), 2)
                    else:
                        '''
                        Drawing rectangle around the stuff
                        cv2.rectangle(frame,(x,y),(x+w,y+h), (255, 0, 255), 2)
                        '''
                        cv2.drawContours(frame, [c], 0, (255,0,255), 3)
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
    app.run(host=args.i, port=int(args.p))
