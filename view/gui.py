#!/usr/bin/env python3
# coding: utf-8

import sys
import typing
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QFormLayout, QTextEdit, QWidget
from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QHBoxLayout, QFrame
from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox, QAbstractSpinBox, QComboBox, QCheckBox
from PyQt5.QtWidgets import QPushButton, QLabel, QMessageBox
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget, QHeaderView
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, QObject, QThread, QRunnable, QThreadPool
import pandas as pd
import numpy as np
import signal
import re
import sys
import csv

class Assets():
    def __init__(self, file_name: str):
        f_dataframe = []
        try:
            f_dataframe = pd.read_csv(file_name)
        except IOError:
            raise Exception("Assets file not found.")

        f_header = f_dataframe.columns.tolist()
        self.f = f_dataframe.fillna('').to_numpy()
        self.f = np.vstack((f_header, self.f))

class Accounts():
    def __init__(self, file_name: str):
        self.f_dataframe = []
        try:
            self.f_dataframe = pd.read_csv(file_name)
        except IOError:
            raise Exception("Accounts file not found.")

        f_header = self.f_dataframe.columns.tolist()
        self.f = self.f_dataframe.fillna('').to_numpy()
        self.f = np.vstack((f_header, self.f))

    def get_account_ids_and_names(self):
        return list(set(zip(self.f_dataframe['Name'].tolist(), self.f_dataframe['Id'].tolist())))


"""
class DragDropTable(QTableWidget):
    def __init__(self, parent):
        super(DragDropTable, self).__init__(parent)
        self.setAcceptDrops(True)
        self.viewport().installEventFilter(self)
        types = ['text/uri-list']
        types.extend(self.mimeTypes())
        self.mimeTypes = lambda: types
        self.setRowCount(0)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super(DragDropTable, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        super(DragDropTable, self).dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                print(str(url.toLocalFile()))
            event.acceptProposedAction()
        else:
            super(DragDropTable,self).dropEvent(event)

    def createMainTable(self, assets, account_ids_names):
        dropdowns = ['AccountId']
        self.setRowCount(len(assets) - 1)  
        self.setColumnCount(len(assets[0]))
        self.setHorizontalHeaderLabels(assets[0])
        for i in range(len(assets[0])):
            if assets[0][i] in dropdowns:
                for j in range(1, len(assets)):
                    combobox = QComboBox()
                    self.setCellWidget(j - 1, i, combobox)
                    for id in account_ids_names:
                        combobox.addItem(id[0])
                        
            else:
                for j in range(1, len(assets)):
                    item = QTableWidgetItem(assets[j][i])
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                    self.setItem(j - 1, i, item)

        #Table will fit the screen horizontally
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
"""


#Main Window
class App(QWidget):
    def __init__(self):
        super().__init__()
        self.assets = Assets('assets.csv')
        self.accounts = Accounts('distributors_and_child_accounts.csv')
        self.title = 'Inventory Tracker'
        self.left = 0
        self.top = 0
        self.width = 1600
        self.height = 900
   
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createMainTable()
        self.createSideTable()
        self.createButtons()
        self.createNewAccount()
   
        self.main_layout = QVBoxLayout()
        self.lower_layout = QGridLayout()
        self.button_layout = QGridLayout()

        self.button_layout.addWidget(self.save_button, 0, 0)
        self.button_layout.addWidget(self.undo_button, 0, 1)
        self.button_layout.addWidget(self.undo_all_button, 0, 2)

        self.lower_layout.addWidget(self.tableSideWidget, 1, 1)
        self.lower_layout.addWidget(self.account_frame, 1, 0)
        self.main_layout.addLayout(self.lower_layout)

        self.main_layout.addWidget(self.main_table)
        self.main_layout.addLayout(self.button_layout)



        self.setLayout(self.main_layout)
   
        #Show window
        self.show()

    
    def createButtons(self):
        self.save_button = QPushButton('Save')
        self.undo_button = QPushButton('Undo')
        self.undo_all_button = QPushButton('Undo All')

    
    def createMainTable(self):
        self.main_table = QTableWidget()
        assets = self.assets.f
        account_ids_names = self.accounts.f
        dropdowns = ['AccountId']
        self.main_table.setRowCount(len(assets) - 1)  
        self.main_table.setColumnCount(len(assets[0]))
        self.main_table.setHorizontalHeaderLabels(assets[0])
        for i in range(len(assets[0])):
            if assets[0][i] in dropdowns:
                for j in range(1, len(assets)):
                    combobox = QComboBox()
                    self.main_table.setCellWidget(j - 1, i, combobox)
                    default_value = assets[j][1]
                    combobox.addItem(default_value)
                    for id in account_ids_names:
                        if id[0] != default_value and id[0] != 'Id':
                            combobox.addItem(id[0])

            else:
                for j in range(1, len(assets)):
                    item = QTableWidgetItem(assets[j][i])
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                    self.main_table.setItem(j - 1, i, item)

        #Table will fit the screen horizontally
        self.main_table.horizontalHeader().setStretchLastSection(True)
        self.main_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        
    def createSideTable(self):
        self.tableSideWidget = QTableWidget()
        dropdowns = ['AccountId']
        account_ids_names = self.accounts.get_account_ids_and_names()
        self.tableSideWidget.setRowCount(len(account_ids_names))  
        self.tableSideWidget.setColumnCount(len(account_ids_names[0]))
        self.tableSideWidget.setMaximumWidth(600)
        self.tableSideWidget.setHorizontalHeaderLabels(['Id', 'Name'])
        for i in range(len(account_ids_names[0])):
            for j in range(len(account_ids_names)):
                self.tableSideWidget.setItem(j, i, QTableWidgetItem(account_ids_names[j][i]))

        #Table will fit the screen horizontally
        self.tableSideWidget.horizontalHeader().setStretchLastSection(True)
        self.tableSideWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        
    def createNewAccount(self):
        self.account_frame = QFrame()
        self.account_frame.setMaximumHeight(200)
        self.account_frame.setMaximumWidth(500)
        title_label = QLabel("Add New Account")
        save_account_button = QPushButton("Save Account")
        """
        self.account_frame.setStyleSheet("border-color: grey;"
                                   "border-width: 1;"
                                   "border-radius: 3;"
                                   "border-style: solid;"
                                   )
        """
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        account_name_edit = QTextEdit()
        description_edit = QTextEdit()
        shipping_poc = QTextEdit()
        technical_poc = QTextEdit()

        self.formLayout = QFormLayout()
        self.formLayout.addWidget(title_label)
        self.formLayout.addRow(self.tr("&Account Name:"), account_name_edit)
        self.formLayout.addRow(self.tr("&Description:"), description_edit)
        self.formLayout.addRow(self.tr("&Shipping POC:"), shipping_poc)
        self.formLayout.addRow(self.tr("&Technical POC:"), technical_poc)
        self.formLayout.addWidget(save_account_button)

        self.account_frame.setLayout(self.formLayout)







        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())