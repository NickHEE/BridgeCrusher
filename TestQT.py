# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QLabel, QApplication, QGridLayout, QPushButton, QListWidget, QLineEdit)


class MainWindow(QWidget):

        def __init__(self):
            super().__init__()
            self.initUI()

        def initUI(self):
            self.setGeometry(300, 200, 600, 400)
            self.grid = QGridLayout()
            self.teams = {}
            self.teamlist = QListWidget()
            self.teamlist.setSortingEnabled(True)

            #LCD Widget to display the force
            force=1000.11
            forcelcd = QLCDNumber(7, self)

            #Push button to zero the scale
            zero = QPushButton('Zero Scale', self)

            #Textbox to enter in team name
            self.teaminput = QLineEdit()
            self.teaminput.setText('Enter team here')
            self.teaminput.returnPressed.connect(self.addTeam)

            #Current highest force text
            maxforce = 0000.00
            maxforcetxt = QLabel()
            #maxforcetxt.setAlignment(Qt.AlignCenter)
            maxforcetxt.setFont(QtGui.QFont("Times", 56))
            maxforcetxt.setText("Maximum Force: %f" % maxforce )

            #grid = QGridLayout()
            self.grid.setColumnStretch(1, 5)
            self.grid.setColumnStretch(3, 2)
            self.grid.addWidget(maxforcetxt, 0,1)
            self.grid.addWidget(forcelcd,1,1)
            self.grid.addWidget(zero,2,1)
            self.grid.addWidget(self.teamlist, 1, 3)
            self.grid.addWidget(self.teaminput, 2, 3)

            self.updateForce(forcelcd, force)
            self.setLayout(self.grid)
            self.showFullScreen()

        def keyPressEvent(self, e):
            if e.key() == Qt.Key_Escape:
                self.close()

        def addTeam(self):
            team = self.teaminput.text()
            self.teaminput.setText("")
            self.teams[team] = 0000.00

            """
            if self.teamlist.count():
                for i in range(self.teamlist.count())
                if self.teams[team] > self.teamlist.item(i):
            """

            self.teamlist.addItem(team + " - " + str(self.teams[team]))


        def updateForce(self, forcelcd, force):
            force += 1
            forcelcd.display(force)
            QtCore.QTimer.singleShot(100, lambda: self.updateForce(forcelcd, force))
            

def main():
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())


if __name__== '__main__':
    main()
