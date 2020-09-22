#Kivy
import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.uix.videoplayer import VideoPlayer
from kivy.uix.video import Video
from kivy.graphics import *
from kivy3dgui.layout3d import Layout3D


#OpenCV
import cv2
import ffmpeg
from PIL import ImageGrab

#Python
import numpy as np
import time
import os
import audioRecording as audioRec
from testingPDFViewer import PDFDocumentWidget
Window.maximize()

class FrontEnd(FloatLayout):
    pass

class FloatLayout(FloatLayout):
    pass

class LayersImage(Image):
    def start(self):
        self.fps = 30
        self.event = Clock.schedule_interval(self.update, 1.0/self.fps)

    def stop(self):
        Clock.unschedule(self.event)

    def update(self, dt):
        img = ImageGrab.grab(bbox=((200, 155, 1050, 774)))
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        buf1 = cv2.flip(img, 0)
        buf = buf1.tobytes()
        image_texture = Texture.create(
            size=(img.shape[1], img.shape[0]), colorfmt='bgr')
        image_texture.blit_buffer(buf, colorfmt='bgr')
        # display image from the texture
        self.texture = image_texture

class KivyCamera(Image):
    def start(self, red, green, blue):
        self.greenValue = green
        self.redValue = red
        self.blueValue = blue
        self.capture = cv2.VideoCapture(0)
        self.statusRecord = False
        self.fps = 30
        self.img = cv2.imread("data/imgs/cameraStudio1.png")
        self.event =  Clock.schedule_interval(self.update, 1.0/self.fps)

    def stops(self):
        Clock.unschedule(self.event)
        self.capture.release()

    def changeRedValue(self, value):
        self.redValue = value

    def changeBlueValue(self, value):
        self.blueValue = value

    def changeGreenValue(self, value):
        self.greenValue = value

    def changeBackground(self, value):
        if value == 1 :
            self.img = cv2.imread("data/imgs/cameraStudio1.png")
        elif value == 2:
            self.img = cv2.imread("data/imgs/cameraStudio2.png")

    def greenScreen(self,frame):
        frame = cv2.resize(frame, (1280, 720))
        img = cv2.resize(self.img, (1280, 720))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        u_green = np.array([self.redValue, self.greenValue, self.blueValue])
        l_green = np.array([self.redValue - 59, self.greenValue - 59, self.blueValue - 59])
        mask = cv2.inRange(frame, l_green, u_green)
        res = cv2.bitwise_and(frame, frame, mask = mask)
        f = frame-res
        f = np.where(f==0, img, f)
        return f

    def update(self, dt):
        return_value, frame = self.capture.read()
        frame = cv2.flip(frame, 1, None)
        frame = self.greenScreen(frame)
        if return_value:
            buf1 = cv2.flip(frame,0)
            buf = buf1.tobytes()
            image_texture = Texture.create(
                size = (frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.texture = image_texture
            # texture = self.texture
            # w, h = frame.shape[1], frame.shape[0]
            # scale_percent = 100
            # width = int(w*scale_percent/100)
            # height = int(h*scale_percent/100)
            # dim = (width, height)
            #
            # resized = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
            # if not texture or texture.width != w or texture.height != h:
            #     self.texture = texture = Texture.create(size=(width, height), colorfmt='bgr')
            #     texture.flip_vertical()
            # texture.blit_buffer(resized.tobytes(), colorfmt='bgr')
            # self.canvas.ask_update()

class Widgets(Widget):
    pass

class PDFViewer(PDFDocumentWidget):
    def __init__(self, **kwargs):
        super(PDFViewer, self).__init__(**kwargs)
        self.temp = None
        self.obj = None

    def start(self):
        if self.temp != None:
            self.source = self.temp
            self.cols = 1
            self.pos = 155, 200
            self.size_hint = None, None
            self.size = 685, 500

    def displayPDF(self, source):
        self.temp = source
        if self.obj != None:
            self.canvas.remove(self.obj)
        self.start()

    def clearCanvas(self):
        self.obj = InstructionGroup()
        self.obj.add(Color(1, 1, 1, 1))
        self.obj.add(Rectangle(pos=(155, 200), size=(685, 500)))
        self.canvas.add(self.obj)

class Layers(Widgets):
    def __init__(self, **kwargs):
        super(Layers, self).__init__(**kwargs)
        self.layer1 = None
        self.layer2 = None
        self.layer3 = None
        self.temp1 = "temp/temp1.jpg"
        self.temp2 = "temp/temp2.jpg"
        self.temp3 = "temp/temp3.jpg"
        self.layerUtama = 1

    def startVideo(self):
        self.rec.state = 'play'

    def stopVideo(self):
        self.rec.state = 'stop'

    def pauseVideo(self):
        self.rec.state = 'pause'

    def start(self, values):
        with self.canvas:
            Color(1,1,1,1)
            self.can = Rectangle(pos= (155, 200), size= (685, 500))
            if self.layerUtama == 1:
                self.rec = Image(source = "", pos= (155, 200), size= (685, 500))
            elif self.layerUtama == 2:
                self.rec = Video(source = "", pos= (155, 200), size= (685, 500))

        if values == 1:
            if self.layer1 != None:
                self.changeBackground(self.layer1)
        elif values == 2:
            if self.layer2 != None:
                self.changeBackground(self.layer2)

    def changeBackground(self, source):
        self.rec.source = source
        if self.layerUtama == 2:
            self.temp2 = source
            self.startVideo()

    def on_touch_down(self, touch):
        self.canvas.add(Color(rgb=(121 / 255.0, 120 / 255.0, 100 / 255.0)))
        touch.ud['line'] = Line(points=(touch.x, touch.y), width = 2)
        self.canvas.add(touch.ud['line'])

    def on_touch_move(self, touch):
        if (touch.x >155.0 and touch.x <840.0 ) and (touch.y>210.0 and touch.y<680.0):
            touch.ud['line'].points +=[touch.x, touch.y]

    def clearCanvas(self):
        self.canvas.clear()
        self.start(self.layerUtama)
        self.changeBackground('')

    def Layer3(self):
        self.canvas.clear()
        self.layerUtama = 3

    def changeLayer(self, values):
        if self.layerUtama == 1:
            print("LAYER 1")
            img = ImageGrab.grab(bbox=((200, 155, 1050, 774)))
            img = img.save(self.temp1)
            imgtemp = Image(source=self.temp1)
            imgtemp.reload()
            self.layer1 = self.temp1
            if values == 2:
                self.layerUtama = 2


        elif self.layerUtama == 2:
            print("LAYER 2")
            self.layer2 = self.temp2
            if values == 1 :
                self.layerUtama = 1

        elif values == 1:
            self.layerUtama = 1
        else:
            self.layerUtama = 2

        self.canvas.clear()
        self.start(self.layerUtama)


class TestingPlish(Layout3D):
    pass


class VideoRecording:
    def __init__(self):
        self.statusRecord = False
        self.process = None
        self.error = False
        self.finish = False

    def record(self):
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.out = cv2.VideoWriter('temp/temp.mp4', fourcc, 10.0, (858, 480))
        self.statusRecord = True
        self.process = Clock.schedule_interval(self.update, 1.0/30)

    def update(self,dt):
        img = ImageGrab.grab(bbox=((1135, 135, 1918, 619)))
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (858, 480))
        if self.statusRecord:
            self.out.write(img)

    def stopRecording(self):
        print("Stop Recording")
        self.statusRecord = False
        self.out.release()

class MainScreen(Screen):
    def start(self, red, green, blue, studio):
        #MELAKUKAN PENGECEKAN UNTUK FILE
        try:
            os.mkdir("temp")
        except FileExistsError:
            print("exist temp")

        try:
            os.mkdir("VideoRecorder")
        except FileExistsError:
            print("EXIST VIDEO RECORDER")
        #MEMBUAT NAMA FILE UNTUK MENYIMPAN VIDEO DAN AUDIO
        os.chdir("VideoRecorder")
        defaultFile = "Video.mp4"
        avail = False
        fileNum = 0
        while avail == False:
            hasMatch = False
            for item in os.listdir():
                if item == defaultFile:
                    hasMatch = True
                    break
            if not hasMatch:
                avail = True
            else:
                fileNum+=1
                defaultFile = "Video"+str(fileNum)+".mp4"

        os.chdir("..")
        self.redValue = red
        self.greenValue = green
        self.blueValue = blue
        self.ids.filechooser.path = os.path.abspath('tempFile/tempImage')
        # print(os.path.abspath('temp.mp4'))
        #FILE NAME
        self.defaultFile = defaultFile

        #INISIASI FILE AUDIO
        self.audio = audioRec.audioRecord()

        #INISIASI LAYER
        self.layerUtama = 1

        #STUDIO ACTIVE
        self.studio = studio
        self.deployStudio(self.studio)

        #INISIASI STATUS
        self.statusRecordAudio = False
        self.statusVideo = False

        self.valueLayers = 1

        #DISPLAY LAYER
        self.ids.layers.start(None)
        self.ids.layersImage.start()
        # self.ids.par.start()

        #DISPLAY CAMERA
        self.ids.qrcam.start( red, green, blue)
        self.ids.qrcam.changeBackground(self.studio)
        self.video = VideoRecording()

    #DEPLOYSTUDIO
    def deployStudio(self, value):
        if value == 1 :
            self.ids.backStudio.meshes = ("./data/objJadi/backStudio1.obj",)
            self.ids.floorStudio.meshes = ("./data/objJadi/floorStudio1.obj",)
            self.ids.artefactStudio.meshes = ("./data/objJadi/artefactStudio1.obj", )
            self.ids.papanStudio.meshes = ("./data/objJadi/papanStudio1.obj", )
            self.ids.papanButton.background_disabled_normal = ("./data/imgs/papanStudio1.png")
            self.ids.cameraStudio.meshes = ("./data/objJadi/cameraStudio1.obj",)
            self.ids.cameraButton.background_disabled_normal = ("./data/imgs/cameraStudio1.png")
            self.ids.mejaStudio.meshes = ("./data/objJadi/mejaStudio1.obj",)
            self.ids.mejaButton.background_disabled_normal = ("./data/imgs/mejaStudio1.png")

        elif value == 2:
            self.ids.backStudio.meshes = ("./data/objJadi/backStudio2.obj",)
            self.ids.floorStudio.meshes = ("./data/objJadi/floorStudio2.obj",)
            self.ids.artefactStudio.meshes = ("./data/objJadi/artefactStudio2.obj",)
            self.ids.papanStudio.meshes = ("./data/objJadi/papanStudio2.obj",)
            self.ids.papanButton.background_disabled_normal = ("./data/imgs/papanStudio2.png")
            self.ids.cameraStudio.meshes = ("./data/objJadi/cameraStudio2.obj",)
            self.ids.cameraButton.background_disabled_normal = ("./data/imgs/cameraStudio2.png")
            self.ids.mejaStudio.meshes = ("./data/objJadi/mejaStudio2.obj",)
            self.ids.mejaButton.background_disabled_normal = ("./data/imgs/mejaStudio2.png")


    #MENGHAPUS SEMUA ISI LAYER
    def clearCanvas(self):
        if self.valueLayers == 3:
            self.ids.pdf.clearCanvas()
            self.ids.pdf.col = 1, 1, 1, 1
        else:
            self.ids.layers.clearCanvas()

    def stopVideo(self):
        self.ids.layers.stopVideo()

    def startVideo(self):
        self.ids.layers.startVideo()

    def pauseVideo(self):
        self.ids.layers.pauseVideo()

    #MEMILIH LAYER UTAMA
    def spinner_clicked(self, values):
        if values == "Layer 2":
            self.ids.filechooser.path = os.path.abspath('tempFile/tempVideo')
            self.valueLayers = 2
            self.ids.btn3.disabled = False
            self.ids.btn4.disabled = False
            self.ids.btn2.disabled = False
            self.ids.layers.changeLayer(self.valueLayers)

        elif values == "Layer 1":

            self.valueLayers = 1
            self.ids.btn3.disabled = True
            self.ids.btn4.disabled = True
            self.ids.btn2.disabled = True
            self.ids.filechooser.path = os.path.abspath('tempFile/tempImage')
            self.ids.layers.changeLayer(self.valueLayers)

        else:
            self.valueLayers = 3
            self.ids.btn3.disabled = True
            self.ids.btn4.disabled = True
            self.ids.btn2.disabled = True
            self.ids.filechooser.path = os.path.abspath('tempFile/tempPDF')
            self.ids.layers.Layer3()
            self.ids.pdf.start()

    def cekCamera(self, value):
        self.ids.par.start()

    def displayVideo(self):
        self.popupDisplay = BoxLayout(orientation = 'vertical')
        video = VideoPlayer(source="VideoRecorder/" + self.defaultFile,
                            state='play',
                            options={'allow_stretch': True})
        button = Button(
            text = "Close",
            on_press = lambda *args: self.popup.dismiss(),
            size_hint = (None, 0.1)
        )

        self.popupDisplay.add_widget(video)
        self.popupDisplay.add_widget(button)

        self.popup = Popup(content=self.popupDisplay,
                      title=self.defaultFile,
                      title_align = 'center',
                      separator_height = '4dp',
                      title_color = [1,0.2,1,1],
                      title_size = '20sp',
                      size_hint=(0.9, 0.9),
                      auto_dismiss = True)
        self.popup.open()

    #MEMULAI DAN MEMBERHENTIKAN
    def Record(self, value):
        if value == 1:
            self.ids.record.text= "Stop"
            self.statusRecordAudio = True
            self.ids.record.values = 2
            self.audio.record("temp/temp.wav")
            self.video.record()
        else:
            self.ids.record.text = "Start"
            self.ids.record.values = 1
            self.audio.stop_recording()
            while self.statusRecordAudio != False :
                self.statusRecordAudio = self.audio.getStatus()
                time.sleep(1)
                if self.statusRecordAudio == False:
                    self.video.stopRecording()
                    self.ids.qrcam.stops()
            try:
                #COMBINE FILE WAV AND MP4
                self.fileAudio = ffmpeg.input('temp/temp.wav')
                self.fileVideo = ffmpeg.input('temp/temp.mp4')
                self.finish = ffmpeg.output(self.fileAudio, self.fileVideo, "VideoRecorder/"+self.defaultFile)
                self.finish.run()
                # print("DONE WITH FILE "+self.defaultFile)

            except ffmpeg.Error as e:
                print(str(e) + " || ERROR")

            self.displayVideo()
            self.AnimationDefault()
            self.start(self.redValue, self.greenValue, self.blueValue, self.studio)

    def AnimationDefault(self):
        self.ids.backStudio.translate = (0, -10, -80)
        self.ids.floorStudio.translate = (0, -10, -80)
        self.ids.artefactStudio.translate = (0, -10, -80)
        self.ids.cameraStudio.translate = (0, -10, -80)
        self.ids.papanStudio.translate = (0, -10, -80)
        self.ids.mejaStudio.translate = (0, -10, -80)
        self.ids.par.look_at = [0, -1, 15, 0, 2, -20, 0, 1, 0]

    def AnimationRoot(self):
        Animation(translate=(0, 8, -27), scale=(0.5, 0.5, 0.5), duration=8).start(self.ids.artefactStudio)
        Animation(translate=(0, 8, -27), scale=(0.5, 0.5, 0.5), duration=8).start(self.ids.mejaStudio)
        Animation(translate=(0, 8, -27), scale=(0.5, 0.5, 0.5), duration=8).start(self.ids.papanStudio)
        Animation(translate=(0, 8, -27), scale=(0.5, 0.5, 0.5), duration=8).start(self.ids.cameraStudio)
        Animation(translate=(0, 8, -27), scale=(0.5, 0.5, 0.5), duration=8).start(self.ids.floorStudio)
        Animation(translate=(0, 8, -27), scale=(0.5, 0.5, 0.5), duration=8).start(self.ids.backStudio)
        Animation(look_at = [0, 15, 15, 0, 15, -20, 0, 1, 0], duration=4).start(self.ids.par)

    def AnimationRoot2(self):
        Animation(translate=(0, 8, -15), scale=(0.5, 0.5, 0.5), duration=8).start(self.ids.artefactStudio)
        Animation(translate=(0, 8, -15), scale=(0.5, 0.5, 0.5), duration=8).start(self.ids.mejaStudio)
        Animation(translate=(0, 8, -15), scale=(0.5, 0.5, 0.5), duration=8).start(self.ids.papanStudio)
        Animation(translate=(0, 8, -15), scale=(0.5, 0.5, 0.5), duration=8).start(self.ids.cameraStudio)
        Animation(translate=(0, 8, -15), scale=(0.5, 0.5, 0.5), duration=8).start(self.ids.floorStudio)
        Animation(translate=(0, 8, -15), scale=(0.5, 0.5, 0.5), duration=8).start(self.ids.backStudio)
        Animation(look_at=[0, 17, 15, 0, 15, -20, 0, 1, 0], duration=4).start(self.ids.par)

    def selectFile(self, filename):
        if self.valueLayers == 3:
            self.ids.pdf.displayPDF(filename[0])
            self.ids.pdf.col= 0, 0, 0, 0
        else:
            self.ids.layers.changeBackground(filename[0])


class CheckGreenScreen(Screen):
    def start(self, studio):
        self.redValue = 60
        self.greenValue = 255
        self.blueValue = 60
        self.studio = 1
        self.ids.qrcam.start( self.redValue, self.greenValue, self.blueValue)

    def deployStudio(self, studio):
        self.changeStudio(studio)

    def changeRed(self, value):
        value = int(value)
        self.ids.labelRed.text = "Red = " + str(value)
        self.redValue = value
        self.ids.qrcam.changeRedValue(value)

    def changeGreen(self, value):
        value = int(value)
        self.ids.labelGreen.text = "Green = " + str(value)
        self.greenValue = value
        self.ids.qrcam.changeGreenValue(value)

    def changeBlue(self, value):
        value = int(value)
        self.ids.labelBlue.text = "Blue = " + str(value)
        self.blueValue = value
        self.ids.qrcam.changeBlueValue(value)

    def doneSetting(self):
        self.ids.qrcam.stops()
        self.manager.get_screen("main").start(self.redValue, self.greenValue, self.blueValue, self.studio)
        self.manager.current= "main"

    def changeStudio(self, value):
        if value == 1:
            self.ids.backStudio2.translate = (0,-10,100)
            self.ids.floorStudio2.translate = (0, -10, 100)
            self.ids.artefactStudio2.translate = (0, -10, 100)
            self.ids.cameraStudio2.translate = (0, -10, 100)
            self.ids.papanStudio2.translate = (0, -10, 100)
            self.ids.mejaStudio2.translate = (0, -10, 100)

            self.ids.backStudio.translate = (0, -10, -80)
            self.ids.floorStudio.translate = (0, -10, -80)
            self.ids.artefactStudio.translate = (0, -10,-80)
            self.ids.cameraStudio.translate = (0, -10, -80)
            self.ids.papanStudio.translate = (0, -10, -80)
            self.ids.mejaStudio.translate = (0, -10, -80)
            self.ids.qrcam.changeBackground(value)
            self.ids.btnStudio1.disabled = True
            self.ids.btnStudio2.disabled = False
            self.studio = 1

        elif value == 2:
            self.ids.backStudio.translate = (0, -10, 100)
            self.ids.floorStudio.translate = (0, -10, 100)
            self.ids.artefactStudio.translate = (0, -10, 100)
            self.ids.cameraStudio.translate = (0, -10, 100)
            self.ids.papanStudio.translate = (0, -10, 100)
            self.ids.mejaStudio.translate = (0, -10, 100)

            self.ids.backStudio2.translate = (0, -10, -80)
            self.ids.floorStudio2.translate = (0, -10, -80)
            self.ids.artefactStudio2.translate = (0, -10,-80)
            self.ids.cameraStudio2.translate = (0, -10, -80)
            self.ids.papanStudio2.translate = (0, -10, -80)
            self.ids.mejaStudio2.translate = (0, -10, -80)
            self.ids.qrcam.changeBackground(value)
            self.ids.btnStudio1.disabled = False
            self.ids.btnStudio2.disabled = True
            self.studio = 2


class Widget2(Widget):
    pass


class CheckScreen(Screen):
    def __init__(self, **kwargs):
        super(CheckScreen, self).__init__(**kwargs)
        self.checkPentab = False
        self.checkCamera = False

    def check(self):
        self.manager.get_screen("green").start(1)
        self.manager.current = "green"

    def detectCamera(self):
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            self.checkCamera = True
            self.ids.imgCheckCamera.source = 'assets/check.png'
            self.ids.detectCamera.background_normal = 'assets/camerabordered.png'
            self.finishCheck()
            cap.release()

    def detectPentab(self):
        self.checkPentab = True
        self.ids.imgCheckPentab.source = 'assets/check.png'
        self.ids.detectPentab.background_normal = 'assets/pentabbordered.png'
        self.finishCheck()

    def finishCheck(self):
        if self.checkCamera == True and self.checkPentab == True:
            self.ids.nextScreen.disabled = False


class Manager(ScreenManager):
    pass


class FrontEnd2(FloatLayout):
    pass


class Widgets2(Widget):
    pass


class TestingPlease(Layout3D):
    pass


class MyApp(App):
    def build(self):
        return Manager()


if __name__ == "__main__":
    MyApp().run()


