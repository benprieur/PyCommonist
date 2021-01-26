import sys, traceback
from UploadTool import UploadTool
from PyQt5.QtWidgets import QWidget, QStatusBar
import os, sip
from os import listdir
from os.path import isfile, join

import exifread
from gps_location import get_exif_location

from ImageUpload import ImageUpload

from PyQt5.QtCore import Qt, QRect
from PyQt5.Qt import QDir
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QHBoxLayout, \
    QFrame, \
    QSplitter, \
    QFormLayout, \
    QLabel, \
    QLineEdit, \
    QPlainTextEdit, \
    QVBoxLayout, \
    QFileSystemModel, \
    QTreeView, \
    QScrollArea, \
    QWidget, \
    QCheckBox, \
    QPushButton, \
    QStatusBar
from constants import VERTICAL_TOP_SIZE, \
    VERTICAL_BOTTOM_SIZE, \
    HORIZONTAL_LEFT_SIZE, \
    HORIZONTAL_RIGHT_SIZE, \
    WIDTH_WIDGET, \
    WIDTH_WIDGET_RIGHT, \
    IMAGE_DIMENSION, \
    STYLE_IMPORT_BUTTON, \
    STYLE_IMPORT_STATUS

class PyCommonist(QWidget):

    tool = None

    def __init__(self):
        super(PyCommonist, self).__init__()
        self._currentUpload = []
        self.initUI()
        self.threads = []
        self.workers = []


    def initUI(self):

        self.currentDirectoryPath = ''

        self.generateSplitter()
        self.generateLeftTopFrame()
        self.generateLeftBottomFrame()

        self.showMaximized()
        self.setWindowTitle('PyCommonist - Wikimedia Commons')
        self.show()

    '''
        onSelectFolder
    '''
    def onSelectFolder(self, selected, deselected):

        try:
            currentIndex = selected.indexes()[0]
            #print(currentIndex)
            #print(currentIndex.row())
            currentDirectoryPath = self.modelTree.filePath(currentIndex)
            print(currentDirectoryPath)

            self.currentDirectoryPath = currentDirectoryPath
            self.generateRightFrame()

            self.update()

        except:
            print("Something bad happened inside onSelectFolder function")
            traceback.print_exc()

    '''
        cbImportNoneStateChanged
    '''
    def cbImportNoneStateChanged(self):

        print (self.cbImportNone.isChecked())
        print(len(self._currentUpload))

        if self.cbImportNone.isChecked() and len(self._currentUpload) > 0:

            for element in self._currentUpload:
                element.cbImport.setCheckState(False)

    '''
        cbImportAllStateChanged
    '''
    def cbImportAllStateChanged(self):

        print (self.cbImportAll.isChecked())
        print(len(self._currentUpload))
        if self.cbImportAll.isChecked() and len(self._currentUpload) > 0:

            for element in self._currentUpload:
                element.cbImport.setCheckState(True)

    '''
        onClickImport
    '''
    def onClickImport(self):
        if (self.tool == None):
            self.tool = UploadTool()
        ret = self.tool.uploadImages(self)

    '''
        cleanThreads
    '''
    def cleanThreads(self):
        print("Clean threads")
        for thread in self.threads:
            print("Thread deletion")
            thread.wait()
            thread.quit()

    '''
        generateSplitter
    '''
    def generateSplitter(self):

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()

        self.leftTopFrame = QFrame()
        self.leftTopFrame.setFrameShape(QFrame.StyledPanel)

        self.rightWidget = QWidget()
        self.rightWidget.resize(300, 300)
        self.layoutRight = QVBoxLayout()
        self.rightWidget.setLayout(self.layoutRight)

        self.scroll = QScrollArea()
        self.layoutRight.addWidget(self.scroll)
        self.scroll.setWidgetResizable(True)
        self.scrollContent = QWidget(self.scroll)

        self.scrollLayout = QVBoxLayout(self.scrollContent)
        self.scrollContent.setLayout(self.scrollLayout)
        self.scroll.setWidget(self.scrollContent)

        self.splitterLeft = QSplitter(Qt.Vertical)
        self.leftBottonFrame = QFrame()
        self.leftBottonFrame.setFrameShape(QFrame.StyledPanel)

        self.splitterLeft.addWidget(self.leftTopFrame)
        self.splitterLeft.addWidget(self.leftBottonFrame)
        self.splitterLeft.setSizes([VERTICAL_TOP_SIZE,VERTICAL_BOTTOM_SIZE])

        ''' Horizontal Splitter '''
        self.splitterCentral = QSplitter(Qt.Horizontal)
        self.splitterCentral.addWidget(self.splitterLeft)
        self.splitterCentral.addWidget(self.rightWidget)
        self.splitterCentral.setSizes([HORIZONTAL_LEFT_SIZE,HORIZONTAL_RIGHT_SIZE])
        hbox.addWidget(self.splitterCentral)

        vbox.addLayout(hbox)

        ''' Status Bar '''
        self.statusBar = QStatusBar()
        self.statusBar.setFixedSize(800, 40)
        vbox.addWidget(self.statusBar)

        self.setLayout(vbox)

    '''
        generateLeftTopFrame
    '''
    def generateLeftTopFrame(self):

        self.layoutLeftTop = QFormLayout()
        self.layoutLeftTop.setFormAlignment(Qt.AlignTop)

        self.lblUserName = QLabel("Username: ")
        self.lblUserName.setAlignment(Qt.AlignLeft)
        self.lineEditUserName = QLineEdit()
        self.lineEditUserName.setFixedWidth(WIDTH_WIDGET)
        self.lineEditUserName.setAlignment(Qt.AlignLeft)
        self.lineEditUserName.setText("Benoît Prieur")
        self.layoutLeftTop.addRow(self.lblUserName, self.lineEditUserName)

        self.lblPassword = QLabel("Password: ")
        self.lblPassword.setAlignment(Qt.AlignLeft)
        self.lineEditPassword = QLineEdit()
        self.lineEditPassword.setFixedWidth(WIDTH_WIDGET)
        self.lineEditPassword.setAlignment(Qt.AlignLeft)
        self.lineEditPassword.setEchoMode(QLineEdit.Password)
        self.layoutLeftTop.addRow(self.lblPassword, self.lineEditPassword)

        self.lblSource = QLabel("Source: ")
        self.lblSource.setAlignment(Qt.AlignLeft)
        self.lineEditSource = QLineEdit()
        self.lineEditSource.setFixedWidth(WIDTH_WIDGET)
        self.lineEditSource.setText("{{own}}")
        self.lineEditSource.setAlignment(Qt.AlignLeft)
        self.layoutLeftTop.addRow(self.lblSource, self.lineEditSource)

        self.lblAuthor = QLabel("Author: ")
        self.lblAuthor.setAlignment(Qt.AlignLeft)
        self.lineEditAuthor = QLineEdit()
        self.lineEditAuthor.setFixedWidth(WIDTH_WIDGET)
        self.lineEditAuthor.setText("{{User:Benoît Prieur/Credit}}")
        self.lineEditAuthor.setAlignment(Qt.AlignLeft)
        self.layoutLeftTop.addRow(self.lblAuthor, self.lineEditAuthor)

        self.lblCategories = QLabel("Categories: ")
        self.lblCategories.setAlignment(Qt.AlignLeft)
        self.lineEditCategories = QLineEdit()
        self.lineEditCategories.setText("Photographs by Benoît Prieur|2021 images by Benoît Prieur")
        self.lineEditCategories.setFixedWidth(WIDTH_WIDGET)
        self.lineEditCategories.setAlignment(Qt.AlignLeft)
        self.layoutLeftTop.addRow(self.lblCategories, self.lineEditCategories)

        self.lblLicense = QLabel("License: ")
        self.lblLicense.setAlignment(Qt.AlignLeft)
        self.lineEditLicense = QLineEdit()
        self.lineEditLicense.setFixedWidth(WIDTH_WIDGET)
        self.lineEditLicense.setText("{{self|cc-by-sa-4.0}}")
        self.lineEditLicense.setAlignment(Qt.AlignLeft)
        self.layoutLeftTop.addRow(self.lblLicense, self.lineEditLicense)

        self.lblDescription = QLabel("Description: ")
        self.lblDescription.setAlignment(Qt.AlignLeft)
        self.lineEditDescription = QPlainTextEdit()
        self.lineEditDescription.setFixedWidth(WIDTH_WIDGET)
        self.layoutLeftTop.addRow(self.lblDescription, self.lineEditDescription)

        separationLeftTopFrame = QLabel()
        self.layoutLeftTop.addWidget(separationLeftTopFrame)

        ''' Button Import & None/All checkboxes'''
        importWidget = QWidget()
        importLayout = QHBoxLayout()
        importWidget.setLayout(importLayout)

        self.cbImportNone = QCheckBox("None")
        self.cbImportNone.stateChanged.connect(self.cbImportNoneStateChanged)

        self.cbImportAll = QCheckBox("All")
        self.cbImportAll.stateChanged.connect(self.cbImportAllStateChanged)

        self.btnImport = QPushButton("Import!")

        self.btnImport.clicked.connect(self.onClickImport)

        importLayout.addWidget(self.cbImportNone)
        importLayout.addWidget(self.cbImportAll)
        importLayout.addWidget(self.btnImport)
        self.layoutLeftTop.addWidget(importWidget)
        importWidget.setStyleSheet("border:1px solid #808080;");
        self.cbImportNone.setStyleSheet("border:0px;");
        self.cbImportAll.setStyleSheet("border:0px;");

        self.btnImport.setStyleSheet(STYLE_IMPORT_BUTTON)

        ''' Layout Association of the Left Top Frame'''
        self.leftTopFrame.setLayout(self.layoutLeftTop)


    '''
        generateLeftBottomFrame
    '''
    def generateLeftBottomFrame(self):

        self.layoutLeftBottom = QVBoxLayout()

        '''Model for QTreeView'''
        self.modelTree = QFileSystemModel()
        self.modelTree.setRootPath(QDir.currentPath())
        self.modelTree.setFilter(QDir.Dirs) # Only directories

        ''' QTreeView '''
        self.treeLeftBottom = QTreeView()
        self.treeLeftBottom.setModel(self.modelTree)
        self.treeLeftBottom.setAnimated(False)
        self.treeLeftBottom.setIndentation(10)
        self.treeLeftBottom.setColumnWidth(0, 300)
        self.treeLeftBottom.expandAll()
        self.treeLeftBottom.selectionModel().selectionChanged.connect(self.onSelectFolder)
        self.layoutLeftBottom.addWidget(self.treeLeftBottom)
        self.leftBottonFrame.setLayout(self.layoutLeftBottom)


    '''
        generateRightFrame
    '''
    def generateRightFrame(self):

        path = self.currentDirectoryPath
        self._currentUpload = []
        layout = self.scrollLayout

        print(layout)
        print(layout.count())

        while layout.count():
            print("destroy")
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        list_dir = os.listdir(path)
        files = [f for f in sorted(list_dir) if isfile(join(path, f))]
        for file in files:
            fullFilePath = os.path.join(path, file)
            if fullFilePath.endswith(".jpg") or fullFilePath.endswith(".png"):

                ''' Current image '''
                localWidget = ImageUpload()
                localLayout = QHBoxLayout()
                localLayout.setAlignment(Qt.AlignRight)
                localWidget.setLayout(localLayout)

                '''Local Left Widget'''
                localLeftWidget = QWidget()
                localLeftLayout = QFormLayout()
                localLeftLayout.setAlignment(Qt.AlignRight)
                localLeftWidget.setLayout(localLeftLayout)
                localLayout.addWidget(localLeftWidget)

                ''' import? + Import Status '''
                cbImport = QCheckBox("Import")
                lblUploadResult = QLabel()
                lblUploadResult.setStyleSheet(STYLE_IMPORT_STATUS)
                localLeftLayout.addRow(cbImport, lblUploadResult)
                localWidget.cbImport = cbImport
                localWidget.lblUploadResult = lblUploadResult

                ''' File Name of picture '''
                lblFileName = QLabel("Name: ")
                lblFileName.setAlignment(Qt.AlignLeft)
                lineEditFileName = QLineEdit()
                lineEditFileName.setFixedWidth(WIDTH_WIDGET_RIGHT)
                lineEditFileName.setText(file)
                lineEditFileName.setAlignment(Qt.AlignLeft)
                localLeftLayout.addRow(lblFileName, lineEditFileName)
                localWidget.lineEditFileName = lineEditFileName

                ''' Shadow Real FileName '''
                lblRealFileName = QLineEdit()
                lblRealFileName.setText(file)
                localWidget.lblRealFileName = lblRealFileName
                localWidget.lblRealFileName.isVisible = False

                ''' Description '''
                lblDescription = QLabel("Description: ")
                lblDescription.setAlignment(Qt.AlignLeft)
                lineEditDescription = QPlainTextEdit()
                lineEditDescription.setFixedWidth(WIDTH_WIDGET_RIGHT)
                localLeftLayout.addRow(lblDescription, lineEditDescription)
                localWidget.lineEditDescription = lineEditDescription

                ''' Categories '''
                lblCategories = QLabel("Categories: ")
                lblCategories.setAlignment(Qt.AlignLeft)
                lineEditCategories = QLineEdit()
                lineEditCategories.setFixedWidth(WIDTH_WIDGET_RIGHT)
                lineEditCategories.setAlignment(Qt.AlignLeft)
                localLeftLayout.addRow(lblCategories, lineEditCategories)
                localWidget.lineEditCategories = lineEditCategories

                tags = None
                try:
                    ''' EXIF '''
                    f_exif = open(fullFilePath, 'rb')
                    tags = exifread.process_file(f_exif)
                    #print(tags)
                except:
                    print("A problem with EXIF data reading")

                ''' Location'''
                # 'GPS GPSLatitude', 'GPS GPSLongitude'] # [45, 49, 339/25] [4, 55, 716/25]
                # 'GPS GPSImgDirection' 'GPS GPSLatitudeRef'
                lat = ''
                long = ''
                heading = ''
                try:
                    lat, long, heading = get_exif_location(tags)
                except:
                    print("A problem with EXIF data reading")

                lblLocation = QLabel("Location: ")
                lblLocation.setAlignment(Qt.AlignLeft)
                lineEditLocation = QLineEdit()
                lineEditLocation.setFixedWidth(WIDTH_WIDGET_RIGHT)
                if lat == None or long == None:
                    lineEditLocation.setText('')
                else:
                    lineEditLocation.setText(str(lat) + '|' + str(long) + "|heading:" + str(heading))
                lineEditLocation.setAlignment(Qt.AlignLeft)
                localLeftLayout.addRow(lblLocation, lineEditLocation)
                localWidget.lineEditLocation = lineEditLocation

                dt = None
                try:
                    ''' Date Time '''
                    dt = tags['EXIF DateTimeOriginal'] # 2021:01:13 14:48:44
                except:
                    print("A problem with EXIF data reading")

                print (dt)
                dt = str(dt)
                indexSpace = dt.find(" ")
                date = dt[0:indexSpace].replace(":", "-")
                time = dt[indexSpace+1:]

                lblDateTime = QLabel("Date Time: ")
                lblDateTime.setAlignment(Qt.AlignLeft)
                lineEditDateTime = QLineEdit()
                lineEditDateTime.setFixedWidth(WIDTH_WIDGET_RIGHT)
                lineEditDateTime.setText(date + ' ' + time)
                lineEditDateTime.setAlignment(Qt.AlignLeft)
                localLeftLayout.addRow(lblDateTime, lineEditDateTime)
                localWidget.lineEditDateTime = lineEditDateTime

                ''' Image itself '''
                label = QLabel()
                pixmap = QPixmap(fullFilePath)
                pixmapResize = pixmap.scaled(IMAGE_DIMENSION, IMAGE_DIMENSION)
                label.setPixmap(pixmapResize)
                localLayout.addWidget(label)
                localWidget.fullFilePath = fullFilePath

                self.scrollLayout.addWidget(localWidget)
                self._currentUpload.append(localWidget)