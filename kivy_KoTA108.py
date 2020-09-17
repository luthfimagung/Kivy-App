#Kivy
import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.graphics import Canvas
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.base import EventLoop
from kivy.lang import Builder
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.uix.videoplayer import VideoPlayer
from kivy.uix.video import Video
from kivy.graphics.opengl import *
from kivy.graphics import *
from kivy3dgui.layout3d import Layout3D

#OpenCV
import cv2
import ffmpeg
from PIL import ImageGrab

#Python
import numpy as np
import time
from threading import Thread
import sys
import os

import audioRecording as audioRec

#OpenGL
from objloader import ObjLoader
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GL.shaders import compileProgram
from OpenGL.GL.shaders import compileShader
import pyrr
import enchant
import win32timezone
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

Builder.load_string('''
#: import FadeTransition kivy.uix.screenmanager.FadeTransition
#: import SlideTransition kivy.uix.screenmanager.SlideTransition
#: import Layout3D kivy3dgui.layout3d
#: import Animation kivy.animation.Animation

<Manager>:
    id: manager
    check_screen: check
    main_screen: main
    green_screen: green
    #check Screen
    CheckScreen:
        id:check
        name:"check"
        manager: manager
    CheckGreenScreen:
        id:green
        name: "green"
        manager: manager
    MainScreen:
        id: main
        name:"main"
        manager: manager

<MyButton@Button>:
    # font_size: 40
    size_hint: 0.44,0.44
    background_color: 0.1, 0.5, 0.6, 1

<MyButton2@Button>:
    size_hint: 0.5, 1
    background_color: 0.1, 0.5, 0.6, 1

<MySlider@Slider>:
    size_hint: None, None
    width: '250dp'

<CheckGreenScreen>:
    widget2:widget2
    qrcam : qrcam
    Widget2:
        id:widget2
        BoxLayout:

            orientation: "vertical"
            padding: 50
            size: 600,200
            pos: 166, 110
            canvas:
                Color:
                    rgba: 0.1, 0.1, 0.1, 1
                Rectangle:
                    pos: 150, 150
                    size: 1200, 250
            BoxLayout:
                orientation:"vertical"
                size_hint: 0.9, None
                cols:2
                canvas:
                    Color:
                        rgba: 0.25, 0.25, 0.25, 1
                    Rectangle:
                        pos: 800, 170
                        size: 510, 175
                    Rectangle:
                        pos: 190, 170
                        size: 510, 175
            BoxLayout:
                orientation:"horizontal"
                size_hint: 0.9, None
                FloatLayout:
                    MyButton2:
                        id: btnStudio1
                        pos: 820, 215
                        disabled: True
                        text: "Studio 1"
                        on_press: root.deployStudio(1)
                    MyButton2:
                        id: btnStudio2
                        pos: 1080, 215
                        disabled: False
                        text: "Studio 2"
                        on_press: root.deployStudio(2)

            BoxLayout:
                orientation:"horizontal"
                size_hint: 0.9, 0.1
                cols:2
                Label:
                    id: labelRed
                    size_hint: None, None
                    pos_hint:{"x":0.1,"y":0.9}
                    text: "Red = 60"
                MySlider:
                    id:sliderRed
                    size_hint: 0.9, None
                    pos_hint:{"x":0.6,"y":0.9}
                    min:60
                    max:255
                    value: 60
                    on_value:root.changeRed(self.value)

            BoxLayout:
                orientation:"horizontal"
                size_hint:0.9,None
                cols:2
                Label:
                    id: labelGreen
                    size_hint: None, None
                    pos_hint:{"x":0.1,"y":0.5}
                    text: "Green = 255"
                MySlider:
                    size_hint: 0.9, None
                    id: sliderGreen
                    pos_hint:{"x":0.6,"y":0.5}
                    min:60
                    max:255
                    value: 255
                    on_value:root.changeGreen(self.value)

            BoxLayout:
                orientation:"horizontal"
                size_hint:0.9,0.8
                cols:2
                Label:
                    id: labelBlue
                    size_hint: None, None
                    pos_hint:{"x":0.1,"y":0.1}
                    text: "Blue = 60"
                MySlider:
                    size_hint: 0.9, None
                    id: sliderBlue
                    pos_hint:{"x":0.6,"y":0.1}
                    min:60
                    max:255
                    value: 60
                    on_value:root.changeBlue(self.value)

            FloatLayout:
                Label:
                    id: labelFile
                    text: "Select Background File..."
                    font_size: 18
                    pos: 649, 372
                Label:
                    id: labelFile
                    text: "Adjust Background Color"
                    font_size: 18
                    pos: 40, 372



        FloatLayout:
            Button:
                text: "Next Screen"
                pos: 650, 65
                size_hint: (None,None)
                size: 200, 75
                font_size: 18
                on_press: root.doneSetting()


        Layout3D:
            id: par
            look_at: [0, -1, 15, 0, 2, -20, 0, 1, 0]
            canvas_size: (1366, 768)
            size: 500,360
            pos: 500,400
            shadow: False
            Node:
                id: backStudio
                name: 'backStudio'
                rotate: (-90, 0, 1, 0)
                scale: (0.5, 0.5, 0.5)
                translate: (0, -10, -80)
                receive_shadows : False

            Node:
                id: floorStudio
                name: 'floorStudio'
                rotate: (-90, 0, 1, 0)
                scale: (0.5, 0.5, 0.5)
                translate: (0, -10, -80)
                receive_shadows : False

            Node:
                id: artefactStudio
                name: 'artefactStudio'
                rotate: (-90, 0, 1, 0)
                scale: (0.5, 0.5, 0.5)
                translate: (0, -10, -80)
                receive_shadows : False

            Node:
                id: papanStudio
                name: 'papanStudio'
                rotate: (-90, 0, 1, 0)
                scale: (0.5, 0.5, 0.5)
                translate: (0, -10, -80)
                receive_shadows : False

                FloatLayout:
                    Button:
                        id: papanButton
                        disabled: True
                        background_disabled_normal : ("./data/imgs/papanStudio1.png")
                    Image:
                        size_hint: .9, .9
                        pos_hint:{"x": 0.05, "y":0.05}
                        allow_stretch: True
                        source: "./data/imgs/polban.png"
                        canvas.before:
                            PushMatrix
                            Rotate:
                                angle: 180
                                axis: 0,0,1
                                origin: self.center
                        canvas.after:
                            PopMatrix

            Node:
                id: cameraStudio
                name: 'cameraStudio'
                rotate: (-90, 0, 1, 0)
                scale: (0.5, 0.5, 0.5)
                translate: (0, -10, -80)
                receive_shadows : False

                FloatLayout:
                    Button:
                        id: cameraButton
                        disabled: True
                        background_disabled_normal : ("./data/imgs/cameraStudio1.png")


            Node:
                id: mejaStudio
                name: 'mejaStudio'
                rotate: (-90, 0, 1, 0)
                scale: (0.5, 0.5, 0.5)
                translate: (0, -10, -80)
                receive_shadows : False

                FloatLayout:
                    Button:
                        id: mejaButton
                        disabled: True
                        background_disabled_normal : ("./data/imgs/mejaStudio1.png")
                    Image:
                        size_hint: 0.7, 0.7
                        pos_hint:{"x": 0.15, "y":0.1}
                        allow_stretch: True
                        source: "./data/imgs/polban.png"
                        canvas.before:
                            PushMatrix
                            Rotate:
                                angle: 180
                                axis: 0,0,1
                                origin: self.center
                        canvas.after:
                            PopMatrix
        Layout3D:
            id: par
            look_at: [0, -1, 15, 0, 2, -20, 0, 1, 0]
            canvas_size: (1366, 768)
            size: 500,360
            pos: 800,400
            shadow: False
            Node:
                id: backStudio
                name: 'backStudio'
                rotate: (-90, 0, 1, 0)
                scale: (0.5, 0.5, 0.5)
                translate: (0, -10, -80)
                receive_shadows : False
                meshes : ("./data/objJadi/backStudio1.obj",)
            Node:
                id: floorStudio
                name: 'floorStudio'
                rotate: (-90, 0, 1, 0)
                scale: (0.5, 0.5, 0.5)
                translate: (0, -10, -80)
                receive_shadows : False
                meshes : ("./data/objJadi/floorStudio1.obj",)
            Node:
                id: artefactStudio
                name: 'artefactStudio'
                rotate: (-90, 0, 1, 0)
                scale: (0.5, 0.5, 0.5)
                translate: (0, -10, -80)
                receive_shadows : False
                meshes : ("./data/objJadi/artefactStudio1.obj",)
            Node:
                id: papanStudio
                name: 'papanStudio'
                rotate: (-90, 0, 1, 0)
                scale: (0.5, 0.5, 0.5)
                translate: (0, -10, -80)
                receive_shadows : False
                meshes : ("./data/objJadi/papanStudio1.obj",)
                FloatLayout:
                    Button:
                        id: papanButton
                        disabled: True
                        background_disabled_normal : ("./data/imgs/papanStudio1.png")
                    Image:
                        size_hint: .9, .9
                        pos_hint:{"x": 0.05, "y":0.05}
                        allow_stretch: True
                        source: "./data/imgs/polban.png"
                        canvas.before:
                            PushMatrix
                            Rotate:
                                angle: 180
                                axis: 0,0,1
                                origin: self.center
                        canvas.after:
                            PopMatrix

            Node:
                id: cameraStudio
                name: 'cameraStudio'
                rotate: (-90, 0, 1, 0)
                scale: (0.5, 0.5, 0.5)
                translate: (0, -10, -80)
                receive_shadows : False
                meshes : ("./data/objJadi/cameraStudio1.obj",)
                FloatLayout:
                    Button:
                        id: cameraButton
                        disabled: True
                        background_disabled_normal : ("./data/imgs/cameraStudio1.png")


            Node:
                id: mejaStudio
                name: 'mejaStudio'
                rotate: (-90, 0, 1, 0)
                scale: (0.5, 0.5, 0.5)
                translate: (0, -10, -80)
                receive_shadows : False
                meshes : ("./data/objJadi/mejaStudio1.obj",)
                FloatLayout:
                    Button:
                        id: mejaButton
                        disabled: True
                        background_disabled_normal : ("./data/imgs/mejaStudio1.png")
                    Image:
                        size_hint: 0.7, 0.7
                        pos_hint:{"x": 0.15, "y":0.1}
                        allow_stretch: True
                        source: "./data/imgs/polban.png"
                        canvas.before:
                            PushMatrix
                            Rotate:
                                angle: 180
                                axis: 0,0,1
                                origin: self.center
                        canvas.after:
                            PopMatrix
        Layout3D:
            id: par
            look_at: [0, -1, 15, 0, 2, -20, 0, 1, 0]
            canvas_size: (1366, 768)
            size: 500,360
            pos: 800,400
            shadow: False
            Node:
                id: backStudio2
                name: 'backStudio'
                rotate: (-90, 0, 1, 0)
                scale: (0.5, 0.5, 0.5)
                translate: (0, -10, 100)
                receive_shadows : False
                meshes : ("./data/objJadi/backStudio2.obj",)
            Node:
                id: floorStudio2
                name: 'floorStudio'
                rotate: (-90, 0, 1, 0)
                scale: (0.5, 0.5, 0.5)
                translate: (0, -10, 100)
                receive_shadows : False
                meshes : ("./data/objJadi/floorStudio2.obj",)
            Node:
                id: artefactStudio2
                name: 'artefactStudio'
                rotate: (-90, 0, 1, 0)
                scale: (0.5, 0.5, 0.5)
                translate: (0, -10, 100)
                receive_shadows : False
                meshes : ("./data/objJadi/artefactStudio2.obj",)
            Node:
                id: papanStudio2
                name: 'papanStudio'
                rotate: (-90, 0, 1, 0)
                scale: (0.5, 0.5, 0.5)
                translate: (0, -10, 100)
                receive_shadows : False
                meshes : ("./data/objJadi/papanStudio2.obj",)
                FloatLayout:
                    Button:
                        id: papanButton
                        disabled: True
                        background_disabled_normal : ("./data/imgs/papanStudio2.png")
                    Image:
                        size_hint: .9, .9
                        pos_hint:{"x": 0.05, "y":0.05}
                        allow_stretch: True
                        source: "./data/imgs/polban.png"
                        canvas.before:
                            PushMatrix
                            Rotate:
                                angle: 180
                                axis: 0,0,1
                                origin: self.center
                        canvas.after:
                            PopMatrix

            Node:
                id: cameraStudio2
                name: 'cameraStudio'
                rotate: (-90, 0, 1, 0)
                scale: (0.5, 0.5, 0.5)
                translate: (0, -10, 100)
                receive_shadows : False
                meshes : ("./data/objJadi/cameraStudio2.obj",)
                FloatLayout:
                    Button:
                        id: cameraButton
                        disabled: True
                        background_disabled_normal : ("./data/imgs/cameraStudio2.png")


            Node:
                id: mejaStudio2
                name: 'mejaStudio2'
                rotate: (-90, 0, 1, 0)
                scale: (0.5, 0.5, 0.5)
                translate: (0, -10, 100)
                receive_shadows : False
                meshes : ("./data/objJadi/mejaStudio2.obj",)
                FloatLayout:
                    Button:
                        id: mejaButton
                        disabled: True
                        background_disabled_normal : ("./data/imgs/mejaStudio2.png")
                    Image:
                        size_hint: 0.7, 0.7
                        pos_hint:{"x": 0.15, "y":0.1}
                        allow_stretch: True
                        source: "./data/imgs/polban.png"
                        canvas.before:
                            PushMatrix
                            Rotate:
                                angle: 180
                                axis: 0,0,1
                                origin: self.center
                        canvas.after:
                            PopMatrix
        KivyCamera:
            id: qrcam
            size: 300,360
            pos: 300,360
            allow_stretch: True

<MainScreen>:
    widgets :widgets
    qrcam: qrcam
    FrontEnd:
        id: frontend
        canvas:
            Color:
                rgba: 0.55, 0.55, 0.55, 1

            Rectangle:
                pos: 0, 0
                size: 127, 764
            # Tools Button Container (Bottom)
            Rectangle:
                pos: 127, 40
                size: 739, 130

            Rectangle:
                pos: 0, 764
                size: 1550, 40

            Rectangle:
                pos: 127, 724
                size: 247, 40

             # Tab 2 (Secondary Display) Tombol Start
            Rectangle:
                pos: 906, 724
                size: 247, 40

            # Tab 3 (Attachment)
            Rectangle:
                pos: 906, 285
                size: 247, 40

            ## Dark
            Color:
                rgba: 0.32, 0.32, 0.32, 1
            # Tab 1 (Main Display)
            Rectangle:
                pos: 374, 724
                size: 532, 40

            # Tab 2 (Secondary Display)
            Rectangle:
                pos: 1153, 724
                size: 600, 40

            # Tab 3 (Attachment)
            Rectangle:
                pos: 1153, 285
                size: 382, 39

            # Middle (Display Divider)
            Rectangle:
                pos: 866, 0
                size: 40, 724

            # Bottom
            Rectangle:
                pos: 127, 0
                size: 1423, 40

            ## Border
            Color:
                rgba: 0.44, 0.44, 0.44, 1

            # Left Container
            Line:
                width: 1
                rectangle: 0, 0, 127, 764

            # Top
            Line:
                width: 1
                rectangle: self.x, 765, self.width, self.height

            Color:
                rgba: 0.23, 0.23, 0.23, 1

            # Tab 1 (Main Display)
            Line:
                width: 1
                rectangle: 128, 724, 247, 40

            # Tab 2 (Secondary Display)
            Line:
                width: 1
                rectangle: 907, 724, 247, 40

            # Tab 3 (Attachment)
            Line:
                width: 1
                rectangle: 907, 285, 247, 40
    Layers:
        id: layers
        size : 685, 500
        pos : 155, 200
    Widgets:
        id: widgets
        FloatLayout:
            # Left Column
            MyButton:
                id: btn1
                pos_hint: {"x":0.13, "top":7.5}
            MyButton:
                id: btn2
                pos_hint: {"x":0.13, "top":6.97}
                text: "Stop"
                on_press : root.stopVideo()

            MyButton:
                id: btn3
                pos_hint: {"x":0.13, "top":6.44}
                text:"Start"
                on_press : root.startVideo()

            MyButton:
                id: btn4
                pos_hint: {"x":0.13, "top":5.91}
                text: "Pause"
                on_press: root.pauseVideo()

            MyButton:
                id: btn5
                pos_hint: {"x":0.13, "top":5.38}

            MyButton:
                id: btn6
                pos_hint: {"x":0.13, "top":4.85}

            MyButton:
                id: btn7
                pos_hint: {"x":0.13, "top":4.32}

            MyButton:
                id: btn8
                pos_hint: {"x":0.13, "top":3.79}

            # Right Column
            MyButton:
                id: btn9
                pos_hint: {"x":0.67, "top":7.5}

            MyButton:
                id: btn10
                pos_hint: {"x": 0.67, "top": 6.97}

            MyButton:
                id: btn11
                pos_hint: {"x": 0.67, "top": 6.44}

            MyButton:
                id: btn12
                pos_hint: {"x": 0.67, "top": 5.91}

            MyButton:
                id: btn13
                pos_hint: {"x": 0.67, "top": 5.38}

            MyButton:
                id: btn14
                pos_hint: {"x": 0.67, "top": 4.85}

            MyButton:
                id: btn15
                pos_hint: {"x": 0.67, "top": 4.32}

            MyButton:
                id: btn16
                pos_hint: {"x": 0.67, "top": 3.79}
                text: "Clear"
                on_press: root.clearCanvas()

            MyButton:
                id: record
                size_hint: None, None
                size: 150, 39
                text: "Start"
                pos_hint:{"x":9.5, "top": 7.63}
                values: 1
                on_press:
                    root.Record(self.values)

            MyButton:
                id: animasi1
                size_hint: None, None
                size: 150, 39
                text: "Animasi 1"
                pos_hint:{"x":6.5, "top": 1.63}
                on_press:
                    root.AnimationRoot()
            MyButton:
                id: animasi2
                size_hint: None, None
                size: 150, 39
                text: "Animasi 2"
                pos_hint:{"x":6.5, "top": 1.20}
                on_press:
                    root.AnimationRoot2()

            BoxLayout:
                orientation: 'vertical'
                size_hint: None, None
                size: 600, 230
                pos_hint:{'center_x':12.25, 'top': 2.9}
                FileChooserListView:
                    id:filechooser
                    on_selection: root.selectFile(filechooser.selection)

            Spinner:
                    # Assigning id
                id: spinner_id
                    # Callback
                on_text: root.spinner_clicked(spinner_id.text)
                background_normal: ''
                background_color: 0.1, 0.5, 0.6, 1
                    # initially text on spinner
                text: "Layer 1"
                on_release:
                    self.background_color= 0.1, 0.5, 0.6, 1
                    # total values on spinner
                values: ["Layer 1", "Layer 2"]
                    # declaring size of the spinner
                    # and the position of it
                size_hint: None, None
                size: 200, 40
                pos_hint:{'center_x':10.25, 'top': 3.26}


    TestingPlish:
        id: par
        look_at: [0, -1, 15, 0, 2, -20, 0, 1, 0]
        canvas_size: (1366, 768)
        size_hint: 0.405, 0.48
        pos: 910, 330
        post_processing: False
        shadow: False
        canvas.before:
            Color:
                rgb: 1, 0.2, 1,1
            Rectangle:
                size: self.size
                pos: self.pos
                source: "./data/imgs/background.jpg"
        Node:
            id: backStudio
            name: 'backStudio'
            rotate: (-90, 0, 1, 0)
            scale: (0.5, 0.5, 0.5)
            translate: (0, -10, -80)
            receive_shadows : False

        Node:
            id: floorStudio
            name: 'floorStudio'
            rotate: (-90, 0, 1, 0)
            scale: (0.5, 0.5, 0.5)
            translate: (0, -10, -80)
            receive_shadows : False

        Node:
            id: artefactStudio
            name: 'artefactStudio'
            rotate: (-90, 0, 1, 0)
            scale: (0.5, 0.5, 0.5)
            translate: (0, -10, -80)
            receive_shadows : False

        Node:
            id: papanStudio
            name: 'papanStudio'
            rotate: (-90, 0, 1, 0)
            scale: (0.5, 0.5, 0.5)
            translate: (0, -10, -80)
            receive_shadows : False
            FloatLayout:
                Button:
                    id: papanButton
                    disabled: True

                LayersImage:
                    id: layersImage
                    size_hint: 1, 1
                    pos_hint:{"x": 0, "y":0}
                    allow_stretch: True
                    canvas.before:
                        PushMatrix
                        Rotate:
                            angle: 180
                            axis: 0,0,1
                            origin: self.center
                    canvas.after:
                        PopMatrix

        Node:
            id: cameraStudio
            name: 'cameraStudio'
            rotate: (-90, 0, 1, 0)
            scale: (0.5, 0.5, 0.5)
            translate: (0, -10, -80)
            receive_shadows : False
            FloatLayout:
                Button:
                    id: cameraButton
                    disabled : True
                KivyCamera:
                    id: qrcam
                    size_hint: .6, .6
                    pos_hint:{"x": 0.2, "y":0.2}
                    allow_stretch: True
                    canvas.before:
                        PushMatrix
                        Rotate:
                            angle: 180
                            axis: 0,0,1
                            origin: self.center
                    canvas.after:
                        PopMatrix

        Node:
            id: mejaStudio
            name: 'mejaStudio'
            rotate: (-90, 0, 1, 0)
            scale: (0.5, 0.5, 0.5)
            translate: (0, -10, -80)
            receive_shadows : False

            FloatLayout:
                Button:
                    id: mejaButton
                    disabled: True
                    background_disabled_normal: ("./data/imgs/mejaStudio1.png")

                Image:
                    size_hint: 0.7, 0.7
                    pos_hint:{"x": 0.15, "y":0.1}
                    allow_stretch: True
                    source: "./data/imgs/polban.png"
                    canvas.before:
                        PushMatrix
                        Rotate:
                            angle: 180
                            axis: 0,0,1
                            origin: self.center
                    canvas.after:
                        PopMatrix

<CheckScreen>:
    FrontEnd2:
        canvas:
            Color:
                rgba: 0.44, 0.44, 0.44, 1
            Line:
                width: 3
                rectangle: 408, 280, 312, 50
            Line:
                width: 3
                rectangle: 812, 280, 312, 50
    Widgets2:
        Button:
            id: detectCamera
            background_normal: 'assets/camerabordered2.png'
            size_hint: .18, .28
            pos_hint: {"x": 0.5, "y": 0.4}
            pos: 405, 350
            size: 317, 277
            on_press:
                root.detectCamera()
        Button:
            id: detectPentab
            background_normal: 'assets/pentabbordered2.png'
            size_hint: .18, .28
            pos_hint: {"x": 0.5, "y": 0.4}
            pos: 810, 350
            size: 317, 277
            on_press:
                root.detectPentab()
        Button:
            id: nextScreen
            disabled: True
            size_hint: .18, .28
            pos_hint: {"x": 0.5, "y": 0.4}
            pos: 650, 150
            size: 200,75
            font_size: 25
            text: "Next Screen"
            on_press:
                root.check()
        Image:
            id: imgCheckCamera
            source: 'assets/cross.png'
            size_hint: .18, .28
            pos: 492, 348
            size: 142, 60
        Image:
            id: imgCheckPentab
            source: 'assets/cross.png'
            size_hint: .18, .28
            pos: 897, 348
            size: 142, 60
        Label:
            text: 'Detect Camera'
            italic: True
            font_size: 28
            pos: 514, 257
        Label:
            text: 'Detect Pentab'
            italic: True
            font_size: 28
            pos: 919, 257
''')


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
        texture = self.texture
        w, h = img.shape[1], img.shape[0]
        scale_percent = 100
        width = int(w * scale_percent / 100)
        height = int(h * scale_percent / 100)
        dim = (width, height)

        resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        if not texture or texture.width != w or texture.height != h:
            self.texture = texture = Texture.create(size=(width, height))
            texture.flip_vertical()
        texture.blit_buffer(resized.tobytes(), colorfmt='bgr')
        self.canvas.ask_update()

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
            texture = self.texture
            w, h = frame.shape[1], frame.shape[0]
            scale_percent = 100
            width = int(w*scale_percent/100)
            height = int(h*scale_percent/100)
            dim = (width, height)

            resized = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
            if not texture or texture.width != w or texture.height != h:
                self.texture = texture = Texture.create(size=(width, height), colorfmt='bgr')
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
        # elif values == 3 :
        #     if self.layer3 != None:
        #         self.changeBackground(self.layer3)

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

            # else: self.layerUtama = 3
        elif self.layerUtama == 2:
            print("LAYER 2")
            # img = ImageGrab.grab(bbox=((200, 155, 1050, 774)))
            # img = img.save(self.temp2)
            # imgtemp = Image(source=self.temp2)
            # imgtemp.reload()
            # self.layer2 = self.temp2
            self.layer2 = self.temp2
            if values == 1 :
                self.layerUtama = 1
            # if str(values) == "Layer 1":
            #     self.layerUtama = 1
            # else: self.layerUtama = 3

        elif self.layerUtama == 3 :
            print("LAYER 3")
            img = ImageGrab.grab(bbox=((200, 155, 1050, 774)))
            img = img.save(self.temp3)
            imgtemp = Image(source=self.temp3)
            imgtemp.reload()
            self.layer3 = self.temp3
            if str(values) == "Layer 1":
                self.layerUtama = 1
            else: self.layerUtama = 2
        print(self.layerUtama)
        self.canvas.clear()
        self.start(self.layerUtama)

class TestingPlish(Layout3D):
    def start(self):
        self.statusRecord = False
        self.texture = []

    def Recording(self):
        self.event = Clock.schedule_interval(self.update, 1.0/30)
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.out = cv2.VideoWriter('temp/temp.mp4', fourcc, 9.0, (1280, 720))
        self.statusRecord = True

    def stopRecording(self):
        Clock.unschedule(self.event)
        print("Stop Recording")
        self.out.release()
        self.statusRecord = False


    def update(self, dt):
        img = ImageGrab.grab(bbox=((1135, 135, 1918, 619)))
        # img = self.export_as_image().
        img = np.array(img)
        # texture = Texture.create(size = self.size, colorfmt=)
        # img = Image(texture)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (1280, 720))
        if self.statusRecord == True:
            self.out.write(img)

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
        self.ids.par.start()

        #DISPLAY CAMERA
        self.ids.qrcam.start( red, green, blue)
        self.ids.qrcam.changeBackground(self.studio)

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
        else :
            self.valueLayers = 1
            self.ids.filechooser.path = os.path.abspath('tempFile/tempImage')
        self.ids.layers.changeLayer(self.valueLayers)

    def cekCamera(self, value):
        self.ids.par.start()
        # img = ImageGrab.grab(bbox=((1135, 135, 1918, 619)))
        # img = img.save("testing.jpg")

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
            self.ids.par.Recording()
        else:
            self.ids.record.text = "Start"
            self.ids.record.values = 1
            self.audio.stop_recording()
            while self.statusRecordAudio != False :
                self.statusRecordAudio = self.audio.getStatus()
                time.sleep(0.5)
                if self.statusRecordAudio == False:
                    self.ids.par.stopRecording()
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
            self.start(self.redValue, self.greenValue, self.blueValue, self.studio)

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
            # self.ids.backStudio.meshes = ("./data/objJadi/backStudio2.obj",)
            # self.ids.floorStudio.meshes = ("./data/objJadi/floorStudio2.obj",)
            # self.ids.artefactStudio.meshes = ("./data/objJadi/artefactStudio2.obj",)
            # self.ids.papanStudio.meshes = ("./data/objJadi/papanStudio2.obj",)
            # self.ids.papanButton.background_disabled_normal = ("./data/imgs/papanStudio2.png")
            # self.ids.cameraStudio.meshes = ("./data/objJadi/cameraStudio2.obj",)
            # self.ids.cameraButton.background_disabled_normal = ("./data/imgs/cameraStudio2.png")
            # self.ids.mejaStudio.meshes = ("./data/objJadi/mejaStudio2.obj",)
            # self.ids.mejaButton.background_disabled_normal = ("./data/imgs/mejaStudio2.png")
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
    #
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

def resourcePath():
    '''Returns path containing content - either locally or in pyinstaller tmp file'''
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS)
    return os.path.join(os.path.abspath("."))

print(resourcePath())

# def resource_path(relative_path):
#     """ Get absolute path to resource, works for dev and for PyInstaller """
#     try:
#         # PyInstaller creates a temp folder and stores path in _MEIPASS
#         base_path = sys._MEIPASS
#     except Exception:
#         base_path = os.path.abspath(".")
#
#     return os.path.join(base_path, relative_path)

if __name__=="__main__":
    kivy.resources.resource_add_path(resourcePath())
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