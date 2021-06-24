from PyQt5.QtWidgets import QMainWindow, QGraphicsScene, QGraphicsPixmapItem, QFileDialog
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor
from PyQt5 import QtCore, QtWidgets
from PyQt5.Qt import Qt
from uis.Gui import Ui_MainWindow
import numpy as np
import cv2
from PyQt5.QtCore import QTimer
import openpifpaf
import math

def cal_angle(point_1, point_2, point_3):
    a = math.sqrt(
        (point_2[0] - point_3[0]) * (point_2[0] - point_3[0]) + (point_2[1] - point_3[1]) * (point_2[1] - point_3[1]))
    b = math.sqrt(
        (point_1[0] - point_3[0]) * (point_1[0] - point_3[0]) + (point_1[1] - point_3[1]) * (point_1[1] - point_3[1]))
    c = math.sqrt(
        (point_1[0] - point_2[0]) * (point_1[0] - point_2[0]) + (point_1[1] - point_2[1]) * (point_1[1] - point_2[1]))
    # A = math.degrees(math.acos((a * a - b * b - c * c) / (-2 * b * c+0.000001)))
    B = math.degrees(math.acos((b * b - a * a - c * c) / (-2 * a * c+0.0001)))
    # C = math.degrees(math.acos((c * c - a * a - b * b) / (-2 * a * b+0.000001)))
    return B

def get_new_point(hand, arm):
    distance = np.sqrt((arm[0] - hand[0]) ** 2 + (arm[1] - hand[1]) ** 2)
    angle = math.atan2(hand[1] - arm[1], hand[0] - arm[0] + 0.00001)
    start_point = (int(hand[0]-distance*1*math.sin(angle)), int(hand[1]+distance*1*math.cos(angle)))
    end_point = (int(hand[0]+distance*1*math.sin(angle)),int(hand[1]-distance*1*math.cos(angle)))
    angle1 = math.pi/4 - angle
    angle2 = math.pi * 1 / 4 +angle
    p1 = (int(start_point[0]-math.cos(angle1)*distance),int(start_point[1]+math.sin(angle1)*distance))
    p2 = (int(end_point[0]-math.cos(angle2)*distance),int(end_point[1]-math.sin(angle1)*distance))
    return start_point, end_point,p1,p2,angle


color = [
    (230,74,25),
    (255,112,67),
    (255,167,38),
    (255,202,40),
    (212,225,87),
    (102,187,106),
    (0,151,167),
    (38,166,154),
    (38,198,218),
    (66,165,245),
    (106,27,154)
]

class CvGuiFrame(QMainWindow):
    def __init__(self):
        super(CvGuiFrame,self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.timer_camera = QTimer()     #定义定时器
        video = './data/1601428211768.mp4'     #加载视频文件
        self.cap = cv2.VideoCapture(0)
        self.ui.start_btn.clicked.connect(self.slotStart)      # 按钮关联槽函数
        self.ui.stop_btn.clicked.connect(self.slotStop)

    # def open_cap(self):
    #     self.cap = cv2.VideoCapture(0)

    def slotStart(self):
        """ Slot function to start the progamme
        """

        self.timer_camera.start(100)
        self.timer_camera.timeout.connect(self.openFrame)

    def slotStop(self):
        """ Slot function to stop the programme
        """

        self.cap.release()
        self.timer_camera.stop()  # 停止计时器

    def openFrame(self):
        """ Slot function to capture frame and process it
        """

        ret, image = self.cap.read()
        arrow_flag = 0
        arrow_x = 0
        arrow_y = 0
        arrow_angle = 0
        if (self.cap.isOpened()):
            ret, image = self.cap.read()
            if ret:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                # n_image = np.zeros((600, 800, 3))
                n_image = np.ones_like(image)
                # print(frame.shape)
                # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                predictor = openpifpaf.Predictor(checkpoint='shufflenetv2k16')
                predictions, gt_anns, meta = predictor.numpy_image(image)
                for p in range(len(predictions)):
                    # 处理每个人
                    points = predictions[p].data
                    exist_point = []
                    for i in range(len(points)):
                        if int(points[i][0]) <= 0 or int(points[i][1]) <= 0:
                            continue
                        cv2.circle(image, (int(points[i][0]), int(points[i][1])), 4, color[int(i / 2)], -1)
                        exist_point.append(i)
                        # cv2.putText(image, "{}".format(i), (int(points[i][0]), int(points[i][1])),
                        #             cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
                        if i == 12:
                            if 6 in exist_point:
                                cv2.line(image, (int(points[6][0]), int(points[6][1])),
                                         (int(points[12][0]), int(points[12][1])),
                                         color[int(6)], 3)
                            continue
                        if i == 11:
                            if 5 in exist_point:
                                cv2.line(image, (int(points[5][0]), int(points[5][1])),
                                         (int(points[11][0]), int(points[11][1])),
                                         color[int(5)], 3)
                            continue

                        if i - 2 in exist_point:
                            cv2.line(image, (int(points[i - 2][0]), int(points[i - 2][1])),
                                     (int(points[i][0]), int(points[i][1])), color[int(i / 2)], 3)
                    if 0 in exist_point and 1 in exist_point:
                        cv2.line(image, (int(points[0][0]), int(points[0][1])), (int(points[1][0]), int(points[1][1])),
                                 color[int(1)], 3)
                    # Todo: 头
                    if points[0][0] != 0:
                        cv2.ellipse(n_image, (int(points[0][0]), int(points[0][1]) + 10), (40, 50), 0, 0, 360,
                                    (255, 255, 255), -1)
                    # Todo: 脖子
                    if points[5][0] != 0:
                        cv2.rectangle(n_image, (int(points[0][0]) - 10, int(points[0][1]) + 30),
                                      (int(points[0][0]) + 10, int(points[5][1])), (255, 255, 255), -1)
                    # Todo: 身体
                    if points[5][0] != 0 and points[12][0] != 0:
                        cv2.rectangle(n_image, (int(points[5][0]), int(points[5][1])),
                                      (int(points[12][0]), int(points[12][1])), (255, 255, 255), -1)
                    # Todo: 右手
                    if points[9][0] != 0 and points[5][0] != 0:
                        cv2.line(n_image, (int(points[7][0]), int(points[7][1])),
                                 (int(points[5][0]), int(points[5][1])), (255, 255, 255), 5)
                    if points[9][0] != 0 and points[7][0] != 0:
                        cv2.line(n_image, (int(points[7][0]), int(points[7][1])),
                                 (int(points[9][0]), int(points[9][1])), (255, 255, 255), 5)
                    # Todo: 左手
                    if points[8][0] != 0 and points[6][0] != 0:
                        cv2.line(n_image, (int(points[8][0]), int(points[8][1])),
                                 (int(points[6][0]), int(points[6][1])), (255, 255, 255), 5)
                    if points[10][0] != 0 and points[8][0] != 0:
                        cv2.line(n_image, (int(points[8][0]), int(points[8][1])),
                                 (int(points[10][0]), int(points[10][1])), (255, 255, 255), 5)
                    # Todo: 左腿
                    if points[12][0] != 0 and points[14][0] != 0:
                        cv2.line(n_image, (int(points[12][0]), int(points[12][1])),
                                 (int(points[14][0]), int(points[14][1])), (255, 255, 255), 5)
                    if points[14][0] != 0 and points[16][0] != 0:
                        cv2.line(n_image, (int(points[14][0]), int(points[14][1])),
                                 (int(points[16][0]), int(points[16][1])), (255, 255, 255), 5)
                    # Todo: 右腿
                    if points[11][0] != 0 and points[13][0] != 0:
                        cv2.line(n_image, (int(points[11][0]), int(points[11][1])),
                                 (int(points[13][0]), int(points[13][1])),
                                 (255, 255, 255), 5)
                    if points[13][0] != 0 and points[15][0] != 0:
                        cv2.line(n_image, (int(points[13][0]), int(points[13][1])),
                                 (int(points[15][0]), int(points[15][1])),
                                 (255, 255, 255), 5)
                    # Todo: 左开弓
                    left_angle = cal_angle(points[6], points[8], points[10])
                    if left_angle > 165 and points[10][1] < (points[12][1] - 100):
                        start_point, end_point, p1, p2, angle = get_new_point(points[10], points[8])
                        cv2.line(n_image, start_point, end_point, (255, 255, 255), 3)
                        cv2.line(n_image, p1, start_point, (255, 255, 255), 2)
                        cv2.line(n_image, p2, end_point, (255, 255, 255), 2)
                        if points[9][0] <= points[0][0] and points[9][0] != 0:
                            cv2.line(n_image, (int(points[9][0]), int(points[9][1])), p1, (255, 255, 255), 1)
                            cv2.line(n_image, (int(points[9][0]), int(points[9][1])), p2, (255, 255, 255), 1)
                        if points[9][0] - points[5][0] <= 30 and points[9][1] - points[5][1] <= 30:
                            arrow_flag = 1
                            arrow_x = int(points[10][0])
                            arrow_y = int(points[10][1])
                            arrow_angle = angle
                    # Todo: 右开弓
                    right_angle = cal_angle(points[5], points[7], points[9])
                    if right_angle > 165 and points[9][1] < (points[11][1] - 100):
                        start_point, end_point, p1, p2, angle = get_new_point(points[9], points[7])
                        cv2.line(n_image, start_point, end_point, (255, 255, 255), 3)
                        cv2.line(n_image, p1, start_point, (255, 255, 255), 2)
                        cv2.line(n_image, p2, end_point, (255, 255, 255), 2)
                        if points[10][0] >= points[0][0]:
                            cv2.line(n_image, (int(points[10][0]), int(points[10][1])), p1, (255, 255, 255), 1)
                            cv2.line(n_image, (int(points[10][0]), int(points[10][1])), p2, (255, 255, 255), 1)

                if arrow_flag == 1:
                    cv2.line(n_image, (arrow_x, arrow_y),
                             (int(arrow_x + 35 * math.cos(arrow_angle)), int(arrow_y + 35 * math.sin(arrow_angle))),
                             (255, 255, 255), 2)
                    arrow_x = int(arrow_x + 45 * math.cos(arrow_angle))
                    arrow_y = int(arrow_y + 45 * math.sin(arrow_angle))

                fps = self.cap.get(cv2.CAP_PROP_FPS)
                cv2.putText(image, 'fps:{}'.format(fps), (10, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)

                height, width, bytesPerComponent = image.shape
                bytesPerLine = bytesPerComponent * width
                q_image = QImage(image.data, width, height, bytesPerLine,
                                 QImage.Format_RGB888).scaled(self.ui.label.width(), self.ui.label.height())
                self.ui.label.setPixmap(QPixmap.fromImage(q_image))
                n_image = cv2.cvtColor(n_image, cv2.COLOR_BGR2RGB)
                height2, width2 ,bytesPerComponent2= n_image.shape
                bytesPerLine2 = bytesPerComponent2 * width2
                q_image2 = QImage(n_image, width2, height2,bytesPerLine2,
                                  QImage.Format_RGB888).scaled(self.ui.label_2.width(), self.ui.label_2.height())
                self.ui.label_2.setPixmap(QPixmap.fromImage(q_image2))
            else:
                self.cap.release()
                self.timer_camera.stop()  # 停止计时器




