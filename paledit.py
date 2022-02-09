# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 22:16:21 2022

@author: frank
"""

import json

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.screenmanager import FadeTransition, ScreenManager, Screen
from kivy.graphics import *
from kivy.core.window import Window

class Canvas8Color(Screen):
    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.color = []
        self.rect = []
        self.colorcode = 0
        # note, must init this here so I can use assignment in canvas with block
        # append does not work in the with block
        self.color = [0] * 8
        self.rect = [0] * 8
        with self.canvas:
            for i in range(0,8):
                self.color[i] = Color()
                if i==0:
                    self.lrect = Rectangle()
                elif i==4:
                    self.rrect = Rectangle()
                self.rect[i] = Rectangle()

    def on_size(self, *args):
        self.Update()

    def Update(self):
        topmargin = self.height/20
        leftmargin = self.height/10
        root = App.get_running_app().root
        if root:
            self.lrect.pos  = (0, 0)
            self.lrect.size = (self.width/2, self.height)
            self.rrect.pos  = (self.width/2, 0)
            self.rrect.size = (self.width/2, self.height)
            for i in range(0,8):
                self.color[i].rgb = root.CalculateColor(self.colorcode+i)
                effective_width = self.width-2*leftmargin
                self.rect[i].pos  = (effective_width/8*i+leftmargin, topmargin)
                self.rect[i].size = (effective_width/8, self.height-topmargin*2)

    def SetColor(self,colorcode):
        self.colorcode = colorcode
        self.Update()

class Canvas256Color(Screen):
    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.color = []
        self.rect = []
        self.colorcode = 0
        # note, must init this here so I can use assignment in canvas with block
        # append does not work in the with block
        self.color = [0] * 256
        self.rect = [0] * 256
        with self.canvas:
            for i in range(256-8,256):
                self.color[i] = Color()
                self.rect[i] = Rectangle()
            for i in range(0,256-8):
                self.color[i] = Color()
                self.rect[i] = Rectangle()

    def on_size(self, *args):
        self.Update()

    def Update(self):
        topmargin = self.height/20
        leftmargin = self.height/10
        root = App.get_running_app().root
        if root:
            for i in range(0,256):
                self.color[i].rgb = root.CalculateColor(i)
                effective_width = self.width-2*leftmargin
                effective_height = self.height-2*topmargin
                row = i//8
                col = i%8
                if col == 0:
                    self.rect[i].pos  = (effective_width/8*col, self.height-(effective_height/32*row+topmargin+effective_height/32))
                    self.rect[i].size = (effective_width/8+leftmargin, effective_height/32)
                    if i >= 256-8:
                        self.rect[i].pos  = (0, 0)
                        self.rect[i].size = (self.width/2, self.height)
                elif col == 4:
                    self.rect[i].pos  = (effective_width/8*col+leftmargin, self.height-(effective_height/32*row+topmargin+effective_height/32))
                    self.rect[i].size = (effective_width/2+leftmargin, effective_height/32)
                    if i >= 256-8:
                        self.rect[i].pos  = (self.width/2, 0)
                        self.rect[i].size = (self.width/2, self.height)
                else:
                    self.rect[i].pos  = (effective_width/8*col+leftmargin, self.height-(effective_height/32*row+topmargin+effective_height/32))
                    self.rect[i].size = (effective_width/8, effective_height/32)

class ControlsScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(ControlsScreen, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.cols = 1
        self.mode = ToggleButton(text = 'Show All Colors')
        self.mode.bind(on_press = self.AllColors)
        self.add_widget(self.mode)
        self.page = Label()
        self.add_widget(self.page)
        self.UpdatePageLabel(0)
        self.prev = Button(text='Previous', size_hint=(1, 0.5))
        self.prev.bind(on_press = self.PrevColor)
        self.add_widget(self.prev)
        self.next = Button(text='Next', size_hint=(1, 0.5))
        self.next.bind(on_press = self.NextColor)
        self.add_widget(self.next)
        self.sync = ToggleButton(text='Use Sync Levels', size_hint=(1, 0.5))
        self.sync.bind(on_press = self.UseSyncLevels)
        self.add_widget(self.sync)
        self.blacklevellabel = Label(size_hint=(1, 0.5))
        self.UpdateBlackLevelLabel(0.0)
        self.add_widget(self.blacklevellabel)
        self.blacklevel = Slider(min = -2.5, max = 2.5)
        self.blacklevel.bind(value = self.UpdateBlackLevel)
        self.add_widget(self.blacklevel)
        self.whitelevellabel = Label(size_hint=(1, 0.5))
        self.UpdateWhiteLevelLabel(5.0)
        self.add_widget(self.whitelevellabel)
        self.whitelevel = Slider(min = 0.0, max = 5.0, value = 5.0)
        self.whitelevel.bind(value = self.UpdateWhiteLevel)
        self.add_widget(self.whitelevel)       

    def UpdatePageLabel(self, colorcode):
        if App.get_running_app().root:
            s = ''
            for i in range(0,8):
                R,G,B = App.get_running_app().root.CalculateColor(colorcode+i)
                s = s + '0x{:02X}: {:1.2f}-{:1.2f}-{:1.2f}'.format(colorcode+i,R,G,B)
                if i<7:
                    s = s + '\n'
            self.page.text = s

    def UpdateBlackLevelLabel(self, level):
        self.blacklevellabel.text = 'Black Level: {:.3f}'.format(level)

    def UpdateWhiteLevelLabel(self, level):
        self.whitelevellabel.text = 'White Level: {:.3f}'.format(level)

    def AllColors(self, w):
        if w.state == "down":
            self.parent.sm.current = 'B'
        else:
            self.parent.sm.current = 'A'

    def UseSyncLevels(self, w):
        if w.state == "down":
            self.parent.UseSyncLevels(True)
        else:
            self.parent.UseSyncLevels(False)

    def PrevColor(self, w):
        colorcode = App.get_running_app().root.colorcode
        colorcode = (colorcode - 8) % 256
        App.get_running_app().root.colorcode = colorcode
        self.parent.SetColor(colorcode)
        self.UpdatePageLabel(colorcode)

    def NextColor(self, w):
        colorcode = App.get_running_app().root.colorcode
        colorcode = (colorcode + 8) % 256
        App.get_running_app().root.colorcode = colorcode
        self.parent.SetColor(colorcode)
        self.UpdatePageLabel(colorcode)

    def UpdateBlackLevel(self, w, level):
        blacklevel = w.value
        self.UpdateBlackLevelLabel(blacklevel)
        App.get_running_app().root.blacklevel = blacklevel
        App.get_running_app().root.UpdateColors()

    def UpdateWhiteLevel(self, w, level):
        whitelevel = w.value
        self.UpdateWhiteLevelLabel(whitelevel)
        App.get_running_app().root.whitelevel = whitelevel
        App.get_running_app().root.UpdateColors()

class MainWindow(BoxLayout):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.controls = ControlsScreen(size_hint=(.2, 1))
        self.add_widget(self.controls)
        self.sm = ScreenManager()
        self.add_widget(self.sm)
        self.sm.add_widget(Canvas8Color(name='A'))
        self.sm.add_widget(Canvas256Color(name='B'))
        self.sm.transition = FadeTransition()

        with open('stock_with_monitor_connected_20220131-154219_reduced.json','r') as f:
            self.colordata = json.load(f)
        self.colorcode = 0
        self.blacklevel = 0.0
        self.whitelevel = 5.0
        self.usesync = False
        self.UpdateColors()

    def SetColor(self, colorcode):
        self.sm.get_screen('A').SetColor(colorcode)
        self.sm.get_screen('B').Update()

    def UpdateColors(self):
        if self.usesync:
            self.rmin = self.colordata[0]["Rsync"] + self.blacklevel
            self.gmin = self.colordata[0]["Gsync"] + self.blacklevel
            self.bmin = self.colordata[0]["Bsync"] + self.blacklevel
        else:
            self.rmin = self.colordata[0]["R"] + self.blacklevel
            self.gmin = self.colordata[0]["G"] + self.blacklevel
            self.bmin = self.colordata[0]["B"] + self.blacklevel
        self.rmax = self.colordata[0]["R"] + self.whitelevel
        self.gmax = self.colordata[0]["G"] + self.whitelevel
        self.bmax = self.colordata[0]["B"] + self.whitelevel
        self.sm.get_screen('A').Update()
        self.sm.get_screen('B').Update()
        self.controls.UpdatePageLabel(self.colorcode)

    def CalculateColor(self, colorcode):
        R = (self.colordata[colorcode]["R"]-self.rmin)/self.rmax
        G = (self.colordata[colorcode]["G"]-self.gmin)/self.gmax
        B = (self.colordata[colorcode]["B"]-self.bmin)/self.bmax
        if R > 1.0:
            R = 1.0
        if G > 1.0:
            G = 1.0
        if B > 1.0:
            B = 1.0    
        if R < 0.0:
            R = 0.0   
        if G < 0.0:
            G = 0.0  
        if B < 0.0:
            B = 0.0
        return (R, G, B) 

    def ExportPalette(self):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        with open(runname+'_'+timestr+'.txt',"w") as f:
            f.write('// Black Level = '+str())
            for i in range(0,8):
                for j in range(0,32):
                    k = i*32+j
                    color = self.CalculateColor(k)

    def UseSyncLevels(self, tf):
        self.usesync = tf
        self.UpdateColors()

class PalEditApp(App):
    def build(self):
        return MainWindow()

if __name__ == '__main__':
    #Window.fullscreen = True
    #Window.maximize()
    PalEditApp().run()