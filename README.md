RPICameraGUI
============

#Rework

I did some rework so the programm can be used with  the new wx-lib (tested version: 3.0.2.0 gtk3 (classic)).
Additionally i added a feature to set awb red and blue gains if awb-mode is set to off.
The original code was written by Bill Grainger.

#Program
Simple graphical interface for taking photos on the Raspberry Pi Camera
Works over ssh.

Written python 2.7 for the Raspberry Pi

#Installation

`
sudo apt-get install -y python-wxgtk2.8 python-wxtools
wget https://github.com/kugelbit/RPICameraGUI
python RPICameraGUI.py
`

Please note if you use ssh you need the -X Option.
for example:
`ssh -X pi@pi-ip-adress`

#Customization
Feel free to adapt the Code for your needs.
Im not a GUI-Designer so the GUI in the code is maybe not optimal for your set up.
Also this is only a little testing tool for me so dont expect to much "code-quality".

just play around with the following offsets (line: 42 to 47): 
`
# screen layout
xoffset= 2
xfilloffset = 70
xcomoffset=170
ybtwoffset=35
ycomchkoffset=50
ycomfilloffset=45
`



