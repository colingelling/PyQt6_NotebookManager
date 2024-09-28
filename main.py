"""

    Created by Colin Gelling on 27/09/2024 (CEST)
    Using Pycharm Professional

"""

from PyQt6 import uic, QtWidgets, QtGui
from PyQt6.QtCore import QObject
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QApplication


class DataModel:
    def __init__(self):
        super().__init__()


class Events(QObject):
    def __init__(self):
        super().__init__()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # Load QtDesigner Ui file
        qt_creator_file = "src/ui/Overview.ui"
        self.ui = uic.loadUi(qt_creator_file, self)

        # Set window position
        frame_geometry = self.frameGeometry()
        screen = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
        frame_geometry.moveCenter(screen)
        self.move(frame_geometry.topLeft())

        # Set window title
        self.setWindowTitle("Overview")

        # Load Ui stylesheet
        stylesheet_file_path = "src/css/overview.css"
        with open(stylesheet_file_path, "r") as file:
            stylesheet = file.read()
            self.setStyleSheet(stylesheet)

        # Load FontAwesome font icons
        font_file = "src/fonts/FontAwesome6-Free-Regular-400.otf"
        QFontDatabase.addApplicationFont(font_file)

        self.content()

    def content(self):
        ui = self.ui

        # Set size properties for the window
        ui.setFixedSize(773, 434)

        ui.notebookManagerTitleLabel.setText("My notebooks")
        ui.notebookManagerTitleLabel.adjustSize()

        ui.contentHeaderWidgetLabel.setText("Welcome")
        ui.contentHeaderWidgetLabel.adjustSize()

class Dialogs(QtWidgets.QDialog):
    def __init__(self):
        super(Dialogs, self).__init__()

    def create_notebook(self):
        pass

    def create_note(self):
        pass

    def read_note(self):
        pass

    def update_notebook(self):
        pass

    def update_note(self):
        pass

    def delete_notebook(self):
        pass

    def delete_note(self):
        pass


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()

