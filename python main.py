import sys
import cv2
import numpy as np
import time
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox, QFileDialog, 
                             QColorDialog, QGroupBox, QGridLayout, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QIcon, QImage, QPixmap
from collections import deque

class VideoProcessor(QThread):
    frame_ready = pyqtSignal(np.ndarray)

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.capture = cv2.VideoCapture(video_path)
        self.frame_rate = self.capture.get(cv2.CAP_PROP_FPS)
        self.delay = int(1000 / self.frame_rate)
        self.paused = False
        self.lower_color = (5, 150, 150)
        self.upper_color = (15, 255, 255)
        self.lower_color_robot = (140, 0, 150)
        self.upper_color_robot = (170, 255, 255)
        self.min_radius = 10
        self.pts_ball = deque(maxlen=64)
        self.pts_robot = deque(maxlen=64)
        self.line_frame = None
        self.line_color_ball = (0, 0, 255)
        self.line_thickness = 2
        self.line_transparency = 1.0
        self.initial_frame = None
        self.start_point_ball = None
        self.stop_flag = False
        self.playback_time = None  # Set initial playback time to None
        self.start_time = None  # Track start time of the playback
        self.elapsed_time = 0

    def run(self):
        while self.capture.isOpened() and not self.stop_flag:
            if not self.paused:
                if self.start_time is None:
                    self.start_time = time.time()  # Initialize start time at the beginning of run

                ret, frame = self.capture.read()
                if not ret:
                    break

                frame = cv2.resize(frame, (640, int(frame.shape[0] * 640 / frame.shape[1])))

                if self.line_frame is None:
                    self.line_frame = np.zeros_like(frame)
                    self.initial_frame = frame.copy()

                blurred = cv2.GaussianBlur(frame, (11, 11), 0)
                hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

                mask_ball = cv2.inRange(hsv, self.lower_color, self.upper_color)
                mask_ball = cv2.erode(mask_ball, None, iterations=2)
                mask_ball = cv2.dilate(mask_ball, None, iterations=2)
                cnts_ball, _ = cv2.findContours(mask_ball.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                center_ball = None

                if len(cnts_ball) > 0:
                    c = max(cnts_ball, key=cv2.contourArea)
                    ((x, y), radius) = cv2.minEnclosingCircle(c)
                    M = cv2.moments(c)
                    center_ball = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                    if radius > self.min_radius:
                        cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                        cv2.circle(frame, center_ball, 5, (0, 165, 255), -1)
                        cv2.putText(frame, "Bola", (int(x) - 10, int(y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 2)

                mask_robot = cv2.inRange(hsv, self.lower_color_robot, self.upper_color_robot)
                mask_robot = cv2.erode(mask_robot, None, iterations=2)
                mask_robot = cv2.dilate(mask_robot, None, iterations=2)
                cnts_robot, _ = cv2.findContours(mask_robot.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                center_robot = None

                if len(cnts_robot) > 0:
                    c = max(cnts_robot, key=cv2.contourArea)
                    ((x, y), radius) = cv2.minEnclosingCircle(c)
                    M = cv2.moments(c)
                    center_robot = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                    if radius > self.min_radius * 2:
                        robot_box = cv2.boundingRect(c)
                        x, y, w, h = robot_box
                        w = int(w * 1)
                        h = int(h * 2)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 2)
                        cv2.putText(frame, "Robot", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)

                self.pts_ball.appendleft(center_ball)
                for i in range(1, len(self.pts_ball)):
                    if self.pts_ball[i - 1] is None or self.pts_ball[i] is None:
                        continue
                    cv2.line(self.line_frame, self.pts_ball[i - 1], self.pts_ball[i], (0, 0, 255), self.line_thickness, lineType=cv2.LINE_AA)

                if len(self.pts_ball) > 1 and self.pts_ball[-1] is not None:
                    if self.start_point_ball is None:
                        self.start_point_ball = self.pts_ball[-1]
                    cv2.putText(frame, "Start", self.start_point_ball, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    cv2.circle(frame, self.start_point_ball, 5, (0, 255, 0), -1)

                self.pts_robot.appendleft(center_robot)
                for i in range(1, len(self.pts_robot)):
                    if self.pts_robot[i - 1] is None or self.pts_robot[i] is None:
                        continue
                    cv2.line(self.line_frame, self.pts_robot[i - 1], self.pts_robot[i], (255, 0, 255), self.line_thickness, lineType=cv2.LINE_AA)

                combined_frame = cv2.addWeighted(frame, 1.0, self.line_frame, self.line_transparency, 0)

                self.frame_ready.emit(combined_frame)

            if self.start_time:
                self.elapsed_time = time.time() - self.start_time  # Elapsed time in seconds
            if self.playback_time is not None and self.elapsed_time >= self.playback_time:
                self.paused = True
                self.start_time = None  # Reset start time when paused

            self.msleep(self.delay)

    def set_color_range(self, lower, upper):
        self.lower_color = lower
        self.upper_color = upper

    def set_robot_color_range(self, lower, upper):
        self.lower_color_robot = lower
        self.upper_color_robot = upper

    def set_min_radius(self, radius):
        self.min_radius = radius

    def set_delay(self, delay):
        self.delay = delay

    def set_line_color_ball(self, color):
        self.line_color_ball = color

    def set_line_thickness(self, thickness):
        self.line_thickness = thickness

    def set_line_transparency(self, transparency):
        self.line_transparency = transparency

    def toggle_pause(self):
        self.paused = not self.paused
        if not self.paused:
            self.start_time = time.time() - self.elapsed_time  # Adjust the start time when resuming

    def reset_video(self):
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.paused = True
        self.line_frame = np.zeros_like(self.initial_frame)
        self.pts_ball.clear()
        self.pts_robot.clear()
        self.start_point_ball = None
        self.elapsed_time = 0  # Reset elapsed time when video is reset
        self.frame_ready.emit(self.initial_frame)
        self.start_time = None  # Reset start time when video is reset

    def set_playback_time(self, time_in_seconds):
        self.playback_time = time_in_seconds
        self.start_time = None  # Ensure start_time is reset when playback time is set

    def release(self):
        self.stop_flag = True
        self.capture.release()

class VideoApp(QWidget):
    def __init__(self):
        super().__init__()

        self.video_processor = None
        self.icon_path = "D:/OneDrive - UGM 365/Work/Project/Rikik/Tracking/Icons/"
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Tracking App 1.0')
        self.resize(800, 500)
        self.setWindowIcon(QIcon(self.icon_path + "app.png"))

        self.main_layout = QVBoxLayout()
        self.video_layout = QVBoxLayout()
        self.control_layout = QVBoxLayout()

        self.header_layout = QHBoxLayout()
        self.logo_label_left = QLabel()
        logo_pixmap_left = QPixmap(self.icon_path + "Fire-X.png")
        if not logo_pixmap_left.isNull():
            self.logo_label_left.setPixmap(logo_pixmap_left.scaled(50, 50, Qt.KeepAspectRatio))
        self.header_layout.addWidget(self.logo_label_left)

        self.header_text = QLabel("FIRE-X Wheeled Soccer Robot")
        self.header_text.setStyleSheet("font-size: 30px; font-weight: bold; color: #ffcc00; margin: 10px;")
        self.header_layout.addWidget(self.header_text, alignment=Qt.AlignCenter)
        self.header_layout.addStretch()
        self.main_layout.addLayout(self.header_layout)

        self.video_label = QLabel()
        self.video_label.setFixedSize(720, 405)
        self.main_layout.addWidget(self.video_label, alignment=Qt.AlignCenter)

        self.initMainControls()
        self.initAdditionalAndSizeControls()

        self.main_layout.addLayout(self.control_layout)
        self.setLayout(self.main_layout)

        self.footer_layout = QHBoxLayout()
        self.footer_text = QLabel("© 2024 Video Processing Application for Tracking")
        self.footer_text.setStyleSheet("font-size: 14px; text-align: left; margin: 5px; color: #ffffff;")
        self.footer_logo = QLabel()
        footer_logo_pixmap = QPixmap(self.icon_path + "Logogram UAD2.png")
        if not footer_logo_pixmap.isNull():
            self.footer_logo.setPixmap(footer_logo_pixmap.scaled(130, 130, Qt.KeepAspectRatio))
        self.footer_layout.addWidget(self.footer_text, alignment=Qt.AlignLeft)
        self.footer_layout.addStretch()
        self.footer_layout.addWidget(self.footer_logo, alignment=Qt.AlignRight)
        self.main_layout.addLayout(self.footer_layout)

        self.setStyleSheet("""
            QWidget {
                font-size: 14px;
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QPushButton {
                background-color: #ffcc00;
                color: black;
                border: none;
                padding: 6px 12px;
                border-radius: 5px;
                margin: 5px;
                min-width: 100px;
                min-height: 40px;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e68a00;
            }
            QPushButton:pressed {
                background-color: #cc7a00;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
            }
            QLabel {
                font-size: 14px;
                color: #ffffff;
            }
            QSpinBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                min-height: 25px;
                min-width: 60px;
            }
        """)

    def initMainControls(self):
        main_controls = QGroupBox("Main Controls")
        main_layout = QGridLayout()

        self.loadButton = QPushButton('Load Video')
        self.loadButton.setIcon(QIcon(self.icon_path + "load.png"))
        self.loadButton.setToolTip("Load a video file")
        self.loadButton.clicked.connect(self.load_video)
        main_layout.addWidget(self.loadButton, 0, 0)

        self.playButton = QPushButton('Play')
        self.playButton.setIcon(QIcon(self.icon_path + "play.png"))
        self.playButton.setToolTip("Play the video")
        self.playButton.clicked.connect(self.play_video)
        main_layout.addWidget(self.playButton, 0, 1)

        self.pauseButton = QPushButton('Pause')
        self.pauseButton.setIcon(QIcon(self.icon_path + "pause.png"))
        self.pauseButton.setToolTip("Pause the video")
        self.pauseButton.clicked.connect(self.pause_video)
        main_layout.addWidget(self.pauseButton, 0, 2)

        self.resetButton = QPushButton('Reset Video')
        self.resetButton.setIcon(QIcon(self.icon_path + "reset.png"))
        self.resetButton.setToolTip("Reset the video to the beginning")
        self.resetButton.clicked.connect(self.reset_video)
        main_layout.addWidget(self.resetButton, 0, 3)

        self.colorPickerBallButton = QPushButton('Pick Ball Color')
        self.colorPickerBallButton.setIcon(QIcon(self.icon_path + "pick_ball.png"))
        self.colorPickerBallButton.setToolTip("Select the color for the ball")
        self.colorPickerBallButton.clicked.connect(self.pick_ball_color)
        main_layout.addWidget(self.colorPickerBallButton, 1, 0, 1, 2)

        self.colorPickerRobotButton = QPushButton('Pick Robot Color')
        self.colorPickerRobotButton.setIcon(QIcon(self.icon_path + "pick_robot.png"))
        self.colorPickerRobotButton.setToolTip("Select the color for the robot")
        self.colorPickerRobotButton.clicked.connect(self.pick_robot_color)
        main_layout.addWidget(self.colorPickerRobotButton, 1, 2, 1, 2)

        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 1)
        main_layout.setColumnStretch(2, 1)
        main_layout.setColumnStretch(3, 1)

        main_controls.setLayout(main_layout)
        self.control_layout.addWidget(main_controls)

    def initAdditionalAndSizeControls(self):
        additional_size_controls = QGroupBox("Additional and Size Controls")
        additional_size_layout = QVBoxLayout()

        additional_controls_layout = QGridLayout()

        self.playbackTimeLabel = QLabel("Playback Time (s):")
        self.playbackTimeInput = QSpinBox()
        self.playbackTimeInput.setRange(1, 3600)
        self.playbackTimeInput.setFixedSize(60, 25)
        self.playbackTimeInput.setValue(10)
        self.playbackTimeInput.valueChanged.connect(self.set_playback_time)
        additional_controls_layout.addWidget(self.playbackTimeLabel, 0, 0, Qt.AlignRight)
        additional_controls_layout.addWidget(self.playbackTimeInput, 0, 1, Qt.AlignLeft)

        self.sizeLabel = QLabel("Objective Size:")
        self.sizeInput = QSpinBox()
        self.sizeInput.setRange(1, 99)
        self.sizeInput.setFixedSize(60, 25)
        self.sizeInput.setValue(10)
        self.sizeInput.valueChanged.connect(self.set_objective_size)
        additional_controls_layout.addWidget(self.sizeLabel, 0, 2, Qt.AlignRight)
        additional_controls_layout.addWidget(self.sizeInput, 0, 3, Qt.AlignLeft)

        self.speedLabel = QLabel("Playback Speed:")
        self.speedInput = QSpinBox()
        self.speedInput.setRange(1, 99)
        self.speedInput.setFixedSize(60, 25)
        self.speedInput.setValue(50)
        self.speedInput.valueChanged.connect(self.set_speed)
        additional_controls_layout.addWidget(self.speedLabel, 0, 4, Qt.AlignRight)
        additional_controls_layout.addWidget(self.speedInput, 0, 5, Qt.AlignLeft)

        additional_controls_layout.setColumnStretch(0, 1)
        additional_controls_layout.setColumnStretch(1, 1)
        additional_controls_layout.setColumnStretch(2, 1)
        additional_controls_layout.setColumnStretch(3, 1)
        additional_controls_layout.setColumnStretch(4, 1)
        additional_controls_layout.setColumnStretch(5, 1)

        additional_size_layout.addLayout(additional_controls_layout)
        additional_size_controls.setLayout(additional_size_layout)
        self.control_layout.addWidget(additional_size_controls)

    def load_video(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mov *.mkv)")
        if file_path:
            try:
                if self.video_processor:
                    self.video_processor.release()
                self.video_processor = VideoProcessor(file_path)
                self.video_processor.set_playback_time(self.playbackTimeInput.value())  # Set initial playback time
                self.video_processor.frame_ready.connect(self.display_frame)
                ret, frame = self.video_processor.capture.read()
                if ret:
                    self.display_frame(frame)
                else:
                    raise Exception("Could not read the video file.")
            except Exception as e:
                print(f"Error loading video: {e}")

    def play_video(self):
        if self.video_processor:
            if not self.video_processor.isRunning():
                self.video_processor.start()
            self.video_processor.paused = False
            self.video_processor.start_time = time.time() - self.video_processor.elapsed_time  # Reset start time when playing the video

    def pause_video(self):
        if self.video_processor:
            self.video_processor.paused = True

    def reset_video(self):
        if self.video_processor:
            self.video_processor.reset_video()

    def pick_ball_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            hsv_color = color.toHsv()
            self.video_processor.set_color_range((hsv_color.hue() - 10, 100, 100), (hsv_color.hue() + 10, 255, 255))

    def pick_robot_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            hsv_color = color.toHsv()
            self.video_processor.set_robot_color_range((hsv_color.hue() - 10, 100, 100), (hsv_color.hue() + 10, 255, 255))

    def set_objective_size(self):
        if self.sizeInput.value() == 0:
            return
        value = self.sizeInput.value()
        if self.video_processor:
            self.video_processor.set_min_radius(value)

    def set_speed(self):
        if self.speedInput.value() == 0:
            return
        value = self.speedInput.value()
        if self.video_processor:
            self.video_processor.set_delay(int(1000 / (self.video_processor.frame_rate * (value / 50.0))))

    def set_playback_time(self):
        if self.playbackTimeInput.value() == 0:
            return
        value = self.playbackTimeInput.value()
        if self.video_processor:
            self.video_processor.set_playback_time(value)

    def display_frame(self, frame):
        if frame is not None:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p = convert_to_Qt_format.scaled(self.video_label.width(), self.video_label.height(), Qt.KeepAspectRatio)
            self.video_label.setPixmap(QPixmap.fromImage(p))

    def closeEvent(self, event):
        if self.video_processor:
            self.video_processor.release()
            self.video_processor.quit()
            self.video_processor.wait()
        cv2.destroyAllWindows()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VideoApp()
    ex.show()
    sys.exit(app.exec_())
