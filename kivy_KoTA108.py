import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
from kivy.core.window import Window
from kivy.graphics import Canvas
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.base import EventLoop
from kivy.lang import Builder
import cv2
import ffmpeg
import numpy as np
import time
from threading import Thread
import os
import subprocess
import audioRecording as audioRec
# import bpy

# Config.set('graphics', 'width', '1366')
# Config.set('graphics', 'height', '768')
# Window.clearcolor = (0.19, 0.19, 0.19, 1)
Window.maximize()
# print(Window.size)

#Variabel Global
# statusRecord = None



class KivyCamera(Image):

    def start(self, capture,out, statusRecord):
        self.capture = capture
        self.fps = 30
        self.out = out
        self.statusRecord = statusRecord
        Clock.schedule_interval(self.update,1.0/self.fps)

    def startRecord(self, statusRecord):
        self.statusRecord = statusRecord

    def stop(self, statusRecord):
        self.statusRecord = statusRecord

    def record(self,frame):
        self.out.write(frame)


    def greenScreen(self,frame):
        img = cv2.imread("background/background.jpg")
        img = cv2.resize(img,(1280,720))
        hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame,(1280,720))
        u_green = np.array([140, 255, 30])
        l_green = np.array([70, 200, 0])
        mask = cv2.inRange(frame,l_green,u_green)
        res = cv2.bitwise_and(frame,frame,mask=mask)
        f=frame - res
        f=np.where(f==0,img,f)
        return f

    def update(self, dt):
        return_value, frame = self.capture.read()
        frame = cv2.flip(frame, 1)
        frame = self.greenScreen(frame)
        if return_value:
            #record script
            if self.statusRecord == True:
                self.out.write(frame)

            texture = self.texture
            w, h = frame.shape[1], frame.shape[0]

            scale_percent = 100
            width = int(w *scale_percent /100)
            height = int(h * scale_percent /100)
            dim = (width, height)

            #resize
            resized = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

            if not texture or texture.width != w or texture.height != h:
                self.texture = texture = Texture.create(size=(width, height))
                texture.flip_vertical()
            texture.blit_buffer(resized.tobytes(), colorfmt='bgr')
            self.canvas.ask_update()



capture = None
out = None
audio = None

class Widgets(Widget):
    def init_qrtest(self):
        try:
            os.mkdir("VideoRecorder")
        except FileExistsError:
            pass
        os.chdir("VideoRecorder")

        defaultFile = "Video.mp4"
        available = False
        fileNum = 0
        while available == False:
            hasMatch = False
            for item in os.listdir():
                if item == defaultFile:
                    hasMatch = True
                    break
            if not hasMatch:
                available = True
            else:
                fileNum += 1
                defaultFile = "Video" + str(fileNum) + ".mp4"
        os.chdir("..")

        self.defaultFile = defaultFile

        # some Variable
        self.audio = audioRec.audioRecord()
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.out = cv2.VideoWriter('temp/temp.mp4', fourcc, 15, (1280, 720))
        self.capture = cv2.VideoCapture(0)
        self.statusRecord = False

        self.ids.qrcam.start(self.capture, self.out,  self.statusRecord)

    def stopRecord(self):
        self.statusRecord = False
        self.ids.qrcam.stop(self.statusRecord)

    def startRecording(self):
        self.statusRecord = True
        self.audio.record("temp/temp.wav")
        self.ids.qrcam.startRecord(self.statusRecord)

    def stopRecording(self):
        if self.capture != None:
            try:
                self.capture.release()
                self.out.release()
                self.audio.stop_recording()

                while self.statusRecord != False:
                    self.statusRecord = self.audio.getStatus()
                    time.sleep(0.5)
                    print(self.statusRecord)

                self.fileAudio = ffmpeg.input('temp/temp.wav')
                self.fileVideo = ffmpeg.input('temp/temp.mp4')
                self.finish = ffmpeg.output(self.fileAudio, self.fileVideo, 'VideoRecorder/'+self.defaultFile)
                self.finish.run()
                print("FINISH CONFIG")
                self.init_qrtest()
            except ffmpeg.Error as e:
                print(e)



    def doexit(self):

        EventLoop.close()

    def show_popup(self):
        show = P()
        popupWindow = Popup(title="Popup Window", content=show, size_hint=(None, None), size=(400, 400))
        popupWindow.open()

class P(FloatLayout):
    pass

class MyApp(App):

    def build(self):
       homeWin = Widgets()
       homeWin.init_qrtest()
       return homeWin



if __name__ == "__main__":
    MyApp().run()