import os,sip
from PyQt5.QtCore import Qt
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
    QTreeView
from constants import VERTICAL_TOP_SIZE, \
    VERTICAL_BOTTOM_SIZE, \
    HORIZONTAL_LEFT_SIZE, \
    HORIZONTAL_RIGHT_SIZE


'''
    generateSplitter
'''
def generateSplitter(widget):

    widget.hbox = QHBoxLayout()

    widget.leftTopFrame = QFrame()
    widget.leftTopFrame.setFrameShape(QFrame.StyledPanel)
    widget.rightFrame = QFrame()
    widget.rightFrame.setFrameShape(QFrame.StyledPanel)

    widget.splitterLeft = QSplitter(Qt.Vertical)
    widget.leftBottonFrame = QFrame()
    widget.leftBottonFrame.setFrameShape(QFrame.StyledPanel)

    widget.splitterLeft.addWidget(widget.leftTopFrame)
    widget.splitterLeft.addWidget(widget.leftBottonFrame)
    widget.splitterLeft.setSizes([VERTICAL_TOP_SIZE,VERTICAL_BOTTOM_SIZE])

    widget.splitterCentral = QSplitter(Qt.Horizontal)
    widget.splitterCentral.addWidget(widget.splitterLeft)
    widget.splitterCentral.addWidget(widget.rightFrame)
    widget.splitterCentral.setSizes([HORIZONTAL_LEFT_SIZE,HORIZONTAL_RIGHT_SIZE])

    widget.hbox.addWidget(widget.splitterCentral)

    widget.setLayout(widget.hbox)


'''
    generateLeftTopFrame
'''
def generateLeftTopFrame(widget):

    widget.layoutLeftTop = QFormLayout()
    widget.layoutLeftTop.setFormAlignment(Qt.AlignTop)

    widget.lblUserName = QLabel("Username: ")
    widget.lblUserName.setAlignment(Qt.AlignLeft)
    widget.lineEditUserName = QLineEdit()
    widget.lineEditUserName.setFixedWidth(200)
    widget.lineEditUserName.setAlignment(Qt.AlignLeft)
    widget.lineEditUserName.setText("Benoît Prieur")
    widget.layoutLeftTop.addRow(widget.lblUserName, widget.lineEditUserName)

    widget.lblPassword = QLabel("Password: ")
    widget.lblPassword.setAlignment(Qt.AlignLeft)
    widget.lineEditPassword = QLineEdit()
    widget.lineEditPassword.setFixedWidth(200)
    widget.lineEditPassword.setAlignment(Qt.AlignLeft)
    widget.lineEditPassword.setEchoMode(QLineEdit.Password)
    widget.layoutLeftTop.addRow(widget.lblPassword, widget.lineEditPassword)

    widget.lblWiki = QLabel("Wiki: ")
    widget.lblWiki.setAlignment(Qt.AlignLeft)
    widget.lineEditWiki = QLabel() #QLineEdit()
    widget.lineEditWiki.setFixedWidth(200)
    widget.lineEditWiki.setText("Wikimedia Commons")
    widget.lineEditWiki.setAlignment(Qt.AlignLeft)
    widget.layoutLeftTop.addRow(widget.lblWiki, widget.lineEditWiki)

    widget.lblSource = QLabel("Source: ")
    widget.lblSource.setAlignment(Qt.AlignLeft)
    widget.lineEditSource = QLineEdit()
    widget.lineEditSource.setFixedWidth(200)
    widget.lineEditSource.setText("{{own}}")
    widget.lineEditSource.setAlignment(Qt.AlignLeft)
    widget.layoutLeftTop.addRow(widget.lblSource, widget.lineEditSource)

    widget.lblDate = QLabel("Date: ")
    widget.lblDate.setAlignment(Qt.AlignLeft)
    widget.lineEditDate = QLineEdit()
    widget.lineEditDate.setFixedWidth(200)
    widget.lineEditDate.setAlignment(Qt.AlignLeft)
    widget.layoutLeftTop.addRow(widget.lblDate, widget.lineEditDate)

    widget.lblAuthor = QLabel("Author: ")
    widget.lblAuthor.setAlignment(Qt.AlignLeft)
    widget.lineEditAuthor = QLineEdit()
    widget.lineEditAuthor.setFixedWidth(200)
    widget.lineEditAuthor.setText("{{User:Benoît Prieur/Credit}}")
    widget.lineEditAuthor.setAlignment(Qt.AlignLeft)
    widget.layoutLeftTop.addRow(widget.lblAuthor, widget.lineEditAuthor)

    widget.lblCategories = QLabel("Categories: ")
    widget.lblCategories.setAlignment(Qt.AlignLeft)
    widget.lineEditCategories = QLineEdit()
    widget.lineEditCategories.setFixedWidth(200)
    widget.lineEditCategories.setAlignment(Qt.AlignLeft)
    widget.layoutLeftTop.addRow(widget.lblCategories, widget.lineEditCategories)

    widget.lblLicense = QLabel("License: ")
    widget.lblLicense.setAlignment(Qt.AlignLeft)
    widget.lineEditLicense = QLineEdit()
    widget.lineEditLicense.setFixedWidth(200)
    widget.lineEditLicense.setText("{{self|cc-by-sa-4.0}}")
    widget.lineEditLicense.setAlignment(Qt.AlignLeft)
    widget.layoutLeftTop.addRow(widget.lblLicense, widget.lineEditLicense)

    widget.lblDescription = QLabel("Description: ")
    widget.lblDescription.setAlignment(Qt.AlignLeft)
    widget.lineEditDescription = QPlainTextEdit()
    widget.layoutLeftTop.addRow(widget.lblDescription, widget.lineEditDescription)

    widget.leftTopFrame.setLayout(widget.layoutLeftTop)


'''
    generateLeftBottomFrame
'''
def generateLeftBottomFrame(widget):

    widget.layoutLeftBottom = QVBoxLayout()

    widget.modelTree = QFileSystemModel()
    widget.modelTree.setRootPath(QDir.currentPath())
    widget.treeLeftBottom = QTreeView()
    widget.treeLeftBottom.setModel(widget.modelTree)

    widget.treeLeftBottom.setAnimated(False)
    widget.treeLeftBottom.setIndentation(20)
    widget.treeLeftBottom.selectionModel().selectionChanged.connect(widget.onSelectFolder)
    widget.layoutLeftBottom.addWidget(widget.treeLeftBottom)
    widget.leftBottonFrame.setLayout(widget.layoutLeftBottom)


'''
    generateRightFrame
'''
def generateRightFrame(widget, path):

    ''' Delete everything on right'''
    layout = widget.rightFrame.layout()
    if layout is not None:
        deleteLayout(layout)

    widget.layoutRight = QVBoxLayout()
    widget.rightFrame.setLayout(widget.layoutRight)
    layout = widget.rightFrame.layout()

    for file in os.listdir(path):
        fullFilePath = os.path.join(path, file)
        if fullFilePath.endswith(".jpg"):

            ''' add image itself'''
            label = QLabel()
            pixmap = QPixmap(fullFilePath)
            pixmapResize = pixmap.scaled(250, 250)
            label.setPixmap(pixmapResize)
            layout.addWidget(label)


'''
    deleteLayout
'''
def deleteLayout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.deleteLayout(item.layout())
        sip.delete(layout)