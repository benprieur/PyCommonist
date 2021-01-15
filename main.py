import sys
from PyQt5.QtWidgets import QApplication, QWidget
from presentation import generateSplitter, \
    generateLeftTopFrame, \
    generateLeftBottomFrame, \
    generateRightFrame

class PyCommonist(QWidget):

    def __init__(self):
        super(PyCommonist, self).__init__()
        self.initUI()

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
        currentIndex = selected.indexes()[0]
        #print(currentIndex)
        #print(currentIndex.row())
        currentDirectoryPath = self.modelTree.filePath(currentIndex)
        print(currentDirectoryPath)

        if self.currentDirectoryPath != currentDirectoryPath:
            self.currentDirectoryPath = currentDirectoryPath
            generateRightFrame(self, self.currentDirectoryPath)

        self.update()

def main():
    app = QApplication(sys.argv)
    ex = PyCommonist()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()