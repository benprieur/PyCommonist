import sys
from PyQt5.QtWidgets import QApplication
from PyCommonist import PyCommonist
from PyQt5.QtGui import QIcon


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('PyCommonist.png'))

    ex = PyCommonist()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
