# -*- coding: utf-8 -*-

COM_PORT = None
csv_path = 'csv'


import sys
import random
import re
import csv
import os
import serial
import io
import time
import serial.tools.list_ports

from PyQt5 import QtGui, QtCore
from PyQt5.QtChart import *
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QLabel, QApplication,
                             QGridLayout, QPushButton, QListWidget,
                             QListWidgetItem, QLineEdit, QMessageBox
                             )
from PyQt5.QtGui import QPixmap, QPainter, QPalette, QColor


class MainWindow(QWidget):

        def __init__(self, ser, sio):
            super().__init__()

            # Setup the colour palette
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor(40, 40, 40))
            palette.setColor(QPalette.WindowText, QColor(230, 230, 230))
            palette.setColor(QPalette.Base, QColor(252, 252, 252))
            palette.setColor(QPalette.AlternateBase, QColor(239, 240, 241))
            palette.setColor(QPalette.ToolTipBase, QColor(239, 240, 241))
            palette.setColor(QPalette.ToolTipText, QColor(49, 54, 59))
            palette.setColor(QPalette.Text, QColor(0, 0, 0))
            palette.setColor(QPalette.Button, QColor(85, 90, 95))
            palette.setColor(QPalette.ButtonText, QColor(50, 50, 50))
            palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
            palette.setColor(QPalette.Link, QColor(41, 128, 185))
            palette.setColor(QPalette.Highlight, QColor(136, 136, 136))
            palette.setColor(QPalette.HighlightedText, QColor(239, 240, 241))
            palette.setColor(QPalette.Disabled, QPalette.Light, Qt.white)
            palette.setColor(QPalette.Disabled, QPalette.Shadow, QColor(234, 234, 234))
            self.setPalette(palette)

            self.ser = ser
            self.sio = sio
            self.start = 1
            self.maxforce = 0000.00
            self.oldforce = 0.0
            self.force = 0.0
            self.initUI()

        def initUI(self):
            self.grid = QGridLayout()
            self.teams = {}
            self.currentteam = [QListWidgetItem_Team()]
            self.chartView = QChartView()
            self.loadNewGraph = True

            # LCD Widget to display the force
            self.forcelcd = QLCDNumber(7, self)
            self.forcelcd.setStyleSheet("color: rgb(0, 210, 0); border-image: url(background3.png) stretch; background-repeat: no-repeat;")
            lcdpalette = self.forcelcd.palette()
            lcdpalette.setColor(lcdpalette.Light, QtGui.QColor(0, 255, 0))
            lcdpalette.setColor(lcdpalette.Dark, QtGui.QColor(0, 0, 0))
            self.forcelcd.setPalette(lcdpalette)
            self.forcelcd.setFrameStyle(0)

            # Push buttons
            zero = QPushButton('Zero Scale', self)
            clearmax = QPushButton('Reset', self)
            clearmax.clicked.connect(self.reset)
            export = QPushButton('Export', self)
            togglestart = QPushButton('Start/Stop', self)

            # Push Button Functions
            zero.clicked.connect(self.zero_scale)
            clearmax.clicked.connect(self.reset)
            export.clicked.connect(self.exportTeams)
            togglestart.clicked.connect(self.toggle)

            # Textbox to enter in team name
            self.teaminput = QLineEdit()
            self.teaminput.setText('Enter team here')
            self.teaminput.returnPressed.connect(self.addTeam)

            # Current highest force text
            self.maxforce = 0000.00
            self.maxforcetxt = QLabel()
            self.maxforcetxt.setFont(QtGui.QFont("Quartz", 62))
            self.maxforcetxt.setText("Maximum Force: %.2f N" % self.maxforce )
            self.maxforcetxt.setStyleSheet("color: rgb(0, 210, 0); background-image: url(maxbackground.png); background-attachment: fixed")
            self.maxforcetxt.setAlignment(QtCore.Qt.AlignCenter)

            # List of teams and scores
            self.teamlist = QListWidget()
            self.teamlist.setStyleSheet("background-color: rgb(85, 90, 100);")
            self.teamlist.setSortingEnabled(True)
            self.teamlist.itemDoubleClicked.connect(self.selectTeam)

            # EGBC Logo
            self.EGBC = QLabel()
            img = QPixmap('EGBC_Logo_Mod2.png')
            self.EGBC.setPixmap(img)


            # Add widgets to grid and format
            self.grid.setColumnStretch(1, 2)
            self.grid.setColumnStretch(2, 2)
            self.grid.setColumnStretch(3, 2)
            self.grid.setColumnStretch(4, 2)
            self.grid.setColumnStretch(5, 1)
            self.grid.setColumnStretch(6, 2)
            self.grid.setRowStretch(1, 6)
            self.grid.setRowStretch(0, 1)

            self.grid.addWidget(self.maxforcetxt, 0, 1, 1, 4)
            self.grid.addWidget(self.EGBC, 0, 5, 1, 2)
            self.grid.addWidget(self.forcelcd, 1, 1, 1, 5)
            self.grid.addWidget(zero, 2, 1)
            self.grid.addWidget(clearmax, 2, 2)
            self.grid.addWidget(export, 2, 3)
            self.grid.addWidget(togglestart, 2, 4)
            self.grid.addWidget(self.teamlist, 1, 6)
            self.grid.addWidget(self.teaminput, 2, 6)

            self.updateforce()
            self.setLayout(self.grid)
            print(self.teaminput.width())
            self.showFullScreen()

        def keyPressEvent(self, e):
            if e.key() == Qt.Key_Escape:
                reply = QMessageBox.question(self, 'PyQt5 message', "Do you want to exit the program?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.close()
                else:
                    e.ignore()

        def zero_scale(self):
            self.ser.write(b'x\r\n')
            self.sio.flush()
            trunk = self.sio.readline()
            self.ser.write(b'1\r\n')
            self.sio.flush()
            for line in self.sio.readlines():
                if line == '>\r\n':
                    break
            self.ser.write(b'x\r\nx\r\n')
            self.sio.flush()
            self.reset()
            return

        def reset(self):
            self.maxforce = 0.0
            self.force = 0.0
            self.maxforcetxt.setText(str("Maximum Force: %.2f N" % self.maxforce))
            self.forcelcd.display(self.force)

        def toggle(self):
            self.start ^= 1
            if self.start:
                self.chartView.hide()
                #self.grid.removeWidget(self.chartView)
                self.forcelcd.show()
            else:
                self.loadNewGraph = True
                self.forcelcd.hide()

        def addTeam(self):
            self.grid.removeWidget(self.chartView)
            team = self.teaminput.text()
            print(team)
            if team and team != "Enter team here":
                self.teaminput.setText("")
                self.teams[team] = [0.00, ]

                item = QListWidgetItem_Team()
                item.setText(team + " - " + str(self.teams[team]))
                item.setFont(QtGui.QFont("Times", 32))

                self.teamlist.addItem(item)

            with open(os.path.join(csv_path, team + '.csv'), 'w', newline='') as csvfileout:
                writer = csv.DictWriter(csvfileout, fieldnames=['Sample', 'Force'])
                writer.writeheader()
                csvfileout.close()

        def selectTeam(self):
            self.chartView.hide()
            self.currentteam = self.teamlist.selectedItems()
            if not self.start:
                self.loadNewGraph = True

        def exportTeams(self):
            for team in self.teams:
                sample = 0
                with open(os.path.join(csv_path, team + '.csv'), 'w', newline='') as csvfileout:
                    writer = csv.DictWriter(csvfileout, fieldnames=['Sample', 'Force'])
                    writer.writeheader()
                    for samples in self.teams[team]:
                        writer.writerow({'Sample': sample, 'Force': samples})
                        sample += 1
                csvfileout.close()

        def get_force(self):
            self.ser.flushOutput()
            self.ser.flushInput()
            output = self.sio.readline()
            print(output)

            if 'Exiting' not in output and len(output) in range(10, 12):
                end = output.rfind(',kg')
                value = output[0:end]
            else:
                value = self.oldforce/9.81
            return value


        def updateforce(self):
            self.grid.removeWidget(self.chartView)
            if self.start:
                # Generate some random force values for testing
                #self.force = random.randrange(1,5000,1)
                #self.force += 0.01

                self.force = round(float(self.get_force()) * 9.81, 2)
                self.forcelcd.display(self.force)
                self.oldforce = self.force

                # Update team dictionary and CSV file
                if self.currentteam[0].name():
                    self.teams[self.currentteam[0].name()].append(self.force)

                    start = time.time()
                    with open(os.path.join(csv_path, self.currentteam[0].name() + ".csv"), "a+", newline='') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=['Sample', 'Force'])
                        csvfile.seek(0)

                        writer.writerow({'Sample': self.currentteam[0].samples, 'Force': self.force})
                        self.currentteam[0].samples += 1
                        csvfile.close()
                    end = time.time()
                    print(end - start)

            # New max force found, update the force label and list
                if self.force > self.maxforce:
                    self.maxforce = self.force
                    self.maxforcetxt.setText("Maximum Force: %.2f N" % self.force)
                    self.currentteam[0].setForce(self.force)

            if not self.start and self.loadNewGraph:
                data = QSplineSeries()
                data.setName(self.currentteam[0].name())

                with open(os.path.join(csv_path, self.currentteam[0].name() + '.csv'), "r", newline='') as file:
                    for line in file:
                        if "Sample" not in line:
                            s = line.split(",")
                            data.append(float(s[0]), float(s[1]))
                    file.close()

                maxForceline = QLineSeries()
                maxForceline.setName("Maxiumum Force")
                maxForceline.append(0.0, self.currentteam[0].force())
                maxForceline.append(self.currentteam[0].samples, self.currentteam[0].force())

                force_chart = QChart()
                force_chart.addSeries(data)
                force_chart.addSeries(maxForceline)
                force_chart.setToolTip("{}".format(self.maxforce))
                force_chart.setTitle("Force vs. Time Graph for {}".format(self.currentteam[0].name()))
                force_chart.createDefaultAxes()
                force_chart.axisY().setRange(0, self.currentteam[0].force() + 10)
                force_chart.setTheme(2)
                self.chartView = QChartView(force_chart)
                self.chartView.setRenderHint(QPainter.Antialiasing)
                # self.grid.removeWidget(self.chartView)
                self.grid.addWidget(self.chartView, 1, 1, 1, 5)
                print(self.grid.children())
                self.chartView.show()
                self.loadNewGraph = False

            QtCore.QTimer.singleShot(200, lambda: self.updateforce())

class QListWidgetItem_Team(QListWidgetItem):

    samples = 1

    def setForce(self, force):
        self.setText(self.name() + " - " + str(force))

    def force(self):
        r = re.compile("([0-9]*[.]){1}[0-9]+")
        return float(r.search(self.text()).group(0))

    def name(self):
        end = self.text().rfind(' -')
        return self.text()[0:end]

    def __lt__(self, other):
        return self.force() > other.force()


def main():
    app = QApplication(sys.argv)

    # Detect COM port
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "USB Serial Port" in p.description:
            match = re.search(r"COM\d", p.description)
            COM_PORT = match.group(0)

    # Setup COM port
    ser = serial.Serial(COM_PORT, 115200, timeout=0.2)
    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser), newline='\r\n')
    start_ = time.time()
    while time.time() < start_ + 1:
        trunk = ser.readline()

    # Start bridge crusher
    cMain = MainWindow(ser, sio)

    sys.exit(app.exec_())

if __name__== '__main__':
    main()
