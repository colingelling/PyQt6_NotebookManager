"""

    Created by Colin Gelling on 27/09/2024 (CEST)
    Using Pycharm Professional

"""
import json
import os

from PyQt6 import uic, QtWidgets, QtGui
from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QFontDatabase, QCursor, QAction
from PyQt6.QtWidgets import QApplication, QTreeWidgetItem, QTreeWidget, QMenu


class DataModel:
    # Declaration of path values for storing application output
    source = os.path.dirname(os.path.realpath(__file__))
    json_file = f"{source}/notebook_information.json"

    def __init__(self):
        super().__init__()
        self._write_file_template()

    def _write_file_template(self):
        # Declare an empty dictionary containing preset keys representing lists
        preset = {"Notebooks": {}}

        if not os.path.exists(DataModel.json_file):
            # Save the updated JSON data
            self._dump(preset)

    @staticmethod
    def load_data():
        with open(DataModel.json_file, 'r') as file:
            return json.load(file)

    def update_data(self, old_data, new_data):
        # Extract old values
        old_note_value = old_data.get('note_name')
        old_notebook_value = old_data.get('notebook')
        old_text_value = old_data.get('note_text')

        # Extract new values
        new_note_value = new_data.get('note_name')
        new_notebook_value = new_data.get('notebook')
        new_text_value = new_data.get('note_text')

        # Load existing JSON data
        json_data = self.load_data()

        # Update or move the note to a new notebook if necessary
        target_notebook = new_notebook_value if old_notebook_value != new_notebook_value else old_notebook_value
        json_data['Notebooks'].setdefault(target_notebook, {})[new_note_value] = {
            "note_text": new_text_value
        }

        # Remove the old note if the notebook or note name has changed
        if old_notebook_value != new_notebook_value or old_note_value != new_note_value:
            del json_data['Notebooks'][old_notebook_value][old_note_value]

        # Save the updated JSON data
        self._dump(json_data)

    @staticmethod
    def _dump(data):
        with open(DataModel.json_file, 'w') as file:
            return json.dump(data, file, indent=4)


class Events(QObject):
    signal = pyqtSignal()

    def __init__(self, widget, item_data):
        super(Events, self).__init__()
        self.tree_widget = widget
        self.data = item_data

        self.tree_event_data = None

        print("Widget: ", widget,  "item_data: ", item_data)

    def _item_filter(self, item):
        parent_item = item.parent()

        if parent_item:
            self.tree_event_data = {
                'parent_notebook': parent_item.text(0),
                'child_note': item.text(0)
            }
            print(self.tree_event_data)

        else:
            self.tree_event_data = {
                'notebook': item.text(0),
            }
            print(self.tree_event_data)

    def mousePressEvent(self, event):
        item = self.tree_widget.itemAt(event.pos())
        print("item ", item)
        self._item_filter(item)

        if item:
            self.actions(event, item)

        # Return to normal behavior
        QTreeWidget.mousePressEvent(self.tree_widget, event)

    def getFilteredChildNoteData(self):
        if 'child_note' in self.tree_event_data:
            return self.tree_event_data
        else:
            return None

    def actions(self, event, item):
        if event.button() == Qt.MouseButton.RightButton:
            context_menu = QMenu()

            delete_action = QAction("Delete")
            edit_action = QAction("Edit")

            style = (""
                     "QMenu {background: #e5e5e5; color: #333; border-radius: 6px; padding: 4px 3px 6px 2px;}"
                     "QMenu::item:selected {background: #fff;}"
                     "")

            context_menu.setStyleSheet(style)
            context_menu.setCursor(Qt.CursorShape.PointingHandCursor)

            # open contextmenu
            context_menu.addAction(delete_action)
            context_menu.addAction(edit_action)

            context_menu.exec(event.globalPosition().toPoint())


class MainWindow(QtWidgets.QMainWindow, DataModel):
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

        self.setFixedSize(534, 834)

        ui.notebookManagerTitleLabel.setText("Management of my notebooks")
        ui.notebookManagerTitleLabel.adjustSize()

        tree_widget = ui.QtreeWidget

        # QTreeWidget customisation
        tree_widget.setHeaderHidden(True)

        # Dictionary to map QTreeWidgetItem as data
        item_data_map = {}

        def initialize_items():
            # Readability reference declaration
            data_elements = DataModel.load_data()

            # Iterate through the data and assign elements to QTreeWidget elements
            for notebook_name in data_elements["Notebooks"]:
                notebook_item = QTreeWidgetItem([notebook_name])
                tree_widget.addTopLevelItem(notebook_item)

                item_data_map[id(notebook_item)] = notebook_name

                for note_element in data_elements["Notebooks"][notebook_name]:
                    note_item = QTreeWidgetItem([note_element])
                    notebook_item.addChild(note_item)

                    item_data_map[id(note_item)] = note_element

        # Execute functionality
        initialize_items()

        def refresh_tree_widget():
            tree_widget.clear()  # Remove all items from the widget
            initialize_items()  # Rebuild the widget items

        # One time model declaration, need the same signals for passing through functions
        events_model = Events(tree_widget, item_data_map)

        # Set a connection from the view passed signal and connect it with functionality in order to rebuild QTreeWidget items
        events_model.signal.connect(refresh_tree_widget)

        # Enable mouse tracking and override method for right-clicking support
        tree_widget.setMouseTracking(True)
        tree_widget.mousePressEvent = events_model.mousePressEvent

        def check_state(model, item_data):
            print("test")

        tree_widget.clicked.connect(
            lambda: check_state(events_model, events_model.getFilteredChildNoteData())
            if events_model.getFilteredChildNoteData() else None
        )

        button_text = "Save"
        ui.notebookActionButton.setText(button_text)
        ui.noteActionButton.setText(button_text)



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()

