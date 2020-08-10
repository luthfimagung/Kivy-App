import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.core.text import Text
from kivy.config import Config
from kivy.core.text import Label
import time
import cv2
import numpy as np

Window.clearcolor = (0.19, 0.19, 0.19, 1)
Window.maximize()
print(Window.size)

class Widget1(Button):
    pass
#
# class Widget2(ButtonBehavior, Image):
#     pass

class MyWidgets(Widget):
    def callback(self, event):
        print("button pressed")

    # default_font = Config.get('kivy', 'default_font')
    # print(default_font)
    # fonts = ['C:/Users/Luthfi M Agung/Downloads/Compressed/Login_v11/Login_v11/fonts/montserrat/Montserrat-SemiBoldItalic.ttf',
    #          'C:/Users/Luthfi M Agung/Downloads/Compressed/Login_v11/Login_v11/fonts/montserrat/Montserrat-Black.ttf',
    #          'C:/Users/Luthfi M Agung/Downloads/Compressed/Login_v11/Login_v11/fonts/montserrat/Montserrat-SemiBold.ttf']
    # Config.set('kivy', 'default_font', fonts)
    # default_font = Config.get('kivy', 'default_font')
    # print(default_font)
    # pass
    # def btn(self):
    #     show_popup()
    # def build(self):
    #     self.add_widget(Widget1())
    #     self.add_widget(Widget2())
    #     return self

class MyApp(App):
    def build(self):
        # btn = Button(text='a')
        # myWidget = MyWidgets()
        # btn.bind(on_press=myWidget.callback)
        # btn = Button(background_normal='lasso2.png',
        #              background_down='lasso.png',
        #              size_hint=(.18, .28),
        #              pos_hint={"x": 0.5, "y": 0.4}
        #              )
        # btn.bind(on_press=self.callback)
        # return btn

    # def show_popup():
#     show = P()
#
#     popupWindow = Popup(title="Popup Window", content=show, size_hint=(None,None),size=(400,400))
#
#     popupWindow.open()
        return MyWidgets()

if __name__ == "__main__":
    MyApp().run()