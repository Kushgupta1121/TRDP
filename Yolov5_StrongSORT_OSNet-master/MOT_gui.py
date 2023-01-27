from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLineEdit, QPlainTextEdit, QVBoxLayout, QHBoxLayout, QHBoxLayout,
    QWidget, QLabel, QMenu, QDialog, QAction, QDialogButtonBox, QFileDialog, QFormLayout, QLabel, QCheckBox,QGroupBox
)
from PyQt5.QtCore import QProcess, Qt, QSize
from PyQt5 import QtGui

import os
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Multi-Object Tracking")

        self.app_icon = QtGui.QIcon()
        self.app_icon.addFile('/net/cremi/kugupta/espaces/travail/Yolov5_DeepSort_Pytorch/icon.png')
        self.setWindowIcon(self.app_icon)

        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

        window_height = 400
        self.setMinimumSize(QSize(800, window_height))

        self.label1 = QLabel("Please select from the options!")
        font = self.label1.font()
        font.setPointSize(12)
        self.label1.setFont(font)
        self.label1.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.p = None

        self.RealTime = QPushButton("Real Time (Live feed)")
        self.RealTime.pressed.connect(self.start_process_RealTime)
        self.RealTime.setStyleSheet("border: 1px solid black; height: 30px")

        self.NonRealTime_NonSynth = QPushButton("Non Real Time (MOT Dataset)")
        self.NonRealTime_NonSynth.pressed.connect(self.start_process_NonRealTime_NonSynth)
        self.NonRealTime_NonSynth.setStyleSheet("border: 1px solid black; height: 30px")

        self.NonRealTime_Synth = QPushButton("Non Real Time (Synthetic Data)")
        self.NonRealTime_Synth.pressed.connect(self.start_process_NonRealTime_Synth)
        self.NonRealTime_Synth.setStyleSheet("border: 1px solid black; height: 30px")

        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.text.setMaximumHeight(window_height - 200)

        self.groupbox = QGroupBox('Select classes')

        vbox = QVBoxLayout()
        self.groupbox.setLayout(vbox)
        
        self.classes={'0': True,'5': False, '2': False, '1': False, '7': False}

        self.checkbox_class1 = QCheckBox('Human') #0
        self.checkbox_class1.setChecked(self.classes.get('0', False))
        self.checkbox_class1.clicked.connect(lambda: self.change_classes('0'))
        
        self.checkbox_class2 = QCheckBox('Bus') #5
        self.checkbox_class2.setChecked(self.classes.get('5', False))
        self.checkbox_class2.clicked.connect(lambda: self.change_classes('5'))

        self.checkbox_class3 = QCheckBox('Car') # 2
        self.checkbox_class3.setChecked(self.classes.get('2', False))
        self.checkbox_class3.clicked.connect(lambda: self.change_classes('2'))

        self.checkbox_class4 = QCheckBox('Bicycle') # 1
        self.checkbox_class4.setChecked(self.classes.get('1', False))
        self.checkbox_class4.clicked.connect(lambda: self.change_classes('1'))
        
        self.checkbox_class5 = QCheckBox('Truck') # 7
        self.checkbox_class5.setChecked(self.classes.get('7', False))
        self.checkbox_class5.clicked.connect(lambda: self.change_classes('7'))
        

        l = QVBoxLayout()  # This controls if the layout is vertical or horizontal
        l.addWidget(self.label1)
        l.addWidget(self.RealTime)
        l.addWidget(self.NonRealTime_NonSynth)
        l.addWidget(self.NonRealTime_Synth)
        
        vbox.addWidget(self.checkbox_class1) 
        vbox.addWidget(self.checkbox_class2)
        vbox.addWidget(self.checkbox_class3)
        vbox.addWidget(self.checkbox_class4)
        vbox.addWidget(self.checkbox_class5)
        
        l.addWidget(self.groupbox)
        
        l.addWidget(self.text)
        w = QWidget()
        w.setLayout(l)
        w.setStyleSheet("background: #BAE4FB")#71C7F8 C9F5EF

        self.stopButton = QPushButton("Stop")
        self.stopButton.pressed.connect(self.stop_process)
        self.stopButton.setStyleSheet("border: 1px solid black; height: 30px")
        self.stopButton.setEnabled(False)

        l.addWidget(self.stopButton)

        self.setCentralWidget(w)

        self.mainMenu = self.menuBar()
        help_menu = self.mainMenu.addMenu('Help')
        help_button = QAction('Do you really want help?', self)
        help_button.triggered.connect(lambda: self.open_help())
        help_menu.addAction(help_button)

        about_menu = self.mainMenu.addMenu('About us')
        about_button = QAction('Do you really want to know?', self)
        about_button.triggered.connect(lambda: self.open_about_us())
        about_menu.addAction(about_button)

    def stop_process(self):
        print('STOP')
        self.stopButton.setEnabled(False)
        #if self.p is None:
        self.p.terminate()

    def change_classes(self, class_name):
        self.classes[class_name] = not self.classes[class_name]
        print(self.classes)

    def open_about_us(self):
        text = 'Sorry'
        TextDialog.get_data(self, title='About us', text=text)

    def open_help(self):
        text = 'This is the help text for this application'
        TextDialog.get_data(self, title='Help', text=text)

    def message(self, s):
        self.text.appendPlainText(s)

    def start_process(self, params):
        self.message("Executing process")
        self.p = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
        self.p.readyReadStandardOutput.connect(self.handle_stdout)
        self.p.readyReadStandardError.connect(self.handle_stderr)
        self.p.stateChanged.connect(self.handle_state)
        self.p.finished.connect(self.process_finished)  # Clean up once complete.
        self.p.start("/autofs/unitytravail/travail/kugupta/trdpenv/bin/python", params)
        self.stopButton.setEnabled(True)

    def get_classes(self):
        needed_classes = [class_name for class_name, is_needed in self.classes.items() if is_needed]
        return needed_classes

    def get_params(self, project_path, model):
        params = [
                '/net/cremi/kugupta/espaces/travail/Yolov5_StrongSORT_OSNet-master/track.py',
                '--yolo-weight', f'{model}',
                '--tracking-method', 'strongsort', #osnet_x1_0_market1501
                '--source', f'{project_path}',
                '--show-vid', '--classes'
        ]
        for class_name in self.get_classes():
            params.append(class_name)
        return params

    def start_process_RealTime(self):
        project_path, model, accepted = SettingsDialog2.get_data(self, title='URL for RealTime')
        if accepted and self.p is None:  # No process running
            params = self.get_params(project_path, model)
            print(params)
            self.start_process(params)

    def start_process_NonRealTime_NonSynth(self):
        project_path, model, save_file, accepted = SettingsDialog1.get_data(self, title='Upload sequence for NonRealTime_NonSynth')
        if accepted and self.p is None:  # No process running.
            params = self.get_params(project_path, model)
            if save_file:
                params.append('--save-txt')
            print(params)
            self.start_process(params)

    def start_process_NonRealTime_Synth(self):
        project_path, model, save_file, accepted = SettingsDialog1.get_data(self, title='Upload sequence for NonRealTime_Synth')
        if accepted and self.p is None:  # No process running.
            params = self.get_params(project_path, model)
            if save_file:
                params.append('--save-txt')
            print(params)
            self.start_process(params)

    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.message(stderr)

    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message(stdout)

    def handle_state(self, state):
        states = {
            QProcess.NotRunning: 'Not running',
            QProcess.Starting: 'Starting',
            QProcess.Running: 'Running',
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")

    def process_finished(self):
        self.message("Process finished.")
        self.p = None


class Dialog(QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.parent = parent
        self.create_layout()

    def create_layout(self):
        pass

    @staticmethod
    def get_data(parent=None, title=''):
        pass


class TextDialog(Dialog):
    def create_layout(self):
        layout = QHBoxLayout(self)

        self.text = QPlainTextEdit('Sorry, we can not help you!')
        self.text.setReadOnly(True)
        self.text.setStyleSheet("background-color: #f0f0f0; border: 0")

        layout.addWidget(self.text)

    @staticmethod
    def get_data(parent=None, title='', text=''):
        dialog = TextDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.text.setPlainText(text)
        dialog.exec_()


class SettingsDialog(Dialog):
    def create_accept_buttons(self):
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        self.layout.addRow(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def add_filepath_input(self, command):
        path_line = QLineEdit()
        path_line.setMinimumWidth(400)
        path_line.setReadOnly(True)
        path_button = QPushButton('...')
        path_button.clicked.connect(command)

        path_form = QHBoxLayout()
        path_form.addWidget(path_line)
        path_form.addWidget(path_button)

        return path_line, path_form

    def handle_ok_button(self):
        button_ok = self.buttons.button(QDialogButtonBox.Ok)
        if not self.file_path_line.text() or not self.model_path_line.text():
            button_ok.setEnabled(False)
        else:
            button_ok.setEnabled(True)

    def get_path(self):
        file_path, file_type = QFileDialog.getOpenFileName(self, "Select file", '', "Videos (*.mp4)")
        if file_path:
            self.file_path_line.setText(file_path)
        self.handle_ok_button()

    def get_model_path(self):
        model_path, file_type = QFileDialog.getOpenFileName(self, "Select file", '', "Models (*.pt)")
        if model_path:
            self.model_path_line.setText(model_path)
        self.handle_ok_button()


class SettingsDialog1(SettingsDialog):
    def create_layout(self):
        self.layout = QFormLayout(self)

        self.file_path_line, self.file_path_form = self.add_filepath_input(self.get_path)
        self.model_path_line, self.model_path_form = self.add_filepath_input(self.get_model_path)
        self.checkbox1 = QCheckBox('')
        self.checkbox1.setChecked(True)

        self.layout.addRow(QLabel("Select file: "), self.file_path_form)
        self.layout.addRow(QLabel("Select YOLO model: "), self.model_path_form)
        self.layout.addRow(QLabel(text='Save file:'), self.checkbox1)

        self.create_accept_buttons()

    @staticmethod
    def get_data(parent=None, title=''):
        dialog = SettingsDialog1(parent)
        dialog.setWindowTitle(title)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        button_ok = dialog.buttons.button(QDialogButtonBox.Ok)
        button_ok.setEnabled(False)

        result = dialog.exec_()
        path = dialog.file_path_line.text()
        model = dialog.model_path_line.text()
        save_file = dialog.checkbox1.isChecked()

        return path, model, save_file, result == QDialog.Accepted


class SettingsDialog2(SettingsDialog):
    def create_layout(self):
        self.layout = QFormLayout(self)

        self.file_path_line = QLineEdit()
        self.file_path_line.setMinimumWidth(400)
        self.file_path_line.textChanged.connect(self.handle_ok_button)
        self.model_path_line, self.model_path_form = self.add_filepath_input(self.get_model_path)

        self.layout.addRow(QLabel("Select file: "), self.file_path_line)
        self.layout.addRow(QLabel("Select model: "), self.model_path_form)

        self.create_accept_buttons()

    @staticmethod
    def get_data(parent=None, title=''):
        dialog = SettingsDialog2(parent)
        dialog.setWindowTitle(title)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        button_ok = dialog.buttons.button(QDialogButtonBox.Ok)
        button_ok.setEnabled(False)

        result = dialog.exec_()
        path = dialog.file_path_line.text()
        model = dialog.model_path_line.text()

        return path, model, result == QDialog.Accepted


app = QApplication(sys.argv)

w = MainWindow()
w.show()

app.exec_()
