# -*- coding: utf-8 -*-

import sys
import random
import re
import csv
import os
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QLabel, QApplication, QGridLayout, QPushButton, QListWidget, QListWidgetItem, QLineEdit)
from PyQt5.QtGui import QPixmap



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

            # Push buttons for zeroing, resetting and exporting
            zero = QPushButton('Zero Scale', self)
            clearmax = QPushButton('Reset', self)
            clearmax.clicked.connect(self.reset)
            export = QPushButton('Export', self)
            export.clicked.connect(self.exportTeams)

            # Textbox to enter in team name
            self.teaminput = QLineEdit()
            self.teaminput.setText('Enter team here')
            self.teaminput.returnPressed.connect(self.addTeam)

            # Current highest force text
            self.maxforce = 0000.00
            self.maxforcetxt = QLabel()
            self.maxforcetxt.setFont(QtGui.QFont("Times", 52))
            self.maxforcetxt.setText("Maximum Force: %f" % self.maxforce )

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
            self.grid.setColumnStretch(1, 4)
            self.grid.setColumnStretch(2, 4)
            self.grid.setColumnStretch(3, 4)
            self.grid.setRowStretch(1,6)
            self.grid.setRowStretch(0,2)
            self.grid.setRowStretch(0, 1)

            self.grid.addWidget(self.maxforcetxt, 0, 1)
            self.grid.addWidget(self.EGBC, 0, 4)
            self.grid.addWidget(forcelcd,1,1,1,3)
            self.grid.addWidget(zero,2,1)
            self.grid.addWidget(clearmax, 2, 2)
            self.grid.addWidget(export, 2, 3)
            self.grid.addWidget(self.teamlist, 1, 4)
            self.grid.addWidget(self.teaminput, 2, 4)

            self.updateForce(forcelcd, force)
            self.setLayout(self.grid)
            print(self.teaminput.width())
            self.showFullScreen()

        def keyPressEvent(self, e):
            if e.key() == Qt.Key_Escape:
                self.close()

        def reset(self):
            self.maxforce = 0000.00
            self.maxforcetxt.setText(str("Maximum Force: %.2f" % self.maxforce))


        def addTeam(self):
            team = self.teaminput.text()
            print(team)
            if team and team != "Enter team here":
                self.teaminput.setText("")
                self.teams[team] = [0000.00,]

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

        def exportTeams(self):
            #print([self.teams[team] for team in self.teams])

            for team in self.teams:
                sample = 0;
                with open(team + '.csv', "w", newline='') as csvfileout:
                    writer = csv.DictWriter(csvfileout, fieldnames=['Sample', 'Force'])
                    writer.writeheader()
                    for samples in self.teams[team]:
                        writer.writerow({'Sample': sample, 'Force': samples})
                        sample+=1
                csvfileout.close()

        def updateForce(self, forcelcd, force):
            #########################################
            #Code for getting force from serial here
            #########################################

            # Generate some random force values for testing
            force = random.randrange(100, 5000, 1)
            force += 0.01

            # Update team dictionary and CSV file
            if self.currentteam[0].name():
                self.teams[self.currentteam[0].name()].append(force)

                with open(self.currentteam[0].name() + ".csv", "a+", newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=['Sample', 'Force'])
                    samplenum = sum(1 for line in csvfile)
                    writer.writerow({'Sample': samplenum, 'Force': force})
                    csvfile.close()

            # New max force found, update the force label and list
            if force > self.maxforce:
                self.maxforce = force
                self.maxforcetxt.setText("Maximum Force: %.2f" % force)
                self.maxforcetxt.setStyleSheet("QLabel {background-color: red}")
                QtCore.QTimer.singleShot(250, lambda: self.maxforcetxt.setStyleSheet(""))
                self.currentteam[0].setForce(force)

            forcelcd.display(force)
            QtCore.QTimer.singleShot(350, lambda: self.updateForce(forcelcd, force))


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
    ex = MainWindow()
    sys.exit(app.exec_())


if __name__== '__main__':
    main()
