from PyQt5.QtWidgets import QApplication
from uis.Gui_frame import CvGuiFrame

class CvGuiAPP(QApplication):
    def __init__(self):
        super(CvGuiAPP,self).__init__([])
        # app主窗口
        self.main_window = CvGuiFrame()
        self.main_window.show()


