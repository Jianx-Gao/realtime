# app 程序的入口
from uis.Gui_app import CvGuiAPP
import sys

app = CvGuiAPP()
status = app.exec_()
sys.exit(status)

