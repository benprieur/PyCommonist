import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyCommonist import PyCommonist

def main():
    """ main """ 
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('img/Logo PyCommonist.svg'))
    instance = PyCommonist()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
