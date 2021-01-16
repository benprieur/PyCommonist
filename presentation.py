import os, sip
from os import listdir
from os.path import isfile, join

import exifread
from gps_location import get_exif_location

from ImageUpload import ImageUpload
from Upload import Upload

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
    QCheckBox
from constants import VERTICAL_TOP_SIZE, \
    VERTICAL_BOTTOM_SIZE, \
    HORIZONTAL_LEFT_SIZE, \
    HORIZONTAL_RIGHT_SIZE, \
    WIDTH_WIDGET, \
    WIDTH_WIDGET_RIGHT, \
    IMAGE_DIMENSION


'''
    generateSplitter
'''
def generateSplitter(mainWidget):

    mainWidget.hbox = QHBoxLayout()

    mainWidget.leftTopFrame = QFrame()
    mainWidget.leftTopFrame.setFrameShape(QFrame.StyledPanel)

    mainWidget.rightWidget = QWidget()
    mainWidget.rightWidget.resize(300, 300)
    mainWidget.layoutRight = QVBoxLayout()
    mainWidget.rightWidget.setLayout(mainWidget.layoutRight)

    mainWidget.scroll = QScrollArea()
    mainWidget.layoutRight.addWidget(mainWidget.scroll)
    mainWidget.scroll.setWidgetResizable(True)
    mainWidget.scrollContent = QWidget(mainWidget.scroll)

    mainWidget.scrollLayout = QVBoxLayout(mainWidget.scrollContent)
    mainWidget.scrollContent.setLayout(mainWidget.scrollLayout)
    mainWidget.scroll.setWidget(mainWidget.scrollContent)

    mainWidget.splitterLeft = QSplitter(Qt.Vertical)
    mainWidget.leftBottonFrame = QFrame()
    mainWidget.leftBottonFrame.setFrameShape(QFrame.StyledPanel)

    mainWidget.splitterLeft.addWidget(mainWidget.leftTopFrame)
    mainWidget.splitterLeft.addWidget(mainWidget.leftBottonFrame)
    mainWidget.splitterLeft.setSizes([VERTICAL_TOP_SIZE,VERTICAL_BOTTOM_SIZE])

    mainWidget.splitterCentral = QSplitter(Qt.Horizontal)
    mainWidget.splitterCentral.addWidget(mainWidget.splitterLeft)
    mainWidget.splitterCentral.addWidget(mainWidget.rightWidget)
    mainWidget.splitterCentral.setSizes([HORIZONTAL_LEFT_SIZE,HORIZONTAL_RIGHT_SIZE])

    mainWidget.hbox.addWidget(mainWidget.splitterCentral)

    mainWidget.setLayout(mainWidget.hbox)


'''
    generateLeftTopFrame
'''
def generateLeftTopFrame(mainWidget):

    mainWidget.layoutLeftTop = QFormLayout()
    mainWidget.layoutLeftTop.setFormAlignment(Qt.AlignTop)

    mainWidget.lblUserName = QLabel("Username: ")
    mainWidget.lblUserName.setAlignment(Qt.AlignLeft)
    mainWidget.lineEditUserName = QLineEdit()
    mainWidget.lineEditUserName.setFixedWidth(WIDTH_WIDGET)
    mainWidget.lineEditUserName.setAlignment(Qt.AlignLeft)
    mainWidget.lineEditUserName.setText("Benoît Prieur")
    mainWidget.layoutLeftTop.addRow(mainWidget.lblUserName, mainWidget.lineEditUserName)

    mainWidget.lblPassword = QLabel("Password: ")
    mainWidget.lblPassword.setAlignment(Qt.AlignLeft)
    mainWidget.lineEditPassword = QLineEdit()
    mainWidget.lineEditPassword.setFixedWidth(WIDTH_WIDGET)
    mainWidget.lineEditPassword.setAlignment(Qt.AlignLeft)
    mainWidget.lineEditPassword.setEchoMode(QLineEdit.Password)
    mainWidget.layoutLeftTop.addRow(mainWidget.lblPassword, mainWidget.lineEditPassword)

    mainWidget.lblWiki = QLabel("Wiki: ")
    mainWidget.lblWiki.setAlignment(Qt.AlignLeft)
    mainWidget.lineEditWiki = QLabel() #QLineEdit()
    mainWidget.lineEditWiki.setFixedWidth(WIDTH_WIDGET)
    mainWidget.lineEditWiki.setText("Wikimedia Commons")
    mainWidget.lineEditWiki.setAlignment(Qt.AlignLeft)
    mainWidget.layoutLeftTop.addRow(mainWidget.lblWiki, mainWidget.lineEditWiki)

    mainWidget.lblSource = QLabel("Source: ")
    mainWidget.lblSource.setAlignment(Qt.AlignLeft)
    mainWidget.lineEditSource = QLineEdit()
    mainWidget.lineEditSource.setFixedWidth(WIDTH_WIDGET)
    mainWidget.lineEditSource.setText("{{own}}")
    mainWidget.lineEditSource.setAlignment(Qt.AlignLeft)
    mainWidget.layoutLeftTop.addRow(mainWidget.lblSource, mainWidget.lineEditSource)

    mainWidget.lblDate = QLabel("Date: ")
    mainWidget.lblDate.setAlignment(Qt.AlignLeft)
    mainWidget.lineEditDate = QLineEdit()
    mainWidget.lineEditDate.setFixedWidth(WIDTH_WIDGET)
    mainWidget.lineEditDate.setAlignment(Qt.AlignLeft)
    mainWidget.layoutLeftTop.addRow(mainWidget.lblDate, mainWidget.lineEditDate)

    mainWidget.lblAuthor = QLabel("Author: ")
    mainWidget.lblAuthor.setAlignment(Qt.AlignLeft)
    mainWidget.lineEditAuthor = QLineEdit()
    mainWidget.lineEditAuthor.setFixedWidth(WIDTH_WIDGET)
    mainWidget.lineEditAuthor.setText("{{User:Benoît Prieur/Credit}}")
    mainWidget.lineEditAuthor.setAlignment(Qt.AlignLeft)
    mainWidget.layoutLeftTop.addRow(mainWidget.lblAuthor, mainWidget.lineEditAuthor)

    mainWidget.lblCategories = QLabel("Categories: ")
    mainWidget.lblCategories.setAlignment(Qt.AlignLeft)
    mainWidget.lineEditCategories = QLineEdit()
    mainWidget.lineEditCategories.setFixedWidth(WIDTH_WIDGET)
    mainWidget.lineEditCategories.setAlignment(Qt.AlignLeft)
    mainWidget.layoutLeftTop.addRow(mainWidget.lblCategories, mainWidget.lineEditCategories)

    mainWidget.lblLicense = QLabel("License: ")
    mainWidget.lblLicense.setAlignment(Qt.AlignLeft)
    mainWidget.lineEditLicense = QLineEdit()
    mainWidget.lineEditLicense.setFixedWidth(WIDTH_WIDGET)
    mainWidget.lineEditLicense.setText("{{self|cc-by-sa-4.0}}")
    mainWidget.lineEditLicense.setAlignment(Qt.AlignLeft)
    mainWidget.layoutLeftTop.addRow(mainWidget.lblLicense, mainWidget.lineEditLicense)

    mainWidget.lblDescription = QLabel("Description: ")
    mainWidget.lblDescription.setAlignment(Qt.AlignLeft)
    mainWidget.lineEditDescription = QPlainTextEdit()
    mainWidget.lineEditDescription.setFixedWidth(WIDTH_WIDGET)
    mainWidget.layoutLeftTop.addRow(mainWidget.lblDescription, mainWidget.lineEditDescription)

    mainWidget.leftTopFrame.setLayout(mainWidget.layoutLeftTop)


'''
    generateLeftBottomFrame
'''
def generateLeftBottomFrame(mainWidget):

    mainWidget.layoutLeftBottom = QVBoxLayout()

    '''Model for QTreeView'''
    mainWidget.modelTree = QFileSystemModel()
    mainWidget.modelTree.setRootPath(QDir.currentPath())
    mainWidget.modelTree.setFilter(QDir.Dirs) # Only directories

    ''' QTreeView '''
    mainWidget.treeLeftBottom = QTreeView()
    mainWidget.treeLeftBottom.setModel(mainWidget.modelTree)
    mainWidget.treeLeftBottom.setAnimated(False)
    mainWidget.treeLeftBottom.setIndentation(20)
    mainWidget.treeLeftBottom.selectionModel().selectionChanged.connect(mainWidget.onSelectFolder)
    mainWidget.layoutLeftBottom.addWidget(mainWidget.treeLeftBottom)
    mainWidget.leftBottonFrame.setLayout(mainWidget.layoutLeftBottom)


'''
    generateRightFrame
'''
def generateRightFrame(mainWidget, path):

    layout = mainWidget.scrollLayout
    print(layout)
    print(layout.count())

    while layout.count():
        print("destroy")
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()

    ''' Current upload'''
    mainWidget._currentUpload = Upload()
    mainWidget._currentUpload.path = path

    files = [f for f in listdir(path) if isfile(join(path, f))]
    for file in files:
        fullFilePath = os.path.join(path, file)
        if fullFilePath.endswith(".jpg"):

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

            ''' import? '''
            cbImport = QCheckBox("Import")
            localLeftLayout.addWidget(cbImport)
            localWidget.cbImport = cbImport

            ''' File Name of picture '''
            lblFileName = QLabel("Name: ")
            lblFileName.setAlignment(Qt.AlignLeft)
            lineEditFileName = QLineEdit()
            lineEditFileName.setFixedWidth(WIDTH_WIDGET_RIGHT)
            lineEditFileName.setText(file)
            lineEditFileName.setAlignment(Qt.AlignLeft)
            localLeftLayout.addRow(lblFileName, lineEditFileName)
            localWidget.lineEditFileName = lineEditFileName

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

            ''' EXIF '''
            f_exif = open(fullFilePath, 'rb')
            tags = exifread.process_file(f_exif)
            #print(tags)

            ''' Location'''
            # 'GPS GPSLatitude', 'GPS GPSLongitude'] # [45, 49, 339/25] [4, 55, 716/25]
            # 'GPS GPSImgDirection' 'GPS GPSLatitudeRef'
            lat, long = get_exif_location(tags)
            lblLocation = QLabel("Location: ")
            lblLocation.setAlignment(Qt.AlignLeft)
            lineEditLocation = QLineEdit()
            lineEditLocation.setFixedWidth(WIDTH_WIDGET_RIGHT)
            lineEditLocation.setText(str(lat) + ', ' + str(long))
            lineEditLocation.setAlignment(Qt.AlignLeft)
            localLeftLayout.addRow(lblLocation, lineEditLocation)
            localWidget.lineEditLocation = lineEditLocation

            ''' Date Time '''
            dt = tags['EXIF DateTimeOriginal'] # 2021:01:13 14:48:44
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

            mainWidget.scrollLayout.addWidget(localWidget)
            mainWidget._currentUpload.listImageUpload.append(localWidget)