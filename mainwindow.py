# -*- coding: utf-8 -*-
from PySide6.QtCore import (QRect, QDate,
    QSize, Slot, Qt, QTimer,QSettings)
from PySide6.QtWidgets import (QMainWindow,QSpinBox,QFileDialog,QLineEdit, QTableWidget,QPushButton, QSizePolicy, QStatusBar, QWidget, QHBoxLayout,QGridLayout, QVBoxLayout,QLabel)
from PySide6.QtGui import  QPixmap, QIcon
import qdarktheme
import os
import pandas as pd
import shutil
from datetime import datetime, timedelta


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        '''
            Initialization of the Main Window
        '''
        super().__init__()
        
        #initialize the QSettings object
        self.settings = QSettings("Demos", "BackupFileLog")
        if self.settings.contains("fileToBackup"):
            self.fileToBackup = self.settings.value("fileToBackup")
        else: 
            self.fileToBackup = ''

        if self.settings.contains("backupPath"):
            self.backupPath = self.settings.value("backupPath")
        else:
            self.backupPath = os.getcwd()
        
        if self.settings.contains("backupTime"):
            self.backupTime = self.settings.value("backupTime")
        else:
            self.backupTime = 1

        print(self.fileToBackup)

        self.setWindowTitle("Backup File Log")
        self.setFixedSize(QSize(700,300))

        # widgets
        self.titleLab = QLabel("<b>Backup file</b>")
        self.statusLab = QLabel()
        self.statusLab.setFixedSize(500,30)
        self.rightsLab = QLabel("Copyright© 2024 Demos S.R.L. Tutti i diritti riservati.")
        self.backupBtn = QPushButton("Esegui backup")
        self.backupBtn.setFixedSize(QSize(170,30))
        self.backupBtn.clicked.connect(self.onBackupBtnClicked)
        self.continuosBackupBtn = QPushButton("Esegui backup continuo")
        self.continuosBackupBtn.setFixedSize(QSize(170,30))
        self.continuosBackupBtn.clicked.connect(self.onContinuosBackupBtnClicked)
        self.searchFolderBtn = QPushButton("Seleziona la cartella")
        self.searchFolderBtn.setFixedSize(QSize(170,30))
        self.searchFolderBtn.clicked.connect(self.onSearchFolderBtnClicked)
        self.searchFilesBtn = QPushButton("Seleziona file")
        self.searchFilesBtn.setFixedSize(QSize(170,30))
        self.searchFilesBtn.clicked.connect(self.onSearchFilesBtnClicked)
        #Selettore del tempo di backup continuo
        self.backupTimeSelector = QSpinBox()
        self.backupTimeSelector.setRange(1, 60)
        self.backupTimeSelector.setValue(self.backupTime)
        self.backupTimeSelector.setSuffix(" minuti")
        self.backupTimeSelector.setFixedSize(QSize(100, 30))
       

        self.folderPathLineEdit = QLineEdit()
        self.folderPathLineEdit.setFixedSize(QSize(350,30))
        self.folderPathLineEdit.setText(self.backupPath)
        self.fileNameLab = QLabel()
        self.fileNameLab.setFixedSize(QSize(350,30))
        if self.fileToBackup != '':
            self.fileNameLab.setText(self.fileToBackup)
        else:
            self.fileNameLab.setText("Nessun File selezionato")

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Pronto", 1000)

        self.wrapperLayout = QVBoxLayout()

        self.backupLayout = QGridLayout()
        self.backupLayout.addWidget(self.fileNameLab,0,0,alignment=Qt.AlignmentFlag.AlignLeft)
        self.backupLayout.addWidget(self.searchFilesBtn,0,2)
        self.backupLayout.addWidget(self.folderPathLineEdit,1,0,alignment=Qt.AlignmentFlag.AlignLeft)
        self.backupLayout.addWidget(self.searchFolderBtn,1,2)
        
        self.backupLayout.addWidget(self.backupBtn,2,2,alignment=Qt.AlignmentFlag.AlignRight)
        self.backupLayout.addWidget(self.backupTimeSelector, 3, 1, alignment=Qt.AlignmentFlag.AlignRight)
        self.backupLayout.addWidget(self.continuosBackupBtn,3,2,alignment=Qt.AlignmentFlag.AlignRight)
        
        self.wrapperLayout.addWidget(self.rightsLab,alignment=Qt.AlignmentFlag.AlignRight)
        self.wrapperLayout.addWidget(self.titleLab)
        self.wrapperLayout.addLayout(self.backupLayout)
        self.wrapperLayout.addWidget(self.statusLab)
        self.wrapperLayout.addWidget(self.rightsLab)


        widget = QWidget()
        widget.setLayout(self.wrapperLayout)
        self.setCentralWidget(widget)

        self.isContinuosBackupActive = False

        if self.fileToBackup != '':
            self.onContinuosBackupBtnClicked()
            

    def onSearchFolderBtnClicked(self):
        dialog = QFileDialog()
        self.backupPath = dialog.getExistingDirectory(None, "Seleziona la cartella",dir=self.backupPath)
        self.folderPathLineEdit.setText(self.backupPath)

    def onSearchFilesBtnClicked(self):
        dialog = QFileDialog()
        files = dialog.getOpenFileNames(None, "Seleziona i file da backup")
        #il nome del file lo scrivo in fileNameLab
        if len(files[0]) > 1:
            self.fileNameLab.setText("Troppi file selezionati")
        elif len(files[0]) == 0:
            self.fileNameLab.setText("Nessun file selezionato")
        else:
            self.fileNameLab.setText(files[0][0])
            self.fileToBackup = files[0][0]
            
    def onContinuosBackupBtnClicked(self):
        
        self.backupTime = self.backupTimeSelector.value()
        self.settings.setValue("backupTime",  self.backupTime)
        self.settings.sync()

        if self.isContinuosBackupActive:
            self.isContinuosBackupActive = False
            self.continuosBackupBtn.setText("Esegui backup continuo")
            self.timer.stop()
            self.backupBtn.setEnabled(True)
            self.searchFilesBtn.setEnabled(True)
            self.searchFolderBtn.setEnabled(True)
            self.backupTimeSelector.setEnabled(True)
        else:
            self.isContinuosBackupActive = True
            #Cambia il nome della label in Stop backup
            self.continuosBackupBtn.setText("Stop backup")
            self.backupBtn.setEnabled(False)
            self.searchFilesBtn.setEnabled(False)
            self.searchFolderBtn.setEnabled(False)
            self.backupTimeSelector.setEnabled(False)
            self.onBackupBtnClicked()
            self.timer = QTimer()
            self.timer.timeout.connect(self.onBackupBtnClicked)
            self.timer.start(self.backupTimeSelector.value()*60000)

    def onBackupBtnClicked(self):
        
        self.settings.setValue("fileToBackup", self.fileToBackup)
        self.settings.setValue("backupPath", self.backupPath)
        self.settings.sync()

        current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        newFilesPath = []
        
        if self.fileToBackup != '':

            fileName = os.path.basename(self.fileToBackup).split('\\')[-1]

            destination_path = self.backupPath + "/" + fileName

            shutil.copy(self.fileToBackup, destination_path)

            if os.path.exists(destination_path):
                print("Backup del file " + fileName +" nella cartella: " + destination_path)
                newFilesPath.append(destination_path)
            
            if len(newFilesPath) > 0:
                statusText = "Ultimo backup : "+ current_date
                self.statusBar.showMessage(statusText, self.backupTime*60000/2)

        else:
            print("Nessun file selezionato")
            self.statusBar.showMessage("Nessun file selezionato", 10000)

                  
      