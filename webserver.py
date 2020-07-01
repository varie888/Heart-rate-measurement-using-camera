from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cv2
import numpy as np
import sys
import time
from process import Process
from video import Video

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


myvideo = Video()
#myinput = self.webcam
process = Process()
frame = np.zeros((10,10,3),np.uint8)

def runprocess(buff):
    #imgUMat = np.float32(buff)

    nparr = np.fromstring(buff, np.uint8)

    #img_np = cv2.imdecode(nparr, cv2.CV_LOAD_IMAGE_COLOR)
    #img_ipl = cv.CreateImageHeader((img_np.shape[1], img_np.shape[0]), cv.IPL_DEPTH_8U, 3)
    #cv.SetData(img_ipl, img_np.tostring(), img_np.dtype.itemsize * 3 * img_np.shape[1])

    #nparr = np.asarray( bytearray( buff ), dtype = np.uint8 )

    buff = cv2.imdecode( nparr, -1 )
    #buff = cv2.UMat(nparr)
    frame = cv2.flip(buff,1)
    process.frame_in = frame
    process.run()
    
    cv2.imshow("Processed", frame)
    
    frame = process.frame_out #get the frame to show in GUI
    f_fr = process.frame_ROI #get the face to show in GUI
    #print(self.f_fr.shape)
    bpm = process.bpm #get the bpm change over the time
    
    # print("FPS")
    # print(process.fps)

    #frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    # cv2.putText(frame, "FPS "+str(float("{:.2f}".format(process.fps))),
    #                 (20,460), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 255),2)
    # img = QImage(frame, frame.shape[1], frame.shape[0], 
    #                 frame.strides[0], QImage.Format_RGB888)
    #self.lblDisplay.setPixmap(QPixmap.fromImage(img))
    
    #f_fr = cv2.cvtColor(f_fr, cv2.COLOR_RGB2BGR)
    #self.lblROI.setGeometry(660,10,self.f_fr.shape[1],self.f_fr.shape[0])
    #f_fr = np.transpose(f_fr,(0,1,2)).copy()
    # f_img = QImage(self.f_fr, self.f_fr.shape[1], self.f_fr.shape[0], 
    #                 self.f_fr.strides[0], QImage.Format_RGB888)
    #self.lblROI.setPixmap(QPixmap.fromImage(f_img))
    
    #self.lblHR.setText("Freq: " + str(float("{:.2f}".format(self.bpm))))
    
    if process.bpms.__len__() >50:
        if(max(process.bpms-np.mean(process.bpms))<5): #show HR if it is stable -the change is not over 5 bpm- for 3s
            #self.lblHR2.setText("Heart rate: " + str(float("{:.2f}".format(np.mean(self.process.bpms)))) + " bpm")
            return np.mean(process.bpms)


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('instream')
def instream(message):
    #print("in msg:")
    #print(message)
    bpm = runprocess(message['stream'])
    if bpm is not None:
        #print("Heart rate:")
        #print(bpm)
        emit('outresults', {'bpm': bpm})

if __name__ == '__main__':
    print("Starting server...")
    socketio.run(app, host="0.0.0.0")
