# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QLabel, QApplication, QGridLayout, QPushButton, QLineEdit)


class MainWindow(QWidget):

        def __init__(self):
            super().__init__()
            self.initUI()

        def initUI(self):
            self.setGeometry(300, 200, 600, 400)

            #LCD Widget to display the force
            force=1000.11
            forcelcd = QLCDNumber(7, self)

            #Push button to zero the scale
            zero = QPushButton('Zero Scale', self)

            #Textbox to enter in team name
            teaminput = QLineEdit()

            #Current highest force text
            maxforce = QLabel()

            grid = QGridLayout()
            grid.setColumnStretch(1, 1)
            grid.addWidget(forcelcd,0,1)
            grid.addWidget(zero,1,1)
            grid.addWidget(teaminput, 1,3)

            self.updateForce(forcelcd, force)
            self.setLayout(grid)
            self.showFullScreen()

        def keyPressEvent(self, e):
            if e.key() == Qt.Key_Escape:
                self.close()


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
