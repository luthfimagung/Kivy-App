#Kivy
import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
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
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import *
from kivy.graphics import *

#OpenCV
import cv2
import ffmpeg
from PIL import ImageGrab

#Python
import numpy as np
import time
from threading import Thread
import os
import subprocess
import audioRecording as audioRec

#OpenGL
import glfw
from objloader import ObjLoader
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GL.shaders import compileProgram, compileShader
import pyrr
from TextureLoader import load_texture
# Config.set('graphics','resizable',True)
# Config.set('graphics', 'width', '1920')
# Config.set('graphics', 'height', '1080')
# Window.clearcolor = (0.19, 0.19, 0.19, 1)
Window.maximize()
# Window.size = (1280,720)
# print(Window.size)

#Variabel Global
# statusRecord = None
vertex_src = """
# version 330
layout(location = 0) in vec3 a_position;
layout(location = 1) in vec2 a_texture;
layout(location = 2) in vec3 a_normal;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;

out vec2 v_texture;

void main()
{
    gl_Position = projection * view * model * vec4(a_position, 1.0);
    v_texture = a_texture;
}
"""
fragment_src = """
# version 330
in vec2 v_texture;
out vec4 out_color;
uniform sampler2D s_texture;
void main()
{
    out_color = texture(s_texture, v_texture);
}
"""



class Background():

    def build(self):
        # glfw callback functions
        def window_resize(window, width, height):
            glViewport(0, 0, width, height)
            projection = pyrr.matrix44.create_perspective_projection_matrix(45, width / height, 0.1, 100)

        # initializing glfw library
        if not glfw.init():
            raise Exception("glfw can not be initialized!")

        # creating the window
        window = glfw.create_window(1280, 720, "My OpenGL window", None, None)

        # check if window was created
        if not window:
            glfw.terminate()
            raise Exception("glfw window can not be created!")

        # set window's position
        glfw.set_window_pos(window, 400, 200)

        # set the callback function for window resize
        glfw.set_window_size_callback(window, window_resize)

        # make the context current
        glfw.make_context_current(window)

        # load here the 3d meshes
        background_indices, background_buffer = ObjLoader.load_model("background1.obj")

        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))

        # VAO and VBO
        VAO = glGenVertexArrays(2)
        VBO = glGenBuffers(2)

        # Background VAO
        glBindVertexArray(VAO[0])
        # Background Vertex Buffer Object
        glBindBuffer(GL_ARRAY_BUFFER, VBO[0])
        glBufferData(GL_ARRAY_BUFFER, background_buffer.nbytes, background_buffer, GL_STATIC_DRAW)

        # Background vertices
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, background_buffer.itemsize * 8, ctypes.c_void_p(0))
        # Background textures
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, background_buffer.itemsize * 8, ctypes.c_void_p(12))
        # Background normals
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, background_buffer.itemsize * 8, ctypes.c_void_p(20))
        glEnableVertexAttribArray(2)

        # textures = glGenTextures(2)
        # load_texture("background/background.jpg", textures[0])

        glUseProgram(shader)
        glClearColor(0, 0.1, 0.1, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        projection = pyrr.matrix44.create_perspective_projection_matrix(45, 1280 / 720, 0.1, 100)
        background_pos = pyrr.matrix44.create_from_translation(pyrr.Vector3([-4, 0, 0]))

        # eye, target, up
        view = pyrr.matrix44.create_look_at(pyrr.Vector3([0, 0, 8]), pyrr.Vector3([0, 0, 0]), pyrr.Vector3([0, 1, 0]))

        model_loc = glGetUniformLocation(shader, "model")
        proj_loc = glGetUniformLocation(shader, "projection")
        view_loc = glGetUniformLocation(shader, "view")

        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

        # the main application loop
        while not glfw.window_should_close(window):
            glfw.poll_events()

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            rot_y = pyrr.Matrix44.from_y_rotation(0.8 * glfw.get_time())
            model = pyrr.matrix44.multiply(rot_y, background_pos)

            # draw the chibi character
            glBindVertexArray(VAO[0])
            glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
            glDrawArrays(GL_TRIANGLES, 0, len(background_indices))
            # glDrawElements(GL_TRIANGLES, len(chibi_indices), GL_UNSIGNED_INT, None)

            glfw.swap_buffers(window)

        # terminate glfw, free up allocated resources
        glfw.terminate()


class FrontEnd(FloatLayout):
    pass

class FloatLayout(FloatLayout):
    pass
class KivyCamera(Image):

    def start(self, capture, out):
        self.capture = capture
        self.out = out
        self.fps = 30
        Clock.schedule_interval(self.update, 1.0/self.fps)

    def startRecord(self, statusRecord):
        print(statusRecord)


    def update(self, dt):
        return_value, frame = self.capture.read()
        frame = cv2.flip(frame, 1, None)
        if return_value:
            texture = self.texture
            w, h = frame.shape[1], frame.shape[0]
            scale_percent = 100
            width = int(w*scale_percent/100)
            height = int(h*scale_percent/100)
            dim = (width, height)

            resized = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
            if not texture or texture.width != w or texture.height != h:
                self.texture = texture = Texture.create(size=(width, height))
                texture.flip_vertical()
            texture.blit_buffer(resized.tobytes(), colorfmt='bgr')
            self.canvas.ask_update()

class Widgets(Widget):
    pass

class Layers(Widgets):
    def __init__(self, **kwargs):
        super(Layers, self).__init__(**kwargs)
        self.layer1 = None
        self.layer2 = None
        self.layer3 = None
        self.temp1 = "temp1.jpg"
        self.temp2 = "temp2.jpg"
        self.temp3 = "temp3.jpg"
        self.layerUtama = 1
    def start(self, values):

        with self.canvas:
            Color(1,1,1,1)
            self.rec = Rectangle(id = "test", source="", pos= (155, 200), size= (685, 500))


        if values == 1:
            if self.layer1 != None:
                self.changeBackground(self.layer1)
        elif values == 2:
            if self.layer2 != None:
                self.changeBackground(self.layer2)
        elif values == 3 :
            if self.layer3 != None:
                self.changeBackground(self.layer3)

    def changeBackground(self, source):
        self.rec.source = source


    def on_touch_down(self, touch):
        self.canvas.add(Color(rgb=(121 / 255.0, 120 / 255.0, 100 / 255.0)))
        touch.ud['line'] = Line(points=(touch.x, touch.y), width = 2)
        self.canvas.add(touch.ud['line'])

    def on_touch_move(self, touch):
        if (touch.x >=155.0 and touch.x <840.0 ) and (touch.y>=200.0 and touch.y<700.0):
            touch.ud['line'].points +=[touch.x, touch.y]

    def clearCanvas(self):
        self.canvas.clear()
        self.start(self.layerUtama)
        self.changeBackground(None)

    def changeLayer(self, values):
        print(values)
        if self.layerUtama == 1:
            img = ImageGrab.grab(bbox=((200,155,940,800)))
            img = img.save(self.temp1)
            self.layer1 =self.temp1
            if str(values) == "Layer 2":
                self.layerUtama = 2
            else : self.layerUtama = 3

        elif self.layerUtama == 2:
            img = ImageGrab.grab(bbox=((200, 155, 940, 800)))
            img = img.save(self.temp2)
            self.layer2 = self.temp2
            if str(values) == "Layer 1":
                self.layerUtama = 1
            else: self.layerUtama = 3

        elif self.layerUtama == 3 :
            img = ImageGrab.grab(bbox=((200, 155, 940, 800)))
            img = img.save(self.temp3)
            self.layer3 = self.temp3
            if str(values) == "Layer 1":
                self.layerUtama = 1
            else: self.layerUtama = 2
        self.canvas.clear()
        self.start(self.layerUtama)

class MainScreen(Screen):
    def start(self):
        self.layerUtama = 1
        self.statusRecord = False
        self.capture = cv2.VideoCapture(0)
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter('testing.avi', self.fourcc, 15, (1280, 720))
        self.ids.layers.start(None)
        self.ids.qrcam.start(self.capture, self.out)

    def record(self):
        self.statusRecord = True
        self.ids.qrcam.startRecord(self.statusRecord)

    def clearCanvas(self):
        self.ids.layers.clearCanvas()

    def spinner_clicked(self, values):
        self.ids.layers.changeLayer(values)


class CheckScreen(Screen):
    def check(self):
        # print("BEING CHECK")
        # cap = cv2.VideoCapture(0)
        # if cap.isOpened():
        #     cap.release()
        #     self.manager.get_screen("main").start()
        #     self.manager.current = "main"
        # else: print("Fales")
        self.manager.get_screen("main").start()
        self.manager.current = "main"

class Manager(ScreenManager):
    pass

class MyApp(App):
    def build(self):
        return Manager()

if __name__=="__main__":
    MyApp().run()


## FILE DULU
# class KivyCamera(Image):
#
#     def start(self, capture, out, statusRecord):
#         if capture == None:
#             print("GAGAL")
#         self.capture = capture
#         self.fps = 30
#         self.out = out
#         self.statusRecord = statusRecord
#         Clock.schedule_interval(self.update,1.0/self.fps)
#
#     def startRecord(self, statusRecord):
#         self.statusRecord = statusRecord
#
#     def stop(self, statusRecord):
#         self.statusRecord = statusRecord
#
#     def record(self,frame):
#         self.out.write(frame)
#
#     def greenScreen(self,frame):
#         img = cv2.imread("background/background.jpg")
#         # img = ImageGrab.grab(bbox=((200,155,940,800)))
#         # img = np.array(img)
#         frame = cv2.resize(frame,(720,480))
#         img = cv2.resize(img,(720,480))
#         hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
#         u_green = np.array([70, 255, 70])
#         l_green = np.array([0, 100, 0])
#         mask = cv2.inRange(frame,l_green,u_green)
#         res = cv2.bitwise_and(frame,frame,mask=mask)
#         f=frame - res
#         f=np.where(f==0,img,f)
#         return f
#
#     def update(self, dt):
#         return_value, frame = self.capture.read()
#         frame = cv2.flip(frame, 1)
#         # frame = self.greenScreen(frame)
#         if return_value:
#             #record script
#             if self.statusRecord == True:
#                 self.out.write(frame)
#
#             texture = self.texture
#             w, h = frame.shape[1], frame.shape[0]
#
#             scale_percent = 100
#             width = int(w *scale_percent /100)
#             height = int(h * scale_percent /100)
#             dim = (width, height)
#             #resize
#             resized = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
#             if not texture or texture.width != w or texture.height != h:
#                 self.texture = texture = Texture.create(size=(width, height))
#                 texture.flip_vertical()
#             texture.blit_buffer(resized.tobytes(), colorfmt='bgr')
#             self.canvas.ask_update()
#
#
#
# capture = None
# out = None
# audio = None
#
# class Widgets(Widget):
#     def __init__(self, **kwargs):
#         super(Widgets, self).__init__(**kwargs)
#         #
#         # try:
#         #     os.mkdir("temp")
#         #
#         # except FileExistsError:
#         #     print("exist temp")
#         #
#         #
#         # try:
#         #     os.mkdir("VideoRecorder")
#         #
#         # except FileExistsError:
#         #     print("exist video recorder")
#         #
#         # os.chdir("VideoRecorder")
#         #
#         # defaultFile = "Video.mp4"
#         # available = False
#         # fileNum = 0
#         # while available == False:
#         #     hasMatch = False
#         #     for item in os.listdir():
#         #         if item == defaultFile:
#         #             hasMatch = True
#         #             break
#         #     if not hasMatch:
#         #         available = True
#         #     else:
#         #         fileNum += 1
#         #         defaultFile = "Video" + str(fileNum) + ".mp4"
#         #         print(defaultFile)
#
#         os.chdir("..")
#         # print(os.path.)
#         # self.defaultFile = defaultFile
#
#         # some Variable
#         self.audio = audioRec.audioRecord()
#         fourcc = cv2.VideoWriter_fourcc(*'XVID')
#         self.out = cv2.VideoWriter('temp/temp.avi', fourcc, 15, (1280, 720))
#         self.capture = cv2.VideoCapture(0)
#         self.statusRecord = False
#         self.ids.qrcam.start(self.capture, self.out,  self.statusRecord)
#
#     def on_touch_down(self, touch):
#         self.canvas.add(Color(rgb=(121 / 255.0, 120 / 255.0, 100 / 255.0)))
#         touch.ud['line'] = Line(points=(touch.x, touch.y), width = 2)
#         self.canvas.add(touch.ud['line'])
#
#     def on_touch_move(self, touch):
#         if (touch.x >=155.0 and touch.x <840.0 ) and (touch.y>=200.0 and touch.y<700.0):
#             touch.ud['line'].points +=[touch.x, touch.y]
#
#     def startRecording(self):
#         self.statusRecord = True
#         self.audio.record("temp/temp.wav")
#         self.ids.qrcam.startRecord(self.statusRecord)
#
#     def stopRecording(self):
#         if self.capture != None:
#             try:
#                 self.audio.stop_recording()
#                 while self.statusRecord != False:
#                     self.statusRecord = self.audio.getStatus()
#                     time.sleep(0.5)
#                     print(self.statusRecord)
#                     if self.statusRecord == False:
#                         self.out.release()
#                         self.capture.release()
#                         print("DONE RELEASE")
#                 # path1 = os.path.abspath('temp/temp.wav')
#                 # path2 = os.path.abspath('temp/temp.mp4')
#                 # self.fileAudio = ffmpeg.input(path1)
#                 # if self.fileAudio != None:
#                 #     print("FILE AUDIO OKE")
#                 # else: print("FILE KOSONG")
#                 #
#                 # self.fileVideo = ffmpeg.input(path2)
#                 # if self.fileVideo != None:
#                 #     print("FILE Video OKE")
#                 # else:
#                 #     print("FILE KOSONG Video")
#                 #
#                 # self.finish = ffmpeg.output(self.fileAudio, self.fileVideo, self.defaultFile)
#                 # print("OUTPUT OKE")
#                 # self.finish.run()
#                 # print("FINISH CONFIG")
#
#             except ffmpeg.Error as e:
#                 print(e)
#
#     def do_exit(self):
#         EventLoop.close()
#
#     def show_popup(self):
#         show = P()
#         popupWindow = Popup(title="Popup Window", content=show, size_hint=(None, None), size=(400, 400))
#         popupWindow.open()

# class P(FloatLayout):
#     pass
#
# class MyApp(App):
#
#     def build(self):
#         homeWin = Widgets()
#         return homeWin
#
# if __name__ == "__main__":
#     MyApp().run()
#     # Background().build()