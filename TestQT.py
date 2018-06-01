# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QVBoxLayout, QApplication, QGridLayout)


class MainWindow(QWidget):

        def __init__(self):
            super().__init__()
            self.initUI()

        def initUI(self):
            self.setGeometry(300, 200, 600, 400)
            force=1000.1
            forcelcd = QLCDNumber(6, self)

            grid = QGridLayout()
            grid.setColumnStretch(1, 4)
            #vbox = QVBoxLayout()
            grid.addWidget(forcelcd,0,1)

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
