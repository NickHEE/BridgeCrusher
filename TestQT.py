<<<<<<< HEAD
# -*- coding: utf-8 -*-

import sys
import random
import re
import csv
import os
import serial
import io
import time

from PyQt5 import QtGui, QtCore
from PyQt5.QtChart import *
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QLabel, QApplication,
                             QGridLayout, QPushButton, QListWidget,
                             QListWidgetItem, QLineEdit, QMessageBox
                             )
from PyQt5.QtGui import QPixmap, QPainter


# CLASSES


class MainWindow(QWidget):

        def __init__(self, ser, sio):
            super().__init__()
            self.ser = ser
            self.sio = sio
            self.start = 1
            self.maxforce = 0000.00
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
            self.forcelcd.setStyleSheet("color: rgb(0, 210, 0); background-image: url(background3.png); background-attachment: fixed")
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
            self.maxforcetxt.setText("Maximum Force: %f" % self.maxforce )
            self.maxforcetxt.setStyleSheet("color: rgb(0, 210, 0); background-image: url(maxbackground.png); background-attachment: fixed")
            self.maxforcetxt.setAlignment(QtCore.Qt.AlignCenter)

            # List of teams and scores
            self.teamlist = QListWidget()
            #self.teamlist.setStyleSheet("QListWidget::item::selected {background-color: green;}")
            self.teamlist.setSortingEnabled(True)
            self.teamlist.itemDoubleClicked.connect(self.selectTeam)

            # EGBC Logo
            self.EGBC = QLabel()
            img = QPixmap('EGBC_Logo_Mod2.png')
            self.EGBC.setPixmap(img)


            # Add widgets to grid and format
            self.grid.setColumnStretch(1, 5)
            self.grid.setColumnStretch(2, 5)
            self.grid.setColumnStretch(3, 5)
            self.grid.setColumnStretch(4, 5)
            self.grid.setRowStretch(1, 6)
            self.grid.setRowStretch(0, 2)
            self.grid.setRowStretch(0, 1)

            self.grid.addWidget(self.maxforcetxt, 0, 1, 1, 3)
            self.grid.addWidget(self.EGBC, 0, 4)
            self.grid.addWidget(self.forcelcd, 1, 1, 1, 4)
            self.grid.addWidget(zero, 2, 1)
            self.grid.addWidget(clearmax, 2, 2)
            self.grid.addWidget(export, 2, 3)
            self.grid.addWidget(togglestart, 2, 4)
            self.grid.addWidget(self.teamlist, 1, 5)
            self.grid.addWidget(self.teaminput, 2, 5)

            self.updateforce()
            self.setLayout(self.grid)
            print(self.teaminput.width())
            self.showFullScreen()

        # FUNCTIONS
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
            #self.loadNewGraph = True
            #if not self.start:
                #self.loadNewGraph = True

        def addTeam(self):
            team = self.teaminput.text()
            print(team)
            if team and team != "Enter team here":
                self.teaminput.setText("")
                self.teams[team] = [0.00, ]

                item = QListWidgetItem_Team()
                item.setText(team + " - " + str(self.teams[team]))
                item.setFont(QtGui.QFont("Times", 32))

                self.teamlist.addItem(item)

            with open(team + '.csv', 'w', newline='') as csvfileout:
                writer = csv.DictWriter(csvfileout, fieldnames=['Sample', 'Force'])
                writer.writeheader()
                csvfileout.close()

        def selectTeam(self):
            self.currentteam = self.teamlist.selectedItems()
            self.loadNewGraph = True

        def exportTeams(self):
            #print([self.teams[team] for team in self.teams])

            for team in self.teams:
                sample = 0
                with open(team + '.csv', "w", newline='') as csvfileout:
                    writer = csv.DictWriter(csvfileout, fieldnames=['Sample', 'Force'])
                    writer.writeheader()
                    for samples in self.teams[team]:
                        writer.writerow({'Sample': sample, 'Force': samples})
                        sample += 1
                csvfileout.close()

        def get_force(self):
            start = time.time()
            output = self.sio.readline()
            end = time.time()
            duration = end - start
            print(duration)

            if 'Exiting' not in output and output:
                end = output.rfind(',kg')
                value = output[0:end]
            else:
                value = 0.0
            return value


        def updateforce(self):

            if self.start:
                self.loadNewGraph = True
                self.chartView.hide()
                self.forcelcd.show()
                # Generate some random force values for testing
                #self.force = random.randrange(1,5000,1)
                #self.force += 0.01
                self.force = float(self.get_force())
                self.forcelcd.display(self.force)

                # Update team dictionary and CSV file
                if self.currentteam[0].name():
                    self.teams[self.currentteam[0].name()].append(self.force)

                    with open(self.currentteam[0].name() + ".csv", "a+", newline='') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=['Sample', 'Force'])
                        csvfile.seek(0)
                        samplenum = sum(1 for line in csvfile)
                        writer.writerow({'Sample': samplenum, 'Force': self.force})
                        csvfile.close()

            # New max force found, update the force label and list
                if self.force > self.maxforce:
                    self.maxforce = self.force
                    self.maxforcetxt.setText("Maximum Force: %.2f" % self.force)
                    #self.maxforcetxt.setStyleSheet("QLabel {background-color: red}")
                    #QtCore.QTimer.singleShot(250, lambda: self.maxforcetxt.setStyleSheet(""))
                    self.currentteam[0].setForce(self.force)

            if not self.start and self.loadNewGraph:
                self.forcelcd.hide()

                data = QSplineSeries()
                data.setName("Test Graph")

                with open(self.currentteam[0].name() + '.csv', "r", newline='') as file:
                    for line in file:
                        if "Sample" not in line:
                            s = line.split(",")
                            data.append(float(s[0]), float(s[1]))
                    file.close()

                force_chart = QChart()
                force_chart.addSeries(data)
                force_chart.setTitle("Test")
                force_chart.createDefaultAxes()
                force_chart.setTheme(2)
                self.chartView = QChartView(force_chart)
                self.chartView.setRenderHint(QPainter.Antialiasing)
                self.grid.addWidget(self.chartView, 1, 1, 1, 4)
                self.chartView.show()
                self.loadNewGraph = False;

            QtCore.QTimer.singleShot(200, lambda: self.updateforce())

class QListWidgetItem_Team(QListWidgetItem):

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
    ser = serial.Serial('COM4', 115200, timeout=0.2)
    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser), newline='\r\n')
    start_ = time.time()
    while time.time() < start_ + 1:
        trunk = ser.readline()

    cMain = MainWindow(ser, sio)
    sys.exit(app.exec_())


if __name__== '__main__':
    main()
=======
# -*- coding: utf-8 -*-

import sys
import random
import re
import csv
import os
import serial
import io
import time

from PyQt5 import QtGui, QtCore
from PyQt5.QtChart import *
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QLabel, QApplication,
                             QGridLayout, QPushButton, QListWidget,
                             QListWidgetItem, QLineEdit, QMessageBox
                             )
from PyQt5.QtGui import QPixmap, QPainter


# CLASSES


class MainWindow(QWidget):

        def __init__(self):
            super().__init__()
            #self.ser = ser
            #self.sio = sio
            self.start = 1
            self.maxforce = 0000.00
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
            self.forcelcd.setStyleSheet("color: rgb(0, 210, 0); background-image: url(background3.png); background-attachment: fixed")
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
            self.maxforcetxt.setText("Maximum Force: %f" % self.maxforce )
            self.maxforcetxt.setStyleSheet("color: rgb(0, 210, 0); background-image: url(maxbackground.png); background-attachment: fixed")
            self.maxforcetxt.setAlignment(QtCore.Qt.AlignCenter)

            # List of teams and scores
            self.teamlist = QListWidget()
            #self.teamlist.setStyleSheet("QListWidget::item::selected {background-color: green;}")
            self.teamlist.setSortingEnabled(True)
            self.teamlist.itemDoubleClicked.connect(self.selectTeam)

            # EGBC Logo
            self.EGBC = QLabel()
            img = QPixmap('EGBC_Logo_Mod2.png')
            self.EGBC.setPixmap(img)


            # Add widgets to grid and format
            self.grid.setColumnStretch(1, 5)
            self.grid.setColumnStretch(2, 5)
            self.grid.setColumnStretch(3, 5)
            self.grid.setColumnStretch(4, 5)
            self.grid.setRowStretch(1, 6)
            self.grid.setRowStretch(0, 2)
            self.grid.setRowStretch(0, 1)

            self.grid.addWidget(self.maxforcetxt, 0, 1, 1, 3)
            self.grid.addWidget(self.EGBC, 0, 4)
            self.grid.addWidget(self.forcelcd, 1, 1, 1, 4)
            self.grid.addWidget(zero, 2, 1)
            self.grid.addWidget(clearmax, 2, 2)
            self.grid.addWidget(export, 2, 3)
            self.grid.addWidget(togglestart, 2, 4)
            self.grid.addWidget(self.teamlist, 1, 5)
            self.grid.addWidget(self.teaminput, 2, 5)

            self.updateforce()
            self.setLayout(self.grid)
            print(self.teaminput.width())
            self.showFullScreen()

        # FUNCTIONS
        def keyPressEvent(self, e):
            if e.key() == Qt.Key_Escape:
                reply = QMessageBox.question(self, 'PyQt5 message', "Do you want to exit the program?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.close()
                else:
                    e.ignore()

        def zero_scale(self):
            """
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
            """
            return


        def reset(self):
            self.maxforce = 0.0
            self.force = 0.0
            self.maxforcetxt.setText(str("Maximum Force: %.2f N" % self.maxforce))
            self.forcelcd.display(self.force)

        def toggle(self):
            self.start ^= 1
            #self.loadNewGraph = True
            #if not self.start:
                #self.loadNewGraph = True

        def addTeam(self):
            team = self.teaminput.text()
            print(team)
            if team and team != "Enter team here":
                self.teaminput.setText("")
                self.teams[team] = [0.00, ]

                item = QListWidgetItem_Team()
                item.setText(team + " - " + str(self.teams[team]))
                item.setFont(QtGui.QFont("Times", 32))

                self.teamlist.addItem(item)

            with open(team + '.csv', 'w', newline='') as csvfileout:
                writer = csv.DictWriter(csvfileout, fieldnames=['Sample', 'Force'])
                writer.writeheader()
                csvfileout.close()

        def selectTeam(self):
            self.currentteam = self.teamlist.selectedItems()
            self.loadNewGraph = True

        def exportTeams(self):
            #print([self.teams[team] for team in self.teams])

            for team in self.teams:
                sample = 0
                with open(team + '.csv', "w", newline='') as csvfileout:
                    writer = csv.DictWriter(csvfileout, fieldnames=['Sample', 'Force'])
                    writer.writeheader()
                    for samples in self.teams[team]:
                        writer.writerow({'Sample': sample, 'Force': samples})
                        sample += 1
                csvfileout.close()
        
        def get_force(self):
            output = self.sio.readline()
            if 'Exiting' not in output:
                # start = output.rfind('-')
                end = output.rfind(',kg')
                value = output[0:end]
            else:
                value = 0.0
            return value

        def updateforce(self):

            if self.start:
                self.loadNewGraph = True
                self.chartView.hide()
                self.forcelcd.show()
                # Generate some random force values for testing
                #self.force = random.randrange(1,5000,1)
                #self.force += 0.01
                self.force = float(self.get_force())
                self.forcelcd.display(self.force)

                # Update team dictionary and CSV file
                if self.currentteam[0].name():
                    self.teams[self.currentteam[0].name()].append(self.force)

                    with open(self.currentteam[0].name() + ".csv", "a+", newline='') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=['Sample', 'Force'])
                        csvfile.seek(0)
                        samplenum = sum(1 for line in csvfile)
                        writer.writerow({'Sample': samplenum, 'Force': self.force})
                        csvfile.close()

            # New max force found, update the force label and list
                if self.force > self.maxforce:
                    self.maxforce = self.force
                    self.maxforcetxt.setText("Maximum Force: %.2f" % self.force)
                    #self.maxforcetxt.setStyleSheet("QLabel {background-color: red}")
                    #QtCore.QTimer.singleShot(250, lambda: self.maxforcetxt.setStyleSheet(""))
                    self.currentteam[0].setForce(self.force)

            if not self.start and self.loadNewGraph:
                self.forcelcd.hide()

                data = QSplineSeries()
                data.setName("Test Graph")

                with open(self.currentteam[0].name() + '.csv', "r", newline='') as file:
                    for line in file:
                        if "Sample" not in line:
                            s = line.split(",")
                            data.append(float(s[0]), float(s[1]))
                    file.close()

                force_chart = QChart()
                force_chart.addSeries(data)
                force_chart.setTitle("Test")
                force_chart.createDefaultAxes()
                force_chart.setTheme(2)
                self.chartView = QChartView(force_chart)
                self.chartView.setRenderHint(QPainter.Antialiasing)
                self.grid.addWidget(self.chartView, 1, 1, 1, 4)
                self.chartView.show()
                self.loadNewGraph = False;

            QtCore.QTimer.singleShot(200, lambda: self.updateforce())

class QListWidgetItem_Team(QListWidgetItem):

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
    #ser = serial.Serial('COM4', 115200, timeout=1)
    #sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser), newline='\r\n')
    #start_ = time.time()
    #while time.time() < start_ + 1:
        #trunk = ser.readline()

    cMain = MainWindow(ser, sio)
    sys.exit(app.exec_())


if __name__== '__main__':
    main()

