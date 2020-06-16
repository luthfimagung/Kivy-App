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
import cv2
import numpy as np
import bpy

# Config.set('graphics', 'width', '1366')
# Config.set('graphics', 'height', '768')
# Window.clearcolor = (0.19, 0.19, 0.19, 1)
Window.maximize()
# print(Window.size)

class KivyCamera(Image):
    def __init__(self, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.capture = None

    def start(self, capture, fps=30):
        self.capture = capture
        Clock.schedule_interval(self.update, 1.0 / fps)

    def stop(self):
        Clock.unschedule_interval(self.update)
        self.capture = None

    def greenScreen(self,frame):
        img = cv2.imread("background.jpg")
        img = cv2.resize(img,(1280,720))
        hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        frame = cv2.resize(frame,(1280,720))
        u_green = np.array([140, 255, 30])
        l_green = np.array([70, 200, 0])
        mask = cv2.inRange(frame,l_green,u_green)
        res = cv2.bitwise_and(frame,frame,mask=mask)
        f=res-frame
        f=np.where(f==0,img,f)
        return f

    def update(self, dt):
        return_value, frame = self.capture.read()
        frame = cv2.flip(frame, 1)
        P = KivyCamera()
        frame = P.greenScreen(frame)
        if return_value:
            texture = self.texture
            w, h = frame.shape[1], frame.shape[0]

            scale_percent = 60
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

class Widgets(Widget):
    def init_qrtest(self):
        pass

    def dostart(self, *largs):
        global capture
        capture = cv2.VideoCapture(0)
        self.ids.qrcam.start(capture)

    def doexit(self):
        global capture
        if capture != None:
            capture.release()
            capture = None
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

    def on_stop(self):
        global capture
        if capture:
            capture.release()
            capture = None

if __name__ == "__main__":
    MyApp().run()