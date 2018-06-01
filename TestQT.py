# -*- coding: utf-8 -*-

import sys
import random
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QLabel, QApplication, QGridLayout, QPushButton, QListWidget, QListWidgetItem, QLineEdit)


class MainWindow(QWidget):

        def __init__(self):
            super().__init__()
            self.initUI()

        def initUI(self):
            self.setGeometry(300, 200, 600, 400)
            self.grid = QGridLayout()
            self.teams = {}
            self.currentteam = [QListWidgetItem()]

            # LCD Widget to display the force
            force=1000.11
            forcelcd = QLCDNumber(7, self)

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
            #maxforcetxt.setAlignment(Qt.AlignCenter)
            self.maxforcetxt.setFont(QtGui.QFont("Times", 56))
            self.maxforcetxt.setText("Maximum Force: %f" % self.maxforce )

            # List of teams and scores
            self.teamlist = QListWidget()
            self.teamlist.itemDoubleClicked.connect(self.selectTeam)

            # Add widgets to grid and format
            self.grid.setColumnStretch(1, 5)
            self.grid.setColumnStretch(3, 2)
            self.grid.addWidget(self.maxforcetxt, 0,1)
            self.grid.addWidget(forcelcd,1,1)
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

            """
            if self.teamlist.count():
                for i in range(self.teamlist.count())
                if self.teams[team] > self.teamlist.item(i):
            """
            item = QListWidgetItem()
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

            # New max force found, update the label
            if force > self.maxforce:
                self.maxforce = force
                self.maxforcetxt.setText("Maximum Force: %f" % force)
                self.maxforcetxt.setStyleSheet("QLabel {background-color: red}")
                QtCore.QTimer.singleShot(250, lambda: self.maxforcetxt.setStyleSheet(""))

                #Update team in the list
                #str = self.currentteam[0].text()
                #end = str.rfind(' -')
                #teamstr = self.currentteam[0].text()[0:end]
                #print(teamstr)

                self.currentteam[0].setText(str(force))

            forcelcd.display(force)
            QtCore.QTimer.singleShot(350, lambda: self.updateForce(forcelcd, force))

def main():
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())


if __name__== '__main__':
    main()
