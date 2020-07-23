#Kivy
import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
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

# Config.set('graphics', 'width', '1366')
# Config.set('graphics', 'height', '768')
# Window.clearcolor = (0.19, 0.19, 0.19, 1)
Window.maximize()
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
            os.mkdir("temp")
        except FileExistsError:
            pass

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

    def on_touch_down(self, touch):
        self.canvas.add(Color(rgb=(121 / 255.0, 120 / 255.0, 100 / 255.0)))
        touch.ud['line'] = Line(points=(touch.x, touch.y), width = 2)
        self.canvas.add(touch.ud['line'])

    def on_touch_move(self, touch):
        if (touch.x >=155.0 and touch.x <840.0 ) and (touch.y>=200.0 and touch.y<700.0):
            touch.ud['line'].points +=[touch.x, touch.y]

    def startRecording(self):
        self.statusRecord = True
        self.audio.record("temp/temp.wav")
        self.ids.qrcam.startRecord(self.statusRecord)

    def stopRecording(self):
        if self.capture != None:
            try:
                self.audio.stop_recording()
                while self.statusRecord != False:
                    self.statusRecord = self.audio.getStatus()
                    time.sleep(0.5)
                    print(self.statusRecord)
                    if self.statusRecord == False:
                        self.capture.release()
                        self.out.release()

                self.fileAudio = ffmpeg.input('temp/temp.wav')
                self.fileVideo = ffmpeg.input('temp/temp.mp4')
                self.finish = ffmpeg.output(self.fileAudio, self.fileVideo, 'VideoRecorder/'+self.defaultFile)
                self.finish.run()
                print("FINISH CONFIG")
                self.init_qrtest()
            except ffmpeg.Error as e:
                print(e)

    def do_exit(self):
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
    # Background().build()