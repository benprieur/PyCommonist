import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyCommonist import PyCommonist


def main():
    """ main """
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('img/Logo PyCommonist.svg'))
    instance = PyCommonist()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
