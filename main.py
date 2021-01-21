import sys
from UploadTool import UploadTool
from PyQt5.QtWidgets import QApplication, QWidget, QStatusBar
from presentation import generateSplitter, \
    generateLeftTopFrame, \
    generateLeftBottomFrame, \
    generateRightFrame

class PyCommonist(QWidget):

    def __init__(self):
        super(PyCommonist, self).__init__()
        self._currentUpload = []
        self.initUI()
        self.threads = []
        self.workers = []


    def initUI(self):

        self.currentDirectoryPath = ''

        generateSplitter(self)
        generateLeftTopFrame(self)
        generateLeftBottomFrame(self)

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
            generateRightFrame(self, self.currentDirectoryPath)

            self.update()

        except:
            print("Something bad happened inside onSelectFolder function")

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
        tool = UploadTool()
        ret = tool.uploadImages(self)

    '''
        cleanThreads
    '''
    def cleanThreads(self):
        print("Clean threads")
        for thread in self.threads:
            print("Thread deletion")
            thread.wait()
            thread.quit()
        self.threads.clear()
        self.workers.clear()


def main():
    app = QApplication(sys.argv)
    ex = PyCommonist()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()