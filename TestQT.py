# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QBrush

class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Event handler')
        #self.show()
        self.frameSize()
        self.showFullScreen()
        #print(self.width())

    def drawRectangles(self, qp):
        col = QColor(0, 0, 0)
        col.setNamedColor('#d4d4d4')
        qp.setPen(col)

        qp.setBrush(QColor(200, 0, 0))
        qp.drawRect(10, 15, 90, 60)

        qp.setBrush(QColor(255, 80, 0, 160))
        qp.drawRect(130, 15, 90, 60)

        qp.setBrush(QColor(25, 0, 90, 200))
        qp.drawRect(250, 15, 90, 60)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())



"""
import sys
from PyQt5 import QtGui,QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QSlider, QLabel,
    QVBoxLayout, QApplication, QGridLayout)

class Example(QWidget):

        def __init__(self):
              super().__init__()
              self.initUI()

        def initUI(self):
            voltage=12 #e.g. I get the value of voltage is 12v
            lcd = QLCDNumber(self)
            lcd.display(voltage)

            # after 5 seconds (5000 milliseconds), call self.updateLabel
            QtCore.QTimer.singleShot(500, lambda: self.updateLabel(lcd, voltage))


            grid = QGridLayout()
            vbox = QVBoxLayout()
            vbox.addWidget(lcd)

            self.setLayout(grid)
            self.setGeometry(300,200,600,400)
            self.setWindowTitle("battery status")
            self.showFullScreen()

        def keyPressEvent(self, e):
            if e.key() == Qt.Key_Escape:
                self.close()


        def updateLabel(self, lcd, v):
            # change the following line to retrieve the new voltage from the device
            v = v + 1
            lcd.display(v)
            QtCore.QTimer.singleShot(5, lambda: self.updateLabel(lcd, v))
            

def main():

         app = QApplication(sys.argv)
         ex = Example()
         sys.exit(app.exec_())

if __name__=='__main__':
         main()
"""