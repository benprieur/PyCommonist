import os, sip
from os import listdir
from os.path import isfile, join

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
    QWidget

from constants import VERTICAL_TOP_SIZE, \
    VERTICAL_BOTTOM_SIZE, \
    HORIZONTAL_LEFT_SIZE, \
    HORIZONTAL_RIGHT_SIZE


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
    mainWidget.lineEditUserName.setFixedWidth(200)
    mainWidget.lineEditUserName.setAlignment(Qt.AlignLeft)
    mainWidget.lineEditUserName.setText("Benoît Prieur")
    mainWidget.layoutLeftTop.addRow(mainWidget.lblUserName, mainWidget.lineEditUserName)

    mainWidget.lblPassword = QLabel("Password: ")
    mainWidget.lblPassword.setAlignment(Qt.AlignLeft)
    mainWidget.lineEditPassword = QLineEdit()
    mainWidget.lineEditPassword.setFixedWidth(200)
    mainWidget.lineEditPassword.setAlignment(Qt.AlignLeft)
    mainWidget.lineEditPassword.setEchoMode(QLineEdit.Password)
    mainWidget.layoutLeftTop.addRow(mainWidget.lblPassword, mainWidget.lineEditPassword)

    mainWidget.lblWiki = QLabel("Wiki: ")
    mainWidget.lblWiki.setAlignment(Qt.AlignLeft)
    mainWidget.lineEditWiki = QLabel() #QLineEdit()
    mainWidget.lineEditWiki.setFixedWidth(200)
    mainWidget.lineEditWiki.setText("Wikimedia Commons")
    mainWidget.lineEditWiki.setAlignment(Qt.AlignLeft)
    mainWidget.layoutLeftTop.addRow(mainWidget.lblWiki, mainWidget.lineEditWiki)

    mainWidget.lblSource = QLabel("Source: ")
    mainWidget.lblSource.setAlignment(Qt.AlignLeft)
    mainWidget.lineEditSource = QLineEdit()
    mainWidget.lineEditSource.setFixedWidth(200)
    mainWidget.lineEditSource.setText("{{own}}")
    mainWidget.lineEditSource.setAlignment(Qt.AlignLeft)
    mainWidget.layoutLeftTop.addRow(mainWidget.lblSource, mainWidget.lineEditSource)

    mainWidget.lblDate = QLabel("Date: ")
    mainWidget.lblDate.setAlignment(Qt.AlignLeft)
    mainWidget.lineEditDate = QLineEdit()
    mainWidget.lineEditDate.setFixedWidth(200)
    mainWidget.lineEditDate.setAlignment(Qt.AlignLeft)
    mainWidget.layoutLeftTop.addRow(mainWidget.lblDate, mainWidget.lineEditDate)

    mainWidget.lblAuthor = QLabel("Author: ")
    mainWidget.lblAuthor.setAlignment(Qt.AlignLeft)
    mainWidget.lineEditAuthor = QLineEdit()
    mainWidget.lineEditAuthor.setFixedWidth(200)
    mainWidget.lineEditAuthor.setText("{{User:Benoît Prieur/Credit}}")
    mainWidget.lineEditAuthor.setAlignment(Qt.AlignLeft)
    mainWidget.layoutLeftTop.addRow(mainWidget.lblAuthor, mainWidget.lineEditAuthor)

    mainWidget.lblCategories = QLabel("Categories: ")
    mainWidget.lblCategories.setAlignment(Qt.AlignLeft)
    mainWidget.lineEditCategories = QLineEdit()
    mainWidget.lineEditCategories.setFixedWidth(200)
    mainWidget.lineEditCategories.setAlignment(Qt.AlignLeft)
    mainWidget.layoutLeftTop.addRow(mainWidget.lblCategories, mainWidget.lineEditCategories)

    mainWidget.lblLicense = QLabel("License: ")
    mainWidget.lblLicense.setAlignment(Qt.AlignLeft)
    mainWidget.lineEditLicense = QLineEdit()
    mainWidget.lineEditLicense.setFixedWidth(200)
    mainWidget.lineEditLicense.setText("{{self|cc-by-sa-4.0}}")
    mainWidget.lineEditLicense.setAlignment(Qt.AlignLeft)
    mainWidget.layoutLeftTop.addRow(mainWidget.lblLicense, mainWidget.lineEditLicense)

    mainWidget.lblDescription = QLabel("Description: ")
    mainWidget.lblDescription.setAlignment(Qt.AlignLeft)
    mainWidget.lineEditDescription = QPlainTextEdit()
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

    files = [f for f in listdir(path) if isfile(join(path, f))]

    for file in files:
        fullFilePath = os.path.join(path, file)
        if fullFilePath.endswith(".jpg"):

            localWidget = QWidget()
            localLayout = QHBoxLayout()
            localLayout.setAlignment(Qt.AlignRight)
            localWidget.setLayout(localLayout)

            '''Local Left Widget'''
            localLeftWidget = QWidget()
            localLeftLayout = QFormLayout()
            localLeftLayout.setAlignment(Qt.AlignRight)
            localLeftWidget.setLayout(localLeftLayout)
            localLayout.addWidget(localLeftWidget)

            ''' add image itself'''
            label = QLabel()
            pixmap = QPixmap(fullFilePath)
            pixmapResize = pixmap.scaled(325, 323)
            label.setPixmap(pixmapResize)
            localLayout.addWidget(label)

            mainWidget.scrollLayout.addWidget(localWidget)
