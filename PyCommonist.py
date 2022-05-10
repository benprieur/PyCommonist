import traceback
from UploadTool import UploadTool
import os
from os.path import isfile, join
import re

from completer import SearchBox
import exifread
from gps_location import get_exif_location
from ImageUpload import ImageUpload
from config import LeftFrameConfig, RightFrameConfig
from EXIFImage import EXIFImage

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
    QTreeView, \
    QScrollArea, \
    QWidget, \
    QCheckBox, \
    QPushButton, \
    QMenu, \
    QMessageBox


from constants import VERTICAL_TOP_SIZE, \
    VERTICAL_BOTTOM_SIZE, \
    HORIZONTAL_LEFT_SIZE, \
    HORIZONTAL_RIGHT_SIZE, \
    WIDTH_WIDGET, \
    WIDTH_WIDGET_RIGHT, \
    IMAGE_DIMENSION, \
    STYLE_IMPORT_BUTTON, \
    STYLE_IMPORT_STATUS, \
    STYLE_STATUSBAR, \
    IMPORT_BUTTON_NO_IMAGE, \
    IMPORT_BUTTON_N_IMAGES


class PyCommonist(QWidget):

    tool = None

    def __init__(self):
        super(PyCommonist, self).__init__()
        self.initUI()
        self.threads = []
        self.workers = []

        # copied image information
        self.copiedName = ''
        self.copiedDescription = ''
        self.copiedCategories = ''

        # upload status
        self.initUpload(0)


    def initUI(self):

        self.currentDirectoryPath = ''
        self.imageSortOrder = RightFrameConfig.default_image_sort

        self.generateSplitter()
        self.generateLeftTopFrame()
        self.generateLeftBottomFrame()

        self.showMaximized()
        self.setWindowTitle('PyCommonist - Wikimedia Commons')

        self.show()

    def onSelectFolder(self, selected):

        try:
            currentIndex = selected.indexes()[0]
            self.currentDirectoryPath = self.modelTree.filePath(currentIndex)
            print(self.currentDirectoryPath)

        except:
            print("Something bad happened inside onSelectFolder function")
            traceback.print_exc()

        self.loadMediaFromCurrentFolder()


    def loadMediaFromCurrentFolder(self):

        try:
            self.clearStatus()
            self.exifImageCollection = []

            list_dir = os.listdir(self.currentDirectoryPath)
            files = [f for f in sorted(list_dir) if isfile(join(self.currentDirectoryPath, f))]
            for file in files:
                fullFilePath = os.path.join(self.currentDirectoryPath, file)
                if fullFilePath.upper().endswith(".JPEG") or \
                   fullFilePath.upper().endswith(".JPG") or \
                   fullFilePath.upper().endswith(".SVG") or \
                   fullFilePath.upper().endswith(".PNG"):

                    currentExifImage = EXIFImage()
                    currentExifImage.fullFilePath = fullFilePath
                    currentExifImage.filename = file
                    tags = None

                    try:
                        """ EXIF """
                        f_exif = open(fullFilePath, 'rb')
                        tags = exifread.process_file(f_exif)
                        #print(tags)
                    except:
                        print("A problem with EXIF data reading")

                    """ Location"""
                    # 'GPS GPSLatitude', 'GPS GPSLongitude'] # [45, 49, 339/25] [4, 55, 716/25]
                    # 'GPS GPSImgDirection' 'GPS GPSLatitudeRef'
                    lat = ''
                    long = ''
                    heading = ''
                    try:
                        currentExifImage.lat, currentExifImage.long, currentExifImage.heading = get_exif_location(tags)
                    except:
                        print("A problem with EXIF data reading")

                    dt = None
                    try:
                        """ Date Time """
                        dt = tags['EXIF DateTimeOriginal'] # 2021:01:13 14:48:44
                    except:
                        print("A problem with EXIF data reading")

                    print (dt)
                    dt = str(dt)
                    indexSpace = dt.find(" ")
                    currentExifImage.date = dt[0:indexSpace].replace(":", "-")
                    currentExifImage.time = dt[indexSpace+1:]

                    self.exifImageCollection.append(currentExifImage)
                    print(currentExifImage)

            self.generateRightFrame()

        except:
            print("Something bad happened inside loadMediaFromCurrentFolder function")
            traceback.print_exc()


    def btnToggleImageSortOrder(self):

        if hasattr(self, '_currentUpload') is False:
            return

        if len(self._currentUpload) > 0:

            if self.imageSortOrder == "file_name":
                self.imageSortOrder = "exif_date"
            else:
                self.imageSortOrder = "file_name"

            self.generateRightFrame()


    def btnSelectNoImage(self):

        if hasattr(self, '_currentUpload') is False:
            return

        if len(self._currentUpload) > 0:

            for element in self._currentUpload:
                element.cbImport.setCheckState(False)


    def btnSelectAllImages(self):

        if hasattr(self, '_currentUpload') is False:
            return

        if len(self._currentUpload) > 0:

            for element in self._currentUpload:
                element.cbImport.setCheckState(True)


    def onToggleImport(self):

        # count selected imports
        selectedImports = 0
        for element in self._currentUpload:
            if element.cbImport.isChecked():
                selectedImports = selectedImports + 1;

        # update selected import counter
        if selectedImports == 0:
            self.btnImport.setText(IMPORT_BUTTON_NO_IMAGE)
        else:
            self.btnImport.setText(IMPORT_BUTTON_N_IMAGES.format(selectedImports))



    def onClickImport(self):

        if hasattr(self, '_currentUpload') is False:
            return

        if len(self._currentUpload) == 0:
            return

        # verify all fields are set
        emptyDescriptions = 0
        emptyCategories = 0
        for element in self._currentUpload:

            if not element.cbImport.isChecked():
                continue;

            # test descriptions (main and element's)
            desc = self.lineEditDescription.toPlainText() + element.lineEditDescription.toPlainText()
            if not (desc and desc.strip()):
                emptyDescriptions = emptyDescriptions + 1

            # test categories (main and element's)
            categs = self.lineEditCategories.text() + element.lineEditCategories.text()
            if not (categs and categs.strip()):
                emptyCategories = emptyCategories + 1

        if emptyDescriptions > 0:
            confirmation = QMessageBox.question(self, 'Incomplete Descriptions', 'There are %s image(s) without description, continue upload?' % emptyDescriptions, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirmation == QMessageBox.No:
                return

        if emptyCategories > 0:
            confirmation = QMessageBox.question(self, 'Incomplete Categories', 'There are %s image(s) without category, continue upload?' % emptyCategories, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirmation == QMessageBox.No:
                return

        if (self.tool == None):
            self.tool = UploadTool()
        ret = self.tool.uploadImages(self)


    def cleanThreads(self):
        try:
            print("Clean threads properly")

            for thread in self.threads:
                print("Current thread proper deletion")
                thread.quit()
                thread.wait()

        except:
            print("A problem with cleanThreads")

    def generateSplitter(self):

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()

        self.leftTopFrame = QFrame()
        self.leftTopFrame.setFrameShape(QFrame.StyledPanel)

        self.rightWidget = QWidget()
        self.rightWidget.resize(300, 300)
        self.layoutRight = QVBoxLayout()
        self.rightWidget.setLayout(self.layoutRight)

        self.generateRightFrameButtons()

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

        self.splitterCentral = QSplitter(Qt.Horizontal)
        self.splitterCentral.addWidget(self.splitterLeft)
        self.splitterCentral.addWidget(self.rightWidget)
        self.splitterCentral.setSizes([HORIZONTAL_LEFT_SIZE,HORIZONTAL_RIGHT_SIZE])
        hbox.addWidget(self.splitterCentral)

        vbox.addLayout(hbox)

        self.statusBar = QLabel()
        self.statusBar.setStyleSheet(STYLE_STATUSBAR)
        vbox.addWidget(self.statusBar)

        self.setLayout(vbox)

    def generateLeftTopFrame(self):

        self.layoutLeftTop = QFormLayout()
        self.layoutLeftTop.setFormAlignment(Qt.AlignTop)

        self.lblUserName = QLabel("Username: ")
        self.lblUserName.setAlignment(Qt.AlignLeft)
        self.lineEditUserName = QLineEdit()
        self.lineEditUserName.setText(LeftFrameConfig.username)
        self.lineEditUserName.setFixedWidth(WIDTH_WIDGET)
        self.lineEditUserName.setAlignment(Qt.AlignLeft)
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
        self.lineEditSource.setText(LeftFrameConfig.source)
        self.lineEditSource.setAlignment(Qt.AlignLeft)
        self.layoutLeftTop.addRow(self.lblSource, self.lineEditSource)

        self.lblAuthor = QLabel("Author: ")
        self.lblAuthor.setAlignment(Qt.AlignLeft)
        self.lineEditAuthor = QLineEdit()
        self.lineEditAuthor.setFixedWidth(WIDTH_WIDGET)
        self.lineEditAuthor.setText(LeftFrameConfig.author)
        self.lineEditAuthor.setAlignment(Qt.AlignLeft)
        self.layoutLeftTop.addRow(self.lblAuthor, self.lineEditAuthor)

        self.lblCategories = QLabel("Categories: ")
        self.lblCategories.setAlignment(Qt.AlignLeft)
        self.lineEditCategories = QLineEdit()
        self.lineEditCategories.setText(LeftFrameConfig.categories)
        self.lineEditCategories.setFixedWidth(WIDTH_WIDGET)
        self.lineEditCategories.setAlignment(Qt.AlignLeft)
        self.layoutLeftTop.addRow(self.lblCategories, self.lineEditCategories)

        self.lblLicense = QLabel("License: ")
        self.lblLicense.setAlignment(Qt.AlignLeft)
        self.lineEditLicense = QLineEdit()
        self.lineEditLicense.setFixedWidth(WIDTH_WIDGET)
        self.lineEditLicense.setText(LeftFrameConfig.license)
        self.lineEditLicense.setAlignment(Qt.AlignLeft)
        self.layoutLeftTop.addRow(self.lblLicense, self.lineEditLicense)

        self.lblLanguage = QLabel("Language code: ")
        self.lblLanguage.setAlignment(Qt.AlignLeft)
        self.lineEditLanguage = QLineEdit()
        self.lineEditLanguage.setFixedWidth(WIDTH_WIDGET)
        self.lineEditLanguage.setText(LeftFrameConfig.language)
        self.lineEditLanguage.setAlignment(Qt.AlignLeft)
        self.layoutLeftTop.addRow(self.lblLanguage, self.lineEditLanguage)

        self.lblDescription = QLabel("Description: ")
        self.lblDescription.setAlignment(Qt.AlignLeft)
        self.lineEditDescription = QPlainTextEdit()
        self.lineEditDescription.setFixedWidth(WIDTH_WIDGET)
        self.layoutLeftTop.addRow(self.lblDescription, self.lineEditDescription)

        separationLeftTopFrame = QLabel()
        self.layoutLeftTop.addWidget(separationLeftTopFrame)

        importWidget = QWidget()
        importLayout = QHBoxLayout()
        importWidget.setLayout(importLayout)

        self.btnImport = QPushButton(IMPORT_BUTTON_NO_IMAGE)

        self.btnImport.clicked.connect(self.onClickImport)

        importLayout.addWidget(self.btnImport)
        self.layoutLeftTop.addWidget(importWidget)
        importWidget.setStyleSheet("border:1px solid #808080;");

        self.btnImport.setStyleSheet(STYLE_IMPORT_BUTTON)

        """ Layout Association of the Left Top Frame"""
        self.leftTopFrame.setLayout(self.layoutLeftTop)

    def generateLeftBottomFrame(self):

        self.layoutLeftBottom = QVBoxLayout()

        self.modelTree = QFileSystemModel()
        self.modelTree.setRootPath(QDir.currentPath())
        self.modelTree.setFilter(QDir.Dirs) # Only directories

        self.treeLeftBottom = QTreeView()
        self.treeLeftBottom.setModel(self.modelTree)
        self.treeLeftBottom.setAnimated(False)
        self.treeLeftBottom.setIndentation(10)
        self.treeLeftBottom.setColumnWidth(0, 300)
        self.treeLeftBottom.expandAll()
        self.treeLeftBottom.selectionModel().selectionChanged.connect(self.onSelectFolder)
        self.layoutLeftBottom.addWidget(self.treeLeftBottom)
        self.leftBottonFrame.setLayout(self.layoutLeftBottom)


    def generateRightFrameButtons(self):

        importCommandWidget = QWidget()
        importCommandLayout = QHBoxLayout()
        importCommandWidget.setLayout(importCommandLayout)

        self.btnToggleImageSort = QPushButton("Images sorted by name")
        self.btnToggleImageSort.clicked.connect(self.btnToggleImageSortOrder)

        self.btnImportCheckNone = QPushButton("Check None")
        self.btnImportCheckNone.clicked.connect(self.btnSelectNoImage)

        self.btnImportCheckAll = QPushButton("Check All")
        self.btnImportCheckAll.clicked.connect(self.btnSelectAllImages)

        self.btnReloadFolder = QPushButton("Reload Folder")
        self.btnReloadFolder.clicked.connect(self.loadMediaFromCurrentFolder)

        importCommandLayout.addWidget(self.btnToggleImageSort)
        importCommandLayout.addWidget(self.btnImportCheckNone)
        importCommandLayout.addWidget(self.btnImportCheckAll)
        importCommandLayout.addWidget(self.btnReloadFolder)

        self.layoutRight.addWidget(importCommandWidget)


    def generateRightFrame(self):

        self._currentUpload = []

        layout = self.scrollLayout
        print(layout)
        print(layout.count())

        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if self.imageSortOrder == "exif_date":
            self.exifImageCollection.sort(key=lambda image: image.date + ' ' + image.time)
            self.btnToggleImageSort.setText("Images sorted by date")
        else:
            self.exifImageCollection.sort(key=lambda image: image.filename)
            self.btnToggleImageSort.setText("Images sorted by name")

        for currentExifImage in self.exifImageCollection:

            localWidget = ImageUpload()
            localLayout = QHBoxLayout()
            localLayout.setAlignment(Qt.AlignRight)
            localWidget.setLayout(localLayout)
            self.scrollLayout.addWidget(localWidget)
            self._currentUpload.append(localWidget)

            localLeftWidget = QWidget()
            localLeftLayout = QFormLayout()
            localLeftLayout.setAlignment(Qt.AlignRight)
            localLeftWidget.setLayout(localLeftLayout)
            localLayout.addWidget(localLeftWidget)

            cbImport = QCheckBox("Import")
            cbImport.toggled.connect(self.onToggleImport)

            lblUploadResult = QLabel()
            lblUploadResult.setStyleSheet(STYLE_IMPORT_STATUS)
            btnCopyPaste = QPushButton("Copy/Paste")
            resultLabelAndButtonsLayout = QHBoxLayout()
            resultLabelAndButtonsLayout.addWidget(lblUploadResult, 3)
            resultLabelAndButtonsLayout.addWidget(btnCopyPaste, 1)
            # create menu here, connect actions after widget creations
            copyPasteMenu = QMenu()
            copyAction = copyPasteMenu.addAction("Copy")
            pasteAction = copyPasteMenu.addAction("Paste name, description and categories")
            pasteWithNumberingAction = copyPasteMenu.addAction("Paste name with numbering, description and categories")
            btnCopyPaste.setMenu(copyPasteMenu)

            localLeftLayout.addRow(cbImport, resultLabelAndButtonsLayout)
            localWidget.cbImport = cbImport
            localWidget.lblUploadResult = lblUploadResult
            localWidget.btnCopyPaste = btnCopyPaste

            lblFileName = QLabel("Name: ")
            lblFileName.setAlignment(Qt.AlignLeft)
            lineEditFileName = QLineEdit()
            lineEditFileName.setFixedWidth(WIDTH_WIDGET_RIGHT)
            lineEditFileName.setText(currentExifImage.filename)
            lineEditFileName.setAlignment(Qt.AlignLeft)

            lineEditFileName.textChanged.connect(lambda state, w=cbImport: w.setChecked(True))

            localLeftLayout.addRow(lblFileName, lineEditFileName)
            localWidget.lineEditFileName = lineEditFileName

            lblRealFileName = QLineEdit()
            lblRealFileName.setText(currentExifImage.filename)
            localWidget.lblRealFileName = lblRealFileName
            localWidget.lblRealFileName.isVisible = False

            lblDescription = QLabel("Description: ")
            lblDescription.setAlignment(Qt.AlignLeft)
            lineEditDescription = QPlainTextEdit()
            lineEditDescription.setFixedWidth(WIDTH_WIDGET_RIGHT)
            localLeftLayout.addRow(lblDescription, lineEditDescription)
            localWidget.lineEditDescription = lineEditDescription

            lblCategories = QLabel("Categories: ")
            searchBoxCategory = SearchBox()
            localLeftLayout.addRow(lblCategories, searchBoxCategory)
            localWidget.searchBoxCategory = searchBoxCategory

            lineEditCategories = QLineEdit()
            lineEditCategories.setFixedWidth(WIDTH_WIDGET_RIGHT)
            localLeftLayout.addRow(QLabel(""), lineEditCategories)
            localWidget.lineEditCategories = lineEditCategories

            localWidget.searchBoxCategory.returnPressed.connect(localWidget.onPressed)

            lblLocation = QLabel("Location: ")
            lblLocation.setAlignment(Qt.AlignLeft)
            lineEditLocation = QLineEdit()
            lineEditLocation.setFixedWidth(WIDTH_WIDGET_RIGHT)
            if currentExifImage.lat == None or currentExifImage.long == None:
                lineEditLocation.setText('')
            else:
                lineEditLocation.setText(str(currentExifImage.lat) + '|' + str(currentExifImage.long) + "|heading:" + str(currentExifImage.heading))
            lineEditLocation.setAlignment(Qt.AlignLeft)
            localLeftLayout.addRow(lblLocation, lineEditLocation)
            localWidget.lineEditLocation = lineEditLocation

            lblDateTime = QLabel("Date Time: ")
            lblDateTime.setAlignment(Qt.AlignLeft)
            lineEditDateTime = QLineEdit()
            lineEditDateTime.setFixedWidth(WIDTH_WIDGET_RIGHT)
            lineEditDateTime.setText(currentExifImage.date + ' ' + currentExifImage.time)
            lineEditDateTime.setAlignment(Qt.AlignLeft)
            localLeftLayout.addRow(lblDateTime, lineEditDateTime)
            localWidget.lineEditDateTime = lineEditDateTime

            copyAction.triggered.connect(lambda state, w=localWidget: self.copyImageInfo(w))
            pasteAction.triggered.connect(lambda state, w=localWidget: self.pasteImageInfo(w, False))
            pasteWithNumberingAction.triggered.connect(lambda state, w=localWidget: self.pasteImageInfo(w, True))

            label = QLabel()
            pixmap = QPixmap(currentExifImage.fullFilePath)
            pixmapResize = pixmap.scaledToWidth(IMAGE_DIMENSION, Qt.FastTransformation)
            label.setPixmap(pixmapResize)
            localLayout.addWidget(label)
            localWidget.fullFilePath = currentExifImage.fullFilePath

            self.update()


    def copyImageInfo(self, imageWidget):
        # copy image information
        self.copiedName = imageWidget.lineEditFileName.text()
        self.copiedDescription = imageWidget.lineEditDescription.toPlainText()
        self.copiedCategories = imageWidget.lineEditCategories.text()

    def pasteImageInfo(self, imageWidget, increaseNumber):
        # paste image information
        name = self.copiedName
        if increaseNumber:
            # increment last number found in name
            numberList = re.findall(r'\d+', name)
            if len(numberList) > 0:
                val = numberList[-1]
                nextVal = str(int(val) + 1)
                # pad with 0s if needed
                if len(nextVal) < len(val):
                    nextVal = nextVal.zfill(len(val))
                # replace last number in the string with increased number
                removeLastNumber = name.rsplit(val, 1)
                name = nextVal.join(removeLastNumber)
                # save name with new number
                self.copiedName = name

        imageWidget.lineEditFileName.setText(name)
        imageWidget.lineEditDescription.setPlainText(self.copiedDescription)
        imageWidget.lineEditCategories.setText(self.copiedCategories)


    def clearStatus(self):
        self.statusBar.setText("")

    def setStatus(self, message):
        self.statusBar.setText(message)


    def initUpload(self, imageCount):
        self.numberOfImagesChecked = imageCount
        self.uploadSuccesses = 0
        self.uploadFailures = 0
        self.uploadStatusDots = 0

    def updateUploadingStatus(self):
        total = self.uploadSuccesses + self.uploadFailures
        if total >= self.numberOfImagesChecked:
            return False

        self.uploadStatusDots = self.uploadStatusDots + 1
        if self.uploadStatusDots > 10:
            self.uploadStatusDots = 0

        message = "{}/{} ".format(total, self.numberOfImagesChecked)
        message = message + "." * self.uploadStatusDots
        self.setStatus(message)

        return True

    def setUploadStatus(self, success):
        if success:
            self.uploadSuccesses = self.uploadSuccesses + 1
        else:
            self.uploadFailures = self.uploadFailures + 1

        message = ""
        successes = self.uploadSuccesses
        failures = self.uploadFailures
        total = self.numberOfImagesChecked

        if successes > 0:
            message = message + " {}/{} image(s) successfully uploaded".format(successes, total)
        if failures > 0:
            if successes > 0:
                message = message + "; "
            message = message + "{} upload(s) failed!".format(failures)

        self.setStatus(message)

