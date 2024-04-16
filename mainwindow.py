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
        
        # Initialize the QSettings object
        self.settings = QSettings("Demos", "BackupFileLog")
        
        # Check if the fileToBackup setting exists, otherwise set it to an empty string
        if self.settings.contains("fileToBackup"):
            self.fileToBackup = self.settings.value("fileToBackup")
        else: 
            self.fileToBackup = ''

        # Check if the backupPath setting exists, otherwise set it to the current working directory
        if self.settings.contains("backupPath"):
            self.backupPath = self.settings.value("backupPath")
        else:
            self.backupPath = os.getcwd()
        
        # Check if the backupTime setting exists, otherwise set it to 1 minute
        if self.settings.contains("backupTime"):
            self.backupTime = self.settings.value("backupTime")
        else:
            self.backupTime = 1

        print(self.fileToBackup)

        self.setWindowTitle("File Backup")
        self.setFixedSize(QSize(700,300))

        # Widgets
        self.titleLab = QLabel("<b>Backup file</b>")
        self.statusLab = QLabel()
        self.statusLab.setFixedSize(500,30)
        self.rightsLab = QLabel("Copyright© 2024 Filippo Spinelli. All rights reserved.")
        self.backupBtn = QPushButton("Run backup")
        self.backupBtn.setFixedSize(QSize(170,30))
        self.backupBtn.clicked.connect(self.onBackupBtnClicked)
        self.continuosBackupBtn = QPushButton("Run Continuous Backup")
        self.continuosBackupBtn.setFixedSize(QSize(170,30))
        self.continuosBackupBtn.clicked.connect(self.onContinuosBackupBtnClicked)
        self.searchFolderBtn = QPushButton("Select Folder")
        self.searchFolderBtn.setFixedSize(QSize(170,30))
        self.searchFolderBtn.clicked.connect(self.onSearchFolderBtnClicked)
        self.searchFilesBtn = QPushButton("Select File")
        self.searchFilesBtn.setFixedSize(QSize(170,30))
        self.searchFilesBtn.clicked.connect(self.onSearchFilesBtnClicked)
        # Selettore del tempo di backup continuo
        self.backupTimeSelector = QSpinBox()
        self.backupTimeSelector.setRange(1, 60)
        self.backupTimeSelector.setValue(self.backupTime)
        self.backupTimeSelector.setSuffix(" min")
        self.backupTimeSelector.setFixedSize(QSize(100, 30))
       
        self.folderPathLineEdit = QLineEdit()
        self.folderPathLineEdit.setFixedSize(QSize(350,30))
        self.folderPathLineEdit.setText(self.backupPath)
        self.fileNameLab = QLabel()
        self.fileNameLab.setFixedSize(QSize(350,30))
        if self.fileToBackup != '':
            self.fileNameLab.setText(self.fileToBackup)
        else:
            self.fileNameLab.setText("No File Selected")

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready", 1000)

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
        # comment if you want to disbale the automatic backup at the startup
        if self.fileToBackup != '':
            self.onContinuosBackupBtnClicked()
            

    def onSearchFolderBtnClicked(self):
        '''
        Event handler for the "Seleziona la cartella" button click.
        Opens a file dialog to select a backup folder and updates the folderPathLineEdit.
        '''
        dialog = QFileDialog()
        self.backupPath = dialog.getExistingDirectory(None, "Select Folder",dir=self.backupPath)
        self.folderPathLineEdit.setText(self.backupPath)

    def onSearchFilesBtnClicked(self):
        '''
        Event handler for the "Seleziona file" button click.
        Opens a file dialog to select files for backup and updates the fileNameLab.
        '''
        dialog = QFileDialog()
        files = dialog.getOpenFileNames(None, "Select file to backup")
        
        # Update the fileNameLab with the selected file
        if len(files[0]) > 1:
            self.fileNameLab.setText("More than one file selected")
        elif len(files[0]) == 0:
            self.fileNameLab.setText("No File selected")
        else:
            self.fileNameLab.setText(files[0][0])
            self.fileToBackup = files[0][0]
            
    def onContinuosBackupBtnClicked(self):
        '''
        Event handler for the "Esegui backup continuo" button click.
        Starts or stops continuous backup based on the current state of isContinuosBackupActive.
        '''
        self.backupTime = self.backupTimeSelector.value()
        self.settings.setValue("backupTime",  self.backupTime)
        self.settings.sync()

        if self.isContinuosBackupActive:
            self.isContinuosBackupActive = False
            self.continuosBackupBtn.setText("Run Continuous Backup")
            self.timer.stop()
            self.backupBtn.setEnabled(True)
            self.searchFilesBtn.setEnabled(True)
            self.searchFolderBtn.setEnabled(True)
            self.backupTimeSelector.setEnabled(True)
            self.folderPathLineEdit.setEnabled(True)
        else:
            self.isContinuosBackupActive = True
            # Change the label text to "Stop backup"
            self.continuosBackupBtn.setText("Stop Backup")
            self.backupBtn.setEnabled(False)
            self.searchFilesBtn.setEnabled(False)
            self.searchFolderBtn.setEnabled(False)
            self.backupTimeSelector.setEnabled(False)
            self.folderPathLineEdit.setEnabled(False)
            self.onBackupBtnClicked()
            self.timer = QTimer()
            self.timer.timeout.connect(self.onBackupBtnClicked)
            self.timer.start(self.backupTimeSelector.value()*60000)

    def onBackupBtnClicked(self):
        '''
        Event handler for the "Esegui backup" button click and continuous backup timer.
        Performs the backup operation and updates the status bar.
        '''
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
                print("Backup file " + fileName +" into folder: " + destination_path)
                newFilesPath.append(destination_path)
            
            if len(newFilesPath) > 0:
                statusText = "Last backup : "+ current_date
                self.statusBar.showMessage(statusText, self.backupTime*60000/2)

        else:
            print("No file selected")
            self.statusBar.showMessage("No file selected", 10000)

                  
      