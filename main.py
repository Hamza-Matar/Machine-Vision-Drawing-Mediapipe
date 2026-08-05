from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2 as cv
import numpy as np
import pygame
import win32api
import win32con
import win32gui
import threading
import time
from math import *
import random
import sys
import mediapipe as mp
import tkinter as tk


def flip(pic, flip_code):
    flip_1 = cv.flip(pic, flip_code)
    return flip_1


def hand_track(pic, mpHands, hands, mpdraw, id_=8, max_num=2, min_detection=0.5, min_tracking=0.5, thickness_=3, circle_radius_=3, color_=(0, 0, 255)):
    drawSpec = mpdraw.DrawingSpec(thickness=thickness_, circle_radius=circle_radius_, color=color_)
    frame = pic
    imgRGB = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    cord_all = []
    cord = []
    if results.multi_hand_landmarks:
        for handlandmark in results.multi_hand_landmarks:
            mpdraw.draw_landmarks(frame, handlandmark, mpHands.HAND_CONNECTIONS, drawSpec, drawSpec)
            for id, lm in enumerate(handlandmark.landmark):
                h, w, c = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                cord_all.append([id, [cx, cy], lm.z])
                if id == id_:
                    cord.append([[cx, cy], lm.z])
    return frame, cord_all, cord


class Window_draw(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drawing")
        self.resize(630, 70)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.move(300, 0)
        font = QFont()
        font.setPointSize(11)
        # self.writing_window = Window_writing()
        self.setFont(font)
        self.UiComponents()
        self.running = True
        x = threading.Thread(target=self.__main_loop)
        x.start()
        self.show()

    def UiComponents(self):
        self.pushButton = QPushButton("Canvas", self)
        self.pushButton.setGeometry(0, 0, 70, 70)
        self.pushButton.setCheckable(True)
        self.pushButton.setChecked(False)
        self.pushButton_2 = QPushButton("Eraser", self)
        self.pushButton_2.setGeometry(70, 0, 70, 70)
        self.pushButton_2.setCheckable(True)
        self.pushButton_2.setChecked(False)
        self.pushButton_3 = QPushButton("Clear", self)
        self.pushButton_3.setGeometry(140, 0, 70, 70)
        self.pushButton_3.setCheckable(True)
        self.pushButton_3.setChecked(False)
        self.pushButton_4 = QPushButton("Shape", self)
        self.pushButton_4.setGeometry(210, 0, 70, 70)
        self.pushButton_4.setCheckable(True)
        self.pushButton_4.setChecked(False)
        # self.pushButton_5 = QPushButton("Read", self)
        # self.pushButton_5.setGeometry(560, 0, 70, 70)
        # self.pushButton_5.clicked.connect(self.read)
        self.comboBox = QComboBox(self)
        self.comboBox.setGeometry(420, 0, 140, 35)
        self.comboBox.addItem("Brush")
        # self.comboBox.addItem("Calligraphy_1")
        # self.comboBox.addItem("Calligraphy_2")
        self.comboBox.addItem("Air_brush")
        self.comboBox_2 = QComboBox(self)
        self.comboBox_2.setGeometry(280, 0, 140, 35)
        self.comboBox_2.addItem("Circle")
        self.comboBox_2.addItem("Line")
        self.comboBox_2.addItem("Rectangle")
        self.spinBox = QSpinBox(self)
        self.spinBox.setGeometry(280, 35, 70, 35)
        self.spinBox.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        self.spinBox.setValue(5)
        self.checkBox = QCheckBox("Full", self)
        self.checkBox.setGeometry(350, 35, 70, 35)
        self.spinBox_2 = QSpinBox(self)
        self.spinBox_2.setGeometry(420, 35, 70, 35)
        self.spinBox_2.setValue(5)
        self.spinBox_2.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        self.comboBox.setCurrentIndex(0)
        self.comboBox_2.setCurrentIndex(0)

    def closeEvent(self, event):
        self.running = False
        event.accept()

    def __main_loop(self):
        root = tk.Tk()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()

        capture = cv.VideoCapture(0)
        ptime = 0
        xy_list = []
        blank = np.zeros((width, height, 3), 'uint8')
        x_1 = 0
        y_1 = 0
        x_2 = 0
        y_2 = 0
        selected = False
        pygame.init()
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        # Set window transparency color
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*(255, 0, 128)), 0, win32con.LWA_COLORKEY)

        canvas = pygame.Surface((width, height))
        canvas.fill((255, 0, 128))
        screen.fill((255, 0, 128))
        pygame.display.update()

        mpHands = mp.solutions.hands
        hands = mpHands.Hands(False, 1, 1, 0.5, 0.5)
        mpdraw = mp.solutions.drawing_utils

        first = True
        while self.running:
            Is_true, frame = capture.read()
            flip_frame = flip(frame, 1)
            ctime = time.time()
            fps = 1 / (ctime - ptime)
            ptime = ctime
            cv.putText(flip_frame, f'{int(fps)}', (20, 70), cv.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
            hand_img, hand_all_landmarks, hand_special_landmark = hand_track(flip_frame, mpHands, hands, mpdraw)
            if len(hand_all_landmarks) > 0:
                xy_list.clear()
                for hand_landmark in hand_all_landmarks:
                    xy_list.append(hand_landmark[1])
                index_x, index_y = hand_special_landmark[0][0]
                h, w, c = flip_frame.shape
            is_canvas = self.pushButton.isChecked()
            pen_size = self.spinBox_2.value() * 10
            pen_color = (0, 0, 255)
            pen_type = self.comboBox.currentText()
            is_eraser = self.pushButton_2.isChecked()
            eraser_size = self.spinBox_2.value() * 10
            do_clear = self.pushButton_3.isChecked()
            do_shape = self.pushButton_4.isChecked()
            draw_shape = False
            shape_type = self.comboBox_2.currentText()
            is_filled = self.checkBox.isChecked()
            shape_thickness = self.spinBox.value()

            if len(hand_all_landmarks) > 0:
                xx, yy = hand_special_landmark[0][0]
                thumb_x, thumb_y = hand_all_landmarks[4][1]
                thumb_index_pos = sqrt(((thumb_x - xx) ** 2) + ((thumb_y - yy) ** 2))
                x = int(index_x * (1 / w) * width)
                y = int(index_y * (1 / h) * height)
                if not do_shape:
                    if thumb_index_pos < 25:
                        if not is_eraser:
                            if pen_type == 'Brush':
                                pygame.draw.circle(canvas, pen_color, (x, y), pen_size)
                            if pen_type == 'Air_brush':
                                for i in range(pen_size):
                                    n_r = random.randint(0, pen_size)
                                    n_theta = random.randint(0, 360)
                                    pygame.draw.circle(canvas, pen_color, (x + n_r * cos(radians(n_theta)), y + n_r * sin(radians(n_theta))), 1)
                        if is_eraser:
                            pygame.draw.circle(canvas, (255, 0, 128), (x, y), eraser_size)
                if do_shape:
                    if thumb_index_pos < 25:
                        if not selected:
                            x_1, y_1 = x, y
                            selected = True
                    if thumb_index_pos > 25:
                        if selected:
                            x_2, y_2 = x, y
                            draw_shape = True
                    if draw_shape:
                        if shape_type == 'Circle':
                            _x_average = (x_1 + x_2) / 2
                            _y_average = (y_1 + y_2) / 2
                            _x_square = (x_1 - x_2) ** 2
                            _y_square = (y_1 - y_2) ** 2
                            diameter = sqrt(_x_square + _y_square)
                            radius = diameter / 2
                            if is_filled:
                                pygame.draw.circle(canvas, pen_color, (_x_average, _y_average), radius)
                            if not is_filled:
                                pygame.draw.circle(canvas, pen_color, (_x_average, _y_average), radius, shape_thickness)
                            selected = False
                        if shape_type == 'Line':
                            pygame.draw.line(canvas, pen_color, (x_1, y_1), (x_2, y_2), shape_thickness)
                            selected = False
                        if shape_type == 'Rectangle ':
                            _x_deference = x_1 - x_2
                            _y_deference = y_1 - y_2
                            if is_filled:
                                pygame.draw.rect(canvas, pen_color, (x_1, y_1, _x_deference, _y_deference))
                            if not is_filled:
                                pygame.draw.rect(canvas, pen_color, (x_1, y_1, _x_deference, _y_deference),
                                                 shape_thickness)
                            selected = False
            if is_canvas:
                cv.imshow('Draw_Test', blank)
            if do_clear:
                canvas.fill((255, 0, 128))
                self.pushButton_3.setChecked(False)
            screen.fill((255, 0, 128))
            screen.blit(canvas, (0, 0))
            if len(hand_all_landmarks) > 0:
                cursor_color = (255, 0, 0) if thumb_index_pos < 25 else (0, 255, 0)

                cursor_radius = pen_size if not is_eraser else eraser_size
                cursor_radius = max(5, int(cursor_radius))  # Ensure it doesn't crash if radius is 0

                pygame.draw.circle(screen, cursor_color, (x, y), cursor_radius, 2)

            pygame.display.update()
            cv.imshow('Image', hand_img)
            if first:
                cv.setWindowProperty('Image', cv.WND_PROP_TOPMOST, 1)
                cv.moveWindow('Image', 1900, 900)
            cv.waitKey(1)
        capture.release()
        cv.destroyAllWindows()
        pygame.quit()

App = QApplication(sys.argv)

# create the instance of our Window
window = Window_draw()

# start the app
sys.exit(App.exec())

