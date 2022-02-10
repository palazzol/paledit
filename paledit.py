# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 22:16:21 2022

@author: frank
"""

import json

from time import strftime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import FadeTransition, ScreenManager, Screen
from kivy.graphics import *
from kivy.core.window import Window

input_filename = 'stock_with_monitor_connected_20220131-154219_reduced.json'

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
            App.get_running_app().root.controls.UpdatePageLabel(self.colorcode)

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
            colorcode = App.get_running_app().root.colorcode
            App.get_running_app().root.controls.UpdatePageLabel(colorcode)
            

class ControlsScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(ControlsScreen, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.cols = 1

        self.export = Button(text = 'Export Palette', size_hint=(1, 0.5))
        self.export.bind(on_press = self.ExportPalette)
        self.add_widget(self.export)

        self.mode = ToggleButton(text = 'Show All Colors', size_hint=(1, 0.5))
        self.mode.bind(on_press = self.AllColors)
        self.add_widget(self.mode)

        self.box = BoxLayout(size_hint=(1, 0.5))
        self.add_widget(self.box)

        self.filt4 = ToggleButton(text='robby')
        self.filt4.bind(on_press = self.FilterRobby)
        self.box.add_widget(self.filt4)

        self.filt3 = ToggleButton(text='wow')
        self.filt3.bind(on_press = self.FilterWow)
        self.box.add_widget(self.filt3)

        self.filt1 = ToggleButton(text='gorf')
        self.filt1.bind(on_press = self.FilterGorf)
        self.box.add_widget(self.filt1)

        self.filt2 = ToggleButton(text='gorfpgm1')
        self.filt2.bind(on_press = self.FilterGorfPgm1)
        self.box.add_widget(self.filt2)

        self.page = Label()
        self.add_widget(self.page)
        self.UpdatePageLabel(0)

        self.box2 = BoxLayout(size_hint=(1, 0.5))
        self.add_widget(self.box2)
        
        self.prev = Button(text='Previous\nGroup')
        self.prev.bind(on_press = self.PrevColor)
        self.box2.add_widget(self.prev)
        self.next = Button(text='Next\nGroup')
        self.next.bind(on_press = self.NextColor)
        self.box2.add_widget(self.next)

        self.blacklevellabel = Label(size_hint=(1, 0.5))
        self.UpdateBlackLevelLabel(0.0)
        self.add_widget(self.blacklevellabel)
        self.blacklevel = Slider(min = -2.5, max = 2.5, size_hint=(1, 0.5))
        self.blacklevel.bind(value = self.UpdateBlackLevel)
        self.add_widget(self.blacklevel)

        self.box3 = BoxLayout(size_hint=(1, 0.5))
        self.add_widget(self.box3)

        #self.color0 = ToggleButton(text='Black=\nColor 0', group="mode")
        #self.color0.bind(on_press = self.UseColor0)
        #self.box3.add_widget(self.color0)

        self.sync = ToggleButton(text='AC Coupled', group="mode")
        self.sync.bind(on_press = self.UseSyncLevels)
        self.box3.add_widget(self.sync)

        self.zero = ToggleButton(text='DC Coupled', group="mode", state="down")
        self.zero.bind(on_press = self.UseZeroVolts)
        self.box3.add_widget(self.zero)

        self.whitelevellabel = Label(size_hint=(1, 0.5))
        self.UpdateWhiteLevelLabel(5.0)
        self.add_widget(self.whitelevellabel)
        self.whitelevel = Slider(min = 0.0, max = 5.0, value = 5.0, size_hint=(1, 0.5))
        self.whitelevel.bind(value = self.UpdateWhiteLevel)
        self.add_widget(self.whitelevel)       

        self.redgainlabel = Label(size_hint=(1, 0.5))
        self.UpdateRedGainLabel(1.0)
        self.add_widget(self.redgainlabel)
        self.redgain = Slider(min = 0.0, max = 2.0, value = 1.0, size_hint=(1, 0.5))
        self.redgain.bind(value = self.UpdateRedGain)
        self.add_widget(self.redgain)    

        self.greengainlabel = Label(size_hint=(1, 0.5))
        self.UpdateGreenGainLabel(1.0)
        self.add_widget(self.greengainlabel)
        self.greengain = Slider(min = 0.0, max = 2.0, value = 1.0, size_hint=(1, 0.5))
        self.greengain.bind(value = self.UpdateGreenGain)
        self.add_widget(self.greengain)      

        self.bluegainlabel = Label(valign='bottom', size_hint=(1, 0.5))
        self.UpdateBlueGainLabel(1.0)
        self.add_widget(self.bluegainlabel)
        self.bluegain = Slider(min = 0.0, max = 2.0, value = 1.0, size_hint=(1, 0.5))
        self.bluegain.bind(value = self.UpdateBlueGain)
        self.add_widget(self.bluegain)   

    def UpdatePageLabel(self, colorcode):
        if App.get_running_app().root:
            s = ''
            for i in range(0,4):
                R,G,B = App.get_running_app().root.CalculateColor(colorcode+i)
                s = s + '0x{:02X}: {:1.2f}-{:1.2f}-{:1.2f}'.format(colorcode+i,R,G,B)
                R,G,B = App.get_running_app().root.CalculateColor(colorcode+i+4)
                s = s + '    0x{:02X}: {:1.2f}-{:1.2f}-{:1.2f}'.format(colorcode+i+4,R,G,B)
                if i<3:
                    s = s + '\n'
            self.page.text = s

    def UpdateBlackLevelLabel(self, level):
        self.blacklevellabel.text = 'Black Level Adj.: {:.3f}'.format(level)

    def UpdateWhiteLevelLabel(self, level):
        self.whitelevellabel.text = 'White Level: {:.3f}'.format(level)

    def UpdateRedGainLabel(self, level):
        self.redgainlabel.text = 'Red Gain: {:.3f}'.format(level)

    def UpdateGreenGainLabel(self, level):
        self.greengainlabel.text = 'Green Gain: {:.3f}'.format(level)

    def UpdateBlueGainLabel(self, level):
        self.bluegainlabel.text = 'Blue Gain: {:.3f}'.format(level)

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

    def UseZeroVolts(self, w):
        if w.state == "down":
            self.parent.UseZeroVolts(True)
        else:
            self.parent.UseZeroVolts(False)

    def UseColor0(self, w):
        if w.state == "down":
            self.parent.UseColor0(True)
        else:
            self.parent.UseColor0(False)

    def FilterGorf(self, w):
        self.parent.FilterGorf(w.state == "down")

    def FilterGorfPgm1(self, w):
        self.parent.FilterGorfPgm1(w.state == "down")

    def FilterWow(self, w):
        self.parent.FilterWow(w.state == "down")

    def FilterRobby(self, w):
        self.parent.FilterRobby(w.state == "down")

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

    def UpdateRedGain(self, w, level):
        redgain = w.value
        self.UpdateRedGainLabel(redgain)
        App.get_running_app().root.redgain = redgain
        App.get_running_app().root.UpdateColors()

    def UpdateGreenGain(self, w, level):
        greengain = w.value
        self.UpdateGreenGainLabel(greengain)
        App.get_running_app().root.greengain = greengain
        App.get_running_app().root.UpdateColors()

    def UpdateBlueGain(self, w, level):
        bluegain = w.value
        self.UpdateBlueGainLabel(bluegain)
        App.get_running_app().root.bluegain = bluegain
        App.get_running_app().root.UpdateColors()

    def ExportPalette(self, w):
        if App.get_running_app().root:
            App.get_running_app().root.ExportPalette()

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

        with open(input_filename,'r') as f:
            self.colordata = json.load(f)
        self.colorcode = 0
        self.blacklevel = 0.0
        self.whitelevel = 5.0
        self.redgain = 1.0
        self.greengain = 1.0
        self.bluegain = 1.0
        self.filtergorf = False
        self.filtergorfpgm1 = False
        self.filterwow = False
        self.filterrobby = False
        self.MODE_USE_SYNC_LEVELS = 0
        self.MODE_USE_COLOR_0 = 1
        self.MODE_USE_ZERO_VOLTS = 2
        self.mode = self.MODE_USE_ZERO_VOLTS

        """
        self.usedcolors = [0x00, # gorf     title - space black? unused?
                                 # gorfpgm1 title - space black? unused?
                                 # wow
                                 # robby
                           0x04, # gorf     title, laser/galax, warp, flag - gray stars?
                           0x06, # gorfpgm1 title, laser/galax, warp, flag - brighter gray stars?
                           0x07, # gorf     astro - white shield
                                 # gorfpgm1 astro - white shield
                           0x09, # wow
                           0x3A, # gorfpgm1 astro bottom row aliens - red/purple?
                           0x4A, # gorf     title, laser/galax - gorf body red?
                           0x4B, # gorf     warp - red (lighter?) - explosion
                           0x51, # wow
                           0x52, # robby
                           0x53, # gorf     astro - orange
                                 # gorfpgm1 astro, warp - astro bottom red, warp explosion
                           0x54, # gorf     flag - light orange
                                 # gorfpgm1 title, laser/galax, flag - gorf body light orange?
                           0x56, # wow
                           0x65, # gorf     astro - orange/yellow??
                                 # gorfpgm1 astro - orange/yellow??
                           0x75, # gorf     title crawl, laser/galax, warp, flag - yellow text, gorf eyes?
                                 # gorfpgm1 title crawl, laser/galax, warp, flag - yellow text, gorf eyes?
                           0x7c, # wow
                           0x7e, # robby
                           0x9e, # wow
                           0xA4, # gorf     astro - green
                                 # gorfpgm1 astro - green
                           0xc7, # wow
                           0xDB, # gorf     astro - sky - blue
                                 # gorfpgm1 astro - sky - blue
                           0xf3, # wow
                           0xfa, # robby
                           0xFC, # gorf     title, laser/galax, warp, flag - gorf blue? feet, pupils?
                                 # gorfpgm1 title, laser/galax, warp, flag - gorf blue? feet, pupils?
        ]
        """

        self.UpdateColors()

    def SetColor(self, colorcode):
        self.sm.get_screen('A').SetColor(colorcode)
        self.sm.get_screen('B').Update()

    def UpdateColors(self):
        if (self.filtergorf or self.filtergorfpgm1 or self.filterwow or self.filterrobby):
            self.usedcolors = []
            if self.filtergorf:
                self.usedcolors.extend([0x00, 0x04, 0x07, 0x4a, 0x4b, 0x53, 0x54, 0x65, 0x75, 0xa4, 0xdb, 0xfc])
            if self.filtergorfpgm1:
                self.usedcolors.extend([0x00, 0x06, 0x07, 0x3a, 0x53, 0x54, 0x65, 0x75, 0xa4, 0xdb, 0xfc])
            if self.filterwow:
                self.usedcolors.extend([0x00, 0x09, 0x51, 0x56, 0x7c, 0x9e, 0xc7, 0xf3])
            if self.filterrobby:
                self.usedcolors.extend([0x00, 0x52, 0x7e, 0xfa])
        else:
            self.usedcolors = list(range(0,256))

        if self.mode == self.MODE_USE_SYNC_LEVELS:
            self.rmin = self.colordata[0]["Rsync"] + self.blacklevel
            self.gmin = self.colordata[0]["Gsync"] + self.blacklevel
            self.bmin = self.colordata[0]["Bsync"] + self.blacklevel
        elif self.mode == self.MODE_USE_COLOR_0:
            self.rmin = self.colordata[0]["R"] + self.blacklevel
            self.gmin = self.colordata[0]["G"] + self.blacklevel
            self.bmin = self.colordata[0]["B"] + self.blacklevel
        else:
            self.rmin = 0.0 + self.blacklevel
            self.gmin = 0.0 + self.blacklevel
            self.bmin = 0.0 + self.blacklevel
        self.rmax = self.colordata[0]["R"] + self.whitelevel
        self.gmax = self.colordata[0]["G"] + self.whitelevel
        self.bmax = self.colordata[0]["B"] + self.whitelevel
        self.sm.get_screen('A').Update()
        self.sm.get_screen('B').Update()
        self.controls.UpdatePageLabel(self.colorcode)

    def CalculateColor(self, colorcode, includeall=False):
        if not includeall:
            if colorcode not in self.usedcolors:
                return (0, 0, 0)
        R = (self.colordata[colorcode]["R"]-self.rmin)/self.rmax*self.redgain
        G = (self.colordata[colorcode]["G"]-self.gmin)/self.gmax*self.greengain
        B = (self.colordata[colorcode]["B"]-self.bmin)/self.bmax*self.bluegain
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
        export_filename = 'trial_palette_' + strftime("%Y%m%d-%H%M%S") + '.txt'
        with open(export_filename,"w") as f:
            f.write('//\n')
            f.write('// Created from: '+input_filename+'\n')
            if self.mode == self.MODE_USE_SYNC_LEVELS:
                f.write('// Black Level referenced to RGB voltages during sync, to adjust for AC coupling in monitor\n')
            elif self.mode == self.MODE_USE_COLOR_0:
                f.write('// Black Level referenced from color 0 (black) level\n')
            else: # self.MODE_USE_ZERO_VOLTS
                f.write('// Black Level referenced to zero volts\n\n')
            f.write('// Black Level = '+str(self.blacklevel)+'\n')
            f.write('// White Level = '+str(self.whitelevel)+'\n')
            f.write('// Red Gain    = '+str(self.redgain)+'\n')
            f.write('// Green Gain  = '+str(self.greengain)+'\n')
            f.write('// Blue Gain   = '+str(self.bluegain)+'\n')
            f.write('// Integer format is ARGB (0xAARRGGBB)\n')
            f.write('//\n')
            f.write('static const rgb_t colors[256] = {\n')
            for i in range(0,32):
                for j in range(0,8):
                    k = i*8+j
                    R, G, B = self.CalculateColor(k, includeall=True)
                    value = 0xff000000 + (int(R*255.0)<<16) + (int(G*255.0)<<8) + int(B*255.0)
                    f.write('0x{:08x}'.format(value))
                    if (i == 31) and (j == 7):
                        pass
                    else:
                        f.write(', ')
                f.write('\n')
            f.write('}\n')
        popup = Popup(title='Info',content=Label(text='File exported to '+ export_filename),
            size_hint=(None, None), size=(400, 100))
        popup.open()

    def UseSyncLevels(self, tf):
        self.mode = self.MODE_USE_SYNC_LEVELS
        self.UpdateColors()

    def UseColor0(self, tf):
        self.mode = self.MODE_USE_COLOR_0
        self.UpdateColors()

    def UseZeroVolts(self, tf):
        self.mode = self.MODE_USE_ZERO_VOLTS
        self.UpdateColors()

    def FilterGorf(self, tf):
        self.filtergorf = tf
        self.UpdateColors()

    def FilterGorfPgm1(self, tf):
        self.filtergorfpgm1 = tf
        self.UpdateColors()

    def FilterWow(self, tf):
        self.filterwow = tf
        self.UpdateColors()

    def FilterRobby(self, tf):
        self.filterrobby = tf
        self.UpdateColors()

class PalEditApp(App):
    def build(self):
        return MainWindow()

if __name__ == '__main__':
    #Window.fullscreen = True
    #Window.maximize()
    PalEditApp().run()