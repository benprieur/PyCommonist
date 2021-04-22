import sys
from PyQt5.QtWidgets import QApplication
from PyCommonist import PyCommonist

def main():
    app = QApplication(sys.argv)
    ex = PyCommonist()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
