#!/usr/bin/env python
import os


os.system("cp fp.py /usr/bin/fp")
os.system("cp ende2.py /usr/bin/ende2.py")
os.system("chmod '755' /usr/bin/fp")
os.system("chmod '755' /usr/bin/ende2.py")
os.system("cp fp.glade /usr/share/linuxcnc/fp.glade")
os.system("cp linuxcnc.gif /usr/share/linuxcnc/emc2.gif")
os.system("cp BE_Logo_RGB_Name_klein.PNG /usr/share/linuxcnc/BE_Logo_RGB_Name_klein.PNG")
os.system("cp BE_Logo_RGB_Icon_klein.PNG /usr/share/linuxcnc/BE_Logo_RGB_Icon_klein.PNG")
os.system("cp M104 /usr/bin/M104")
os.system("chmod '755' /usr/bin/M104")
