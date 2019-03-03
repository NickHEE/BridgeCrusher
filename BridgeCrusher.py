""" BridgeCrusher.py - Created by Nicholas Huttemann and Julie Lee for the annual EGBC 'bridge crushing competition'
during our 2018 co-op with WTS. Designed for use with the 'SparkFun OpenScale' (https://www.sparkfun.com/products/13261)
"""

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
                             QListWidgetItem, QLineEdit, QMessageBox)
from PyQt5.QtGui import QPixmap, QPainter, QPalette, QColor

script_dir = os.path.dirname(__file__)
csv_path = os.path.join(script_dir,'csv')


class MainWindow(QWidget):

        def __init__(self, ser=None, sio=None, teamsFromfile=False):
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
            self.maxForce = 0000.00
            self.oldForce = 0.0
            self.force = 0.0
            self.initUI()

        def initUI(self):
            """ Instantiate and connect all widgets of the GUI """

            self.inActive = 0
            self.grid = QGridLayout()
            self.teams = {}
            self.activeTeam = [QListWidgetItem_Team()]
            self.chartView = QChartView()
            self.loadNewGraph = True

            # LCD Widget to display the force
            self.forceLCD = QLCDNumber(7, self)
            self.forceLCD.setStyleSheet(r"color: rgb(0, 210, 0); "
                                        r"border-image: url(background.png);"
                                        r"stretch; "
                                        r"background-repeat: no-repeat;")
            lcdPalette = self.forceLCD.palette()
            lcdPalette.setColor(lcdPalette.Light, QtGui.QColor(0, 255, 0))
            lcdPalette.setColor(lcdPalette.Dark, QtGui.QColor(0, 0, 0))
            self.forceLCD.setPalette(lcdPalette)
            self.forceLCD.setFrameStyle(0)

            # Push buttons
            zero = QPushButton('Zero Scale', self)
            clearMax = QPushButton('Reset', self)
            clearMax.clicked.connect(self.reset)
            load = QPushButton('Load Teams', self)
            self.toggleStart = QPushButton('Stop', self)

            # Push Button Functions
            zero.clicked.connect(self.zeroScale)
            clearMax.clicked.connect(self.reset)
            load.clicked.connect(self.loadTeams)
            self.toggleStart.clicked.connect(self.toggle)

            # Textbox to enter in team name
            self.teamInput = QLineEdit()
            self.teamInput.setText('Enter team here')
            self.teamInput.returnPressed.connect(self.addTeam)

            # Current highest force text
            self.maxForce = 0000.00
            self.maxForceText = QLabel()
            self.maxForceText.setFont(QtGui.QFont("DS-Digital", 68))
            self.maxForceText.setText("Maximum Force: %.2f N" % self.maxForce)
            self.maxForceText.setStyleSheet(r"color: rgb(0, 210, 0); "
                                           r"background-image: url(maxbackground.png); "
                                           r"background-attachment: fixed;"
                                           r"background-repeat: no-repeat;")
            self.maxForceText.setAlignment(QtCore.Qt.AlignCenter)

            # List of teams and scores
            self.teamList = QListWidget()
            self.teamList.setStyleSheet("QListWidget{background-color: rgb(85, 90, 100);}"
                                        "QListWidget::item:selected{background: #93d130; color: #000000}"
                                        "QLabel{background: transparent;border: none;}")
            self.teamList.setSortingEnabled(True)
            self.teamList.itemClicked.connect(self.selectTeam)

            # EGBC Logo
            self.EGBC = QLabel()
            img = QPixmap('logo.png')
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

            self.grid.addWidget(self.maxForceText, 0, 1, 1, 4)
            self.grid.addWidget(self.EGBC, 0, 5, 1, 2)
            self.grid.addWidget(self.forceLCD, 1, 1, 1, 5)
            self.grid.addWidget(zero, 2, 1)
            self.grid.addWidget(clearMax, 2, 2)
            self.grid.addWidget(load, 2, 3)
            self.grid.addWidget(self.toggleStart, 2, 4)
            self.grid.addWidget(self.teamList, 1, 6)
            self.grid.addWidget(self.teamInput, 2, 6)

            self.updateForce()
            self.setLayout(self.grid)
            self.showFullScreen()

        def keyPressEvent(self, e):
            """ Handles any key presses. Currently only ESC key used. """

            if e.key() == Qt.Key_Escape:
                reply = QMessageBox.question(self, 'PyQt5 message', "Do you want to exit the program?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.close()
                else:
                    e.ignore()

        def zeroScale(self):
            """ Writes a sequence of characters that will zero the 'OpenScale' """

            if self.ser and self.sio:
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
            else:
                QMessageBox.question(self, 'PyQt5 message', "No serial connection available. Connect serial device and "
                                                            "reload Brudge Crusher. (Or launch without '-debug')",
                                     QMessageBox.Ok)

        def reset(self):
            """ Resets the maximum force text at the top of the window. No longer an essential function. """

            self.maxForce = 0.0
            self.force = 0.0
            self.maxForceText.setText(str("Maximum Force: %.2f N" % self.maxForce))
            self.forceLCD.display(self.force)

        def toggle(self):
            """ Toggle Bridge Crusher between the 'start' and 'stop' states. Data is recorded during the start state
            and displayed in a graph format in the stop state. If there is no active team selected and the
            stop state is entered, the forceLCD will pause but no graph will show. """

            if self.teams and self.activeTeam[0].name():
                self.inActive = 0;
                self.start ^= 1
                if self.start:
                    self.toggleStart.setText('Stop')
                    self.chartView.hide()
                    self.forceLCD.show()
                else:
                    self.toggleStart.setText('Start')
                    self.loadNewGraph = True
                    self.forceLCD.hide()
            elif not self.teams:
                m = QMessageBox.question(self, 'PyQt5 message', "Enter a team and record data to view force graph",
                                             QMessageBox.Ok)
            elif not self.activeTeam[0].name():
                self.inActive ^= 1;
                if self.inActive:
                    self.toggleStart.setText('Start')
                else:
                    self.toggleStart.setText('Stop')


        def addTeam(self):
            """ Adds a new team to the teamList from the textbox and creates a corresponding .csv.
            Triggers when a team is entered into the teamList textbox. """

            self.grid.removeWidget(self.chartView)
            team = self.teamInput.text()
            print(team)
            if team and team != "Enter team here":
                self.teamInput.setText("")
                self.teams[team] = [0.00, ]
                item = QListWidgetItem_Team()
                item.setText(team + " - " + str(self.teams[team]))
                item.setFont(QtGui.QFont("Times", 32))
                self.teamList.addItem(item)

            with open(os.path.join(csv_path, team + '.csv'), 'w+', newline='') as csvfileout:
                writer = csv.DictWriter(csvfileout, fieldnames=['Sample', 'Force'])
                writer.writeheader()
                csvfileout.close()

        def selectTeam(self):
            """ Upon left clicking on a team, it is selected as the 'active team' and force data will be recorded for
            that team. """

            self.chartView.hide()
            self.activeTeam = self.teamList.selectedItems()
            self.maxForce = self.activeTeam[0].maxForce
            self.maxForceText.setText("Maximum Force: %.2f N" % self.maxForce)
            if not self.start:
                self.loadNewGraph = True

        def loadTeams(self):
            """ Load team names from 'teams.txt' """

            try:
                with open('teams.txt') as f:
                    teams = [team.rstrip() for team in f]
                    if not set(teams) & set(self.teams.keys()):
                        for team in teams:
                            self.teams[team] = [0.00, ]
                            item = QListWidgetItem_Team()
                            item.setText(team + " - " + str(self.teams[team]))
                            item.setFont(QtGui.QFont("Times", 32))
                            self.teamList.addItem(item)

                            with open(os.path.join(csv_path, team + '.csv'), 'w+', newline='') as csvfileout:
                                writer = csv.DictWriter(csvfileout, fieldnames=['Sample', 'Force'])
                                writer.writeheader()
                                csvfileout.close()
            except:
                m = QMessageBox.question(self, 'PyQt5 message',
                                         "Unable to load teams from file. Does 'teams.txt' exist?",
                                         QMessageBox.Ok)

        def getForce(self):
            """ Gets the current force value through the serial interface. """

            self.ser.flushOutput()
            self.ser.flushInput()
            output = self.sio.readline()
            print(output)

            # Ensure that the value is valid
            if 'Exiting' not in output and len(output) in range(10, 13):
                end = output.rfind(',kg')
                value = output[0:end]
            else:
                value = self.oldForce / 9.81
            return value

        def updateForce(self):
            """ Updates the force displays and writes to the team .csv when in the 'start' state. When in the stop
            state, reads from the team .csv and displays the recorded force data on a graph."""

            self.grid.removeWidget(self.chartView)
            if self.start:
                if not self.ser or not self.sio:
                    # Generate some random force values for testing
                    self.force = random.randrange(1, 5000, 1)
                    self.force += 0.01
                else:
                    self.force = round(float(self.getForce()) * 9.81, 2)
                if not self.inActive:
                    self.forceLCD.display(self.force)
                    self.oldForce = self.force

                    # Update team dictionary and CSV file
                    if self.activeTeam[0].name() and not self.inActive:
                        self.teams[self.activeTeam[0].name()].append(self.force)
                        with open(os.path.join(csv_path, self.activeTeam[0].name() + ".csv"), "a+", newline='') as csvfile:
                            writer = csv.DictWriter(csvfile, fieldnames=['Sample', 'Force'])
                            csvfile.seek(0)
                            writer.writerow({'Sample': self.activeTeam[0].samples, 'Force': self.force})
                            self.activeTeam[0].samples += 1
                            csvfile.close()

                    # New max force found, update the force label and list
                    if self.force > self.maxForce:
                        self.maxForce = self.force
                        self.maxForceText.setText("Maximum Force: %.2f N" % self.maxForce)
                        if self.activeTeam[0].maxForce < self.maxForce:
                            self.activeTeam[0].maxForce = self.maxForce
                            self.activeTeam[0].setForce(self.force)

            # Display force graph
            if not self.start and self.loadNewGraph:
                data = QSplineSeries()
                data.setName(self.activeTeam[0].name())

                with open(os.path.join(csv_path, self.activeTeam[0].name() + '.csv'), "r", newline='') as file:
                    for line in file:
                        if "Sample" not in line:
                            s = line.split(",")
                            data.append(float(s[0]), float(s[1]))
                    file.close()

                maxForceline = QLineSeries()
                maxForceline.setName("Maxiumum Force")
                maxForceline.append(0.0, self.activeTeam[0].force())
                maxForceline.append(self.activeTeam[0].samples, self.activeTeam[0].force())

                force_chart = QChart()
                force_chart.addSeries(data)
                force_chart.addSeries(maxForceline)
                force_chart.setToolTip("{}".format(self.maxForce))
                force_chart.setTitle("Force vs. Time Graph for {}".format(self.activeTeam[0].name()))
                force_chart.createDefaultAxes()
                force_chart.axisY().setRange(0, self.activeTeam[0].force() + 10)
                force_chart.setTheme(2)
                self.chartView = QChartView(force_chart)
                self.chartView.setRenderHint(QPainter.Antialiasing)
                self.grid.addWidget(self.chartView, 1, 1, 1, 5)
                self.chartView.show()
                self.loadNewGraph = False

            # Rate at which the force value is updated. Limited by the serial interface. Faster update rates
            # may cause more invalid force data to be read.
            QtCore.QTimer.singleShot(200, lambda: self.updateForce())


class QListWidgetItem_Team(QListWidgetItem):
    """ Custom QListWidgetItem that allows for easy access to team name and maximum recorded force. Gets sorted by
    maximum recorded force """

    def __init__(self):
        super().__init__()
        self.samples = 1
        self.maxForce = 0

    def setForce(self, force):
        self.setText(self.name() + " - " + str(force))

    def force(self):
        r = re.compile("([0-9]*[.]){1}[0-9]+")
        return float(r.search(self.text()).group(0))

    def name(self):
        end = self.text().rfind(' -')
        return self.text()[0:end]

    # Redefinition of __lt__ allows sorting by force
    def __lt__(self, other):
        return self.force() > other.force()


def main():
    app = QApplication(sys.argv)
    print(sys.argv)

    if '-debug' not in sys.argv[1:]:
        # Detect COM port
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if "USB Serial Port" in p.description:
                match = re.search(r"COM\d", p.description)
                COM_PORT = match.group(0)

        ##############################################################
        #COM_PORT = UNCOMMENT AND SET COM PORT MANUALLY HERE IF NEEDED
        ##############################################################

        # Setup COM port
        ser = serial.Serial(COM_PORT, 115200, timeout=0.2)
        sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser), newline='\r\n')
        start_ = time.time()
        while time.time() < start_ + 1:
            trunk = ser.readline()

        # Start bridge crusher
        cMain = MainWindow(ser=ser, sio=sio)
    else:
        # Launch without serial data for testing
        cMain = MainWindow()

    sys.exit(app.exec_())

if __name__== '__main__':
    main()
