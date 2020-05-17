# copied from the work by https://github.com/kugelbit/RPICameraGUI
# modified to suit my own usage + 7" touch screen
import time
import os
import wx
import subprocess  # needed to run external program raspistill 
from wx.lib.pubsub import pub as Publisher

class ViewerPanel(wx.Panel):
    def __init__(self, parent):
        """set up for playing with images"""
        wx.Panel.__init__(self, parent)

        width, height = wx.DisplaySize()
       
        self.photoMaxSize = height - 200
        self.img = wx.EmptyImage(self.photoMaxSize,self.photoMaxSize)
        self.image_name=""

        # set up for communication between instances of different classes
        Publisher.subscribe(self.updateImages, ("update images"))

        self.layout()

    def fillCS(self):
        """ this draws window to collect all the options for the next image"""
        # screen layout
        xoffset= 2
        xfilloffset = 70
        xcomoffset=170
        ybtwoffset=35
        ycomchkoffset=50
        ycomfilloffset=45

        #image size defaults
        w=1920 
        h=1080

        rotmodes = ['0','90','180','270']
        
        exposuremodes = ['off','auto','night','nightpreview','backlight',
                         'spotlight','sports','snow','beach','verylong','fixedfps','antishake','fireworks']
        
        awbmodes = ['off','auto','sun','cloudshade','tungsten','fluorescent','incandescent','flash','horizon']
        
        ifxmodes = ['none','negative','solarise','whiteboard','blackboard','sketch','denoise','emboss','oilpaint',
                      'hatch','gpen','pastel','watercolour','film','blur']

        wx.StaticText(self.CS, -1, 'Parameters', (xcomoffset,1))

        offset = -1

        # width
        offset = offset + 1
        wx.StaticText(self.CS, -1,'width in pixels' , (xcomoffset,ycomchkoffset + offset*ybtwoffset))
        self.cbw=wx.CheckBox(self.CS, -1, '-w ', (xoffset, ycomchkoffset + offset*ybtwoffset))
        self.scw = wx.SpinCtrl(self.CS, -1, str(w), (xoffset+xfilloffset, ycomfilloffset + offset*ybtwoffset), (60, -1), min=20, max=5000)

        # height
        offset = offset + 1
        wx.StaticText(self.CS, -1,'height in pixels' , (xcomoffset,ycomchkoffset + offset*ybtwoffset))
        self.cbh=wx.CheckBox(self.CS, -1, '-h ', (xoffset, ycomchkoffset + offset*ybtwoffset))
        self.sch = wx.SpinCtrl(self.CS, -1, str(h), (xoffset+xfilloffset, ycomfilloffset+ offset*ybtwoffset), (60, -1), min=20, max=5000)

""" going to use a generated file name based on time
        # filename
        offset = offset + 1
        wx.StaticText(self.CS, -1,'filename for picture' , (xcomoffset,ycomchkoffset + offset*ybtwoffset))
        self.cbo=wx.CheckBox(self.CS, -1, '-o ', (xoffset, ycomchkoffset + offset*ybtwoffset))
        self.oname = wx.TextCtrl(self.CS, pos=(xoffset+xfilloffset,ycomfilloffset+ offset*ybtwoffset),size=(120, -1),value=defaultfilename) # default filename given
        self.cbo.SetValue(True)
"""
        # quality
        offset = offset + 1
        wx.StaticText(self.CS, -1,'quality of jpg' , (xcomoffset,ycomchkoffset + offset*ybtwoffset))
        self.cbq=wx.CheckBox(self.CS, -1, '-q ', (xoffset, ycomchkoffset + offset*ybtwoffset))
        self.scq = wx.SpinCtrl(self.CS, -1, str(75), (xoffset+xfilloffset, ycomfilloffset+ offset*ybtwoffset), (60, -1), min=0, max=100)

        # time delay
        offset = offset + 1
        wx.StaticText(self.CS, -1,'time delay (ms) before' , (xcomoffset,ycomchkoffset + offset*ybtwoffset)) 
        self.cbt=wx.CheckBox(self.CS, -1, '-t ', (xoffset, ycomchkoffset + offset*ybtwoffset))
        self.sct = wx.SpinCtrl(self.CS, -1, str(1000), (xoffset+xfilloffset, ycomfilloffset+ offset*ybtwoffset), (80, -1), min=100, max=100000000)
        self.cbt.SetValue(True)

        # sharpness
        offset = offset + 1
        wx.StaticText(self.CS, -1,'sharpness    -100 - 100' , (xcomoffset,ycomchkoffset + offset*ybtwoffset))
        self.cbsh=wx.CheckBox(self.CS, -1, '-sh', (xoffset, ycomchkoffset + offset*ybtwoffset))
        self.scsh = wx.SpinCtrl(self.CS, -1, str(0), (xoffset+xfilloffset, ycomfilloffset+ offset*ybtwoffset), (60, -1), min=-100, max=100)

        # contrast
        offset = offset + 1
        wx.StaticText(self.CS, -1,'contrast     -100 - 100' , (xcomoffset,ycomchkoffset + offset*ybtwoffset))
        self.cbco=wx.CheckBox(self.CS, -1, '-co ', (xoffset, ycomchkoffset + offset*ybtwoffset))
        self.scco = wx.SpinCtrl(self.CS, -1, str(0), (xoffset+xfilloffset, ycomfilloffset+ offset*ybtwoffset), (60, -1), min=-100, max=100)

        # brightness
        offset = offset + 1
        wx.StaticText(self.CS, -1,'brightness      0 - 100' , (xcomoffset,ycomchkoffset + offset*ybtwoffset))
        self.cbbr=wx.CheckBox(self.CS, -1, '-br ', (xoffset, ycomchkoffset + offset*ybtwoffset))
        self.scbr = wx.SpinCtrl(self.CS, -1, str(0), (xoffset+xfilloffset, ycomfilloffset+ offset*ybtwoffset), (60, -1), min=0, max=100)

        # saturation
        offset = offset + 1
        wx.StaticText(self.CS, -1,'saturation   -100 - 100' , (xcomoffset,ycomchkoffset + offset*ybtwoffset))
        self.cbsa=wx.CheckBox(self.CS, -1, '-sa ', (xoffset, ycomchkoffset + offset*ybtwoffset))
        self.scsa = wx.SpinCtrl(self.CS, -1, str(0), (xoffset+xfilloffset, ycomfilloffset+ offset*ybtwoffset), (60, -1), min=-100, max=100)

        # image rotation
        offset = offset + 1
        wx.StaticText(self.CS, -1,'rotate image' , (xcomoffset,ycomchkoffset + offset*ybtwoffset))
        self.cbrot=wx.CheckBox(self.CS, -1, '-rot ', (xoffset, ycomchkoffset + offset*ybtwoffset))
        self.scrot = wx.ComboBox(self.CS, -1, pos=(xoffset+xfilloffset, ycomfilloffset+ offset*ybtwoffset), size=(90, -1), choices=rotmodes, style=wx.CB_READONLY)

        # exposure mode
        offset = offset + 1
        wx.StaticText(self.CS, -1,'exposure mode' , (xcomoffset,ycomchkoffset + offset*ybtwoffset))
        self.cbex=wx.CheckBox(self.CS, -1, '-ex ', (xoffset, ycomchkoffset + offset*ybtwoffset))
        self.scex = wx.ComboBox(self.CS, -1, pos=(xoffset+xfilloffset, ycomfilloffset+ offset*ybtwoffset), size=(90, -1), choices=exposuremodes, style=wx.CB_READONLY)

        # exposure compensation
        offset = offset + 1
        wx.StaticText(self.CS, -1,'exposure compensation -10 - 10' , (xcomoffset,ycomchkoffset + offset*ybtwoffset))
        self.cbev=wx.CheckBox(self.CS, -1, '-ev ', (xoffset, ycomchkoffset + offset*ybtwoffset))
        self.scev = wx.SpinCtrl(self.CS, -1, str(0), (xoffset+xfilloffset, ycomfilloffset+ offset*ybtwoffset), (60, -1), min=-10, max=10)

        # white balance
        offset = offset + 1
        wx.StaticText(self.CS, -1,'automatic white balance' , (xcomoffset,ycomchkoffset + offset*ybtwoffset))
        self.cbawb=wx.CheckBox(self.CS, -1, '-awb ', (xoffset, ycomchkoffset + offset*ybtwoffset))
        self.scawb = wx.ComboBox(self.CS, -1, pos=(xoffset+xfilloffset, ycomfilloffset+ offset*ybtwoffset), size=(90, -1), choices=awbmodes, style=wx.CB_READONLY)

        # red gain
        offset = offset + 1
        wx.StaticText(self.CS, -1,'red gain if awb-mode=off ' , (xcomoffset,ycomchkoffset + offset*ybtwoffset))
        self.scawbred = wx.SpinCtrlDouble(self, value='0.00', pos=(xoffset+xfilloffset+5, ycomfilloffset+ offset*ybtwoffset+5), size=(60, -1),
            min=-100, max=100, inc=0.25)

        # blue gain
        offset = offset + 1
        wx.StaticText(self.CS, -1,'blue gain if awb-mode=off ' , (xcomoffset,ycomchkoffset + offset*ybtwoffset))
        self.scawbblue = wx.SpinCtrlDouble(self, value='0.00', pos=(xoffset+xfilloffset+5, ycomfilloffset+ offset*ybtwoffset+5), size=(60, -1),
            min=-100, max=100, inc=0.25)

        # image effect
        offset = offset + 1
        wx.StaticText(self.CS, -1,'image effect' , (xcomoffset,ycomchkoffset + offset*ybtwoffset))
        self.cbifx=wx.CheckBox(self.CS, -1, '-ifx ', (xoffset, ycomchkoffset + offset*ybtwoffset))
        self.scifx = wx.ComboBox(self.CS, -1, pos=(xoffset+xfilloffset, ycomfilloffset+ offset*ybtwoffset), size=(90, -1), choices=ifxmodes, style=wx.CB_READONLY)

        # ---take photo---
        offset = offset + 1
        wx.Button(self.CS, 1, 'Take Photo', (30, ycomfilloffset+ offset*ybtwoffset))

        # when happy take a new picture
        self.Bind(wx.EVT_BUTTON, self.TakePic, id=1)
        
    def TakePic(self, event):
        
        global imagefilename
        imagefilename = time.strftime("%Y%m%d-%H%M%S") + ".potshot.jpg"

        # pick up all the settings selected and add to command line to be usd to take a picture
        self.cmdln='raspistill '
        self.cmdln=self.cmdln + '-o "' + imagefilename +'" '
        
        if self.cbw.GetValue() :
            self.cmdln=self.cmdln + '-w ' + str(self.scw.GetValue()) +' '
        if self.cbh.GetValue() :
            self.cmdln=self.cmdln + '-h ' + str(self.sch.GetValue()) +' '
        if self.cbq.GetValue() :
            self.cmdln=self.cmdln + '-q ' + str(self.scq.GetValue())+' '
        if self.cbt.GetValue() :
            self.cmdln=self.cmdln + '-t ' + str(self.sct.GetValue())+' '      
        if self.cbsh.GetValue() :
            self.cmdln=self.cmdln + '-sh ' + str(self.scsh.GetValue())+' '
        if self.cbco.GetValue() :
            self.cmdln=self.cmdln + '-co ' + str(self.scco.GetValue())+' '
        if self.cbbr.GetValue() :
            self.cmdln=self.cmdln + '-br ' + str(self.scbr.GetValue())+' '
        if self.cbsa.GetValue() :
            self.cmdln=self.cmdln + '-sa ' + str(self.scsa.GetValue())+' '
        if self.cbrot.GetValue() :
            self.cmdln=self.cmdln + '-rot ' + str(self.scrot.GetValue())+' '
        if self.cbex.GetValue() :
            self.cmdln=self.cmdln + '-ex ' + str(self.scex.GetValue())+' '
        if self.cbev.GetValue() :
            self.cmdln=self.cmdln + '-ev ' + str(self.scev.GetValue())+' '    
        if self.cbawb.GetValue() :
            mode = str(self.scawb.GetValue())
            self.cmdln=self.cmdln + '-awb ' + mode +' '
            if mode == "off":
                #-awbg 1.5,1.2
                self.cmdln=self.cmdln + '-awbg ' + str(self.scawbred.GetValue()) + ','+ str(self.scawbblue.GetValue()) +' '
        if self.cbifx.GetValue() :
            self.cmdln=self.cmdln + '-ifx ' + str(self.scifx.GetValue())+' '
        
        # call external program ro take a picture
        subprocess.check_call([self.cmdln], shell=True)

        # update image on screen
        Publisher.sendMessage("update images",msg="")

    def layout(self):
        """
        Layout the widgets on the panel
        """
        self.bigsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, 
                                         wx.BitmapFromImage(self.img))
        self.mainSizer.Add(self.imageCtrl, 0, wx.ALL|wx.CENTER, 5)
        self.imageLabel = wx.StaticText(self, label="")
        self.mainSizer.Add(self.imageLabel, 1, wx.ALL, 5)
        
        btnData = [("Rot Clock 90", btnSizer, self.onRotClock),
                   ("Rot Anti-clock 90", btnSizer, self.onRotAclock)]
        
        for data in btnData:
            label, sizer, handler = data
            self.btnBuilder(label, sizer, handler)
            
        self.mainSizer.Add(btnSizer, 1, wx.CENTER)
        self.CS=wx.Panel(self,0, size=(350,1000))
        self.fillCS()
        self.bigsizer.Add(self.CS, 0, wx.ALL,5)
        self.bigsizer.Add(self.mainSizer, 1, wx.ALL,5)
        self.SetSizer(self.bigsizer)

    def btnBuilder(self, label, sizer, handler):
        """
        Builds a button, binds it to an event handler and adds it to a sizer
        """
        btn = wx.Button(self, label=label)
        btn.Bind(wx.EVT_BUTTON, handler)
        sizer.Add(btn, 0, wx.ALL|wx.CENTER, 5)

    def loadImage(self, image):
        """"""
        self.image_name = os.path.basename(image)
        self.img = wx.Image(image, wx.BITMAP_TYPE_ANY)
        self.rescaleImage()

    def rescaleImage(self):
        # scale the image to fit frame, preserving the aspect ratio
        W = self.img.GetWidth()
        H = self.img.GetHeight()
        if W > H:
            NewW = self.photoMaxSize
            NewH = self.photoMaxSize * H / W
        else:
            NewH = self.photoMaxSize
            NewW = self.photoMaxSize * W / H
        self.img = self.img.Scale(NewW,NewH)

        self.imageCtrl.SetBitmap(wx.BitmapFromImage(self.img))
        self.imageLabel.SetLabel(self.cmdln)
        self.Refresh()
        Publisher.sendMessage("resize", msg="")

    def rotPictureClock(self):
        """
        Rotates the current picture clockwise but only does it once BG 12/6/13
        as it does not store teh rotated image
        """
       
        self.img = self.img.Rotate90(True)
        
        # may need to scale the image, preserving the aspect ratio
        self.rescaleImage()

    def rotPictureAclock(self):
        """
        Rotates the current picture anti-clockwise but only does it once BG 12/6/13
        as it does not store teh rotated image
        """
        
        self.img = self.img.Rotate90(False)
        
        # may need to scale the image, preserving the aspect ratio
        self.rescaleImage()

    def updateImages(self,msg):
        self.loadImage(imagefilename)
 
     def onRotClock(self, event):
        """
        Rotates Image clockwise method, note it works on the image not the camera
        """
        self.rotPictureClock()

    def onRotAclock(self, event):
        """
        Rotates Image anti-clockwise method  
        """
        self.rotPictureAclock()

      
class ViewerFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Pot Shots")
        panel = ViewerPanel(self)
        
        Publisher.subscribe(self.resizeFrame, ("resize"))
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        
        self.Show()
        self.sizer.Fit(self)
        self.Center()     
         
    def resizeFrame(self, msg):
        self.sizer.Fit(self)
        

if __name__ == "__main__":
    app = wx.App(False)
    frame = ViewerFrame()
    app.MainLoop()
