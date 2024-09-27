"""

    Created by Colin Gelling on 27/09/2024 (CEST)
    Using Pycharm Professional

"""

from PyQt6 import uic
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QApplication, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        qt_creator_file = "src/ui/Overview.ui"
        uic.loadUi(qt_creator_file, self)

        self.setWindowTitle("Overview")

        stylesheet_file_path = "src/css/overview.css"
        with open(stylesheet_file_path, "r") as file:
            stylesheet = file.read()
            self.setStyleSheet(stylesheet)

        font_file = "src/fonts/FontAwesome6-Free-Regular-400.otf"
        QFontDatabase.addApplicationFont(font_file)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()

