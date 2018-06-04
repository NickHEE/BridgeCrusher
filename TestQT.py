# -*- coding: utf-8 -*-

import sys
import random
import re
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QLabel, QApplication, QGridLayout, QPushButton, QListWidget, QListWidgetItem, QLineEdit)


class MainWindow(QWidget):

        def __init__(self):
            super().__init__()
            self.initUI()

        def initUI(self):
            self.setGeometry(300, 200, 600, 400)
            self.grid = QGridLayout()
            self.teams = {}
            self.currentteam = [QListWidgetItem_Team()]

            # LCD Widget to display the force
            force=1000.11
            forcelcd = QLCDNumber(7, self)
            forcelcd.setFrameStyle(3)

            # Push buttons for zeroing and reseting
            zero = QPushButton('Zero Scale', self)
            clearmax = QPushButton('Reset', self)
            clearmax.clicked.connect(self.reset)

            # Textbox to enter in team name
            self.teaminput = QLineEdit()
            self.teaminput.setText('Enter team here')
            self.teaminput.returnPressed.connect(self.addTeam)

            # Current highest force text
            self.maxforce = 0000.00
            self.maxforcetxt = QLabel()
            self.maxforcetxt.setFont(QtGui.QFont("Times", 48))
            self.maxforcetxt.setText("Maximum Force: %f" % self.maxforce )

            # List of teams and scores
            self.teamlist = QListWidget()
            #self.teamlist.setStyleSheet("QListWidget::item::selected {background-color: green;}")
            self.teamlist.setSortingEnabled(True)
            self.teamlist.itemDoubleClicked.connect(self.selectTeam)

            # Add widgets to grid and format
            self.grid.setColumnStretch(1, 4)
            self.grid.setColumnStretch(2, 4)
            self.grid.setColumnStretch(3, 4)
            self.grid.setRowStretch(1,6)
            self.grid.setRowStretch(0,2)
            self.grid.setRowStretch(0, 1)

            self.grid.addWidget(self.maxforcetxt, 0,1)
            self.grid.addWidget(forcelcd,1,1,1,2)
            self.grid.addWidget(zero,2,1)
            self.grid.addWidget(clearmax, 2,2)
            self.grid.addWidget(self.teamlist, 1, 3)
            self.grid.addWidget(self.teaminput, 2, 3)

            self.updateForce(forcelcd, force)
            self.setLayout(self.grid)
            self.showFullScreen()

        def keyPressEvent(self, e):
            if e.key() == Qt.Key_Escape:
                self.close()

        def reset(self):
            self.maxforce = 0000.00
            self.maxforcetxt.setText(str("Maximum Force: %f" % self.maxforce))


        def addTeam(self):
            team = self.teaminput.text()
            self.teaminput.setText("")
            self.teams[team] = 0000.00

            item = QListWidgetItem_Team()
            item.setText(team + " - " + str(self.teams[team]))
            item.setFont(QtGui.QFont("Times", 32))

            self.teamlist.addItem(item)

        def selectTeam(self):
            self.currentteam = self.teamlist.selectedItems()

        def updateForce(self, forcelcd, force):
            #########################################
            #Code for getting force from serial here
            #########################################

            # Generate some random force values for testing
            force = random.randrange(100, 5000, 1)
            force += 0.01

            # New max force found, update the force label and list
            if force > self.maxforce:
                self.maxforce = force
                self.maxforcetxt.setText("Maximum Force: %f" % force)
                self.maxforcetxt.setStyleSheet("QLabel {background-color: red}")
                QtCore.QTimer.singleShot(250, lambda: self.maxforcetxt.setStyleSheet(""))
                self.currentteam[0].setForce(force)

            forcelcd.display(force)
            QtCore.QTimer.singleShot(350, lambda: self.updateForce(forcelcd, force))


class QListWidgetItem_Team(QListWidgetItem):

    def setForce(self, force):
        end = self.text().rfind(' -')
        name = self.text()[0:end]
        self.setText(name + " - " + str(force))

    def force(self):
        r = re.compile("([0-9]*[.]){1}[0-9]+")
        return float(r.search(self.text()).group(0))

    def __lt__(self, other):
        return self.force() > other.force()


def main():
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())


if __name__== '__main__':
    main()
