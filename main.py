"""

    Created by Colin Gelling on 27/09/2024 (CEST)
    Using Pycharm Professional

"""

import json
import os
from signal import signal

from PyQt6 import uic, QtWidgets, QtGui
from PyQt6.QtCore import QObject, Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFontDatabase, QCursor, QAction
from PyQt6.QtWidgets import QApplication, QTreeWidgetItem, QTreeWidget, QMenu


class DataModel:
    # Declaration of path values for storing application output
    source = os.path.dirname(os.path.realpath(__file__))
    json_file = f"{source}/notebook_information.json"

    def __init__(self):
        super().__init__()
        self._write_file_template()

    @staticmethod
    def prepare_context_data(item):
        parent_item = item.parent()

        if parent_item: return {'parent_notebook': parent_item.text(0), 'child_note': item.text(0)}
        else: return {'notebook': item.text(0)}

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

    @staticmethod
    def create_notebook(notebook_name):
        json_data = DataModel.load_data()
        json_data["Notebooks"][notebook_name] = {}

        # Save the updated JSON data
        DataModel._dump(json_data)

    def update_notebook(self, data):
        not_changed_item = data.get('not_changed_notebook')
        probably_changed_item = data.get('probably_changed_notebook')

        if not_changed_item != probably_changed_item:

            json_data = self.load_data()  # Load existing JSON data
            json_data['Notebooks'][probably_changed_item] = json_data['Notebooks'].pop(not_changed_item)  # Replace

            # Save the updated JSON data
            self._dump(json_data)

        else:
            # TODO: Return signal, referring to QmessageBox()
            pass

    def update_note(self, old_data, new_data):
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
    notebook_edit_signal = pyqtSignal(dict, str)
    data_signal = pyqtSignal()

    notebook_form_state = None
    note_form_state = None

class Widgets:
    tree_widget = None

    def __init__(self, events_model):
        super(Widgets, self).__init__()
        self.events_model = events_model
        self.item_data_map = {}

    def setup_tree_widget(self, widget):

        Widgets.tree_widget = widget  # Assign as class property
        widget.setHeaderHidden(True)  # QTreeWidget customisation; hiding headers

        self.add_tree_items(widget)  # Execute functionality for adding both notebooks and notes

        # Extending to context menu display
        widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        widget.customContextMenuRequested.connect(self.context_menu)

    def add_tree_items(self, widget):
        # Readability reference declaration
        data_elements = DataModel.load_data()

        # Iterate through the data and assign elements to QTreeWidget elements
        for notebook_name in data_elements["Notebooks"]:
            notebook_item = QTreeWidgetItem([notebook_name])
            widget.addTopLevelItem(notebook_item)

            # Storing object data in order to keep the positions for comparable situations later
            self.item_data_map[id(notebook_item)] = notebook_name

            for note_element in data_elements["Notebooks"][notebook_name]:
                note_item = QTreeWidgetItem([note_element])
                notebook_item.addChild(note_item)

                self.item_data_map[id(note_item)] = note_element

    def refresh_tree_widget(self, widget):
        widget.clear()  # Remove all items from the widget
        self.add_tree_items(widget)  # Rebuild widget items

    def context_menu(self, position):
        # Receive the item's clicked position
        selected_item = Widgets.tree_widget.itemAt(position)

        if selected_item:
            menu = QMenu()  # Create context menu instance

            edit_action_text = "Edit"
            delete_action_text = "Delete"

            # Adding options
            edit_action = menu.addAction(edit_action_text)
            delete_action = menu.addAction(delete_action_text)

            # Connecting the options to functions
            edit_action.triggered.connect(lambda: self.activate_trigger(selected_item, edit_action_text))
            delete_action.triggered.connect(lambda: self.activate_trigger(selected_item, delete_action_text))

            # Display the context menu at the mouse position and get the selected action
            menu.exec(Widgets.tree_widget.viewport().mapToGlobal(position))

    def activate_trigger(self, item, action):
        item_data = DataModel.prepare_context_data(item)

        # emit signal that the item has been clicked
        item_text = item.text(0)
        item_data["pressed_item"] = item_text
        self.events_model.notebook_edit_signal.emit(item_data, action)


class MainWindow(QtWidgets.QMainWindow):
    context_menu_func = None

    def __init__(self):
        super(MainWindow, self).__init__()

        # One time model declaration, need the same signals for passing through functions
        self.data_model = DataModel()
        self.events_model = Events()
        self.widgets_model = Widgets(self.events_model)

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

        # Widget assignment
        parent_tree_widget = ui.QtreeWidget

        # TreeWidget setup
        self.widgets_model.setup_tree_widget(parent_tree_widget)

        # Set a connection from the view passed signal and connect it with functionality in order to rebuild QTreeWidget items
        self.events_model.data_signal.connect(lambda: self.widgets_model.refresh_tree_widget(parent_tree_widget))

        ui.notebookActionLabel.setText("The name of your notebook")
        ui.noteActionLabel.setText("The name of your note")
        ui.noteActionSelectorLabel.setText("Parent notebook for this note")
        ui.noteActionDescriptionLabel.setText("Note text")

        notebook_save_button = ui.notebookActionButton
        note_save_button =  ui.noteActionButton

        save_button_text = "Save"
        notebook_save_button.setText(save_button_text)
        note_save_button.setText(save_button_text)

        notebook_save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        note_save_button.setCursor(Qt.CursorShape.PointingHandCursor)

        # Set default state at the beginning
        if not self.events_model.notebook_form_state:
            self.events_model.notebook_form_state = "notebook creation mode"  # Set (default) mode for the first time

        notebook_data = {}

        def handle_signal(data, action):
            self.events_model.notebook_form_state = "notebook editing mode"  # Change mode

            notebook_name = data.get('pressed_item')  # Assign value
            ui.notebookAction_lineEdit.setText(notebook_name)  # Set input field text
            notebook_data['not_changed_notebook'] = notebook_name  # Add notebook_name to notebook_data for remembering

        self.events_model.notebook_edit_signal.connect(handle_signal)

        def state_verification(state):
            input_field = ui.notebookAction_lineEdit
            input_text = input_field.text()  # Assign value on time of button click

            if not input_text:
                # TODO: rEtUrN qMeSsAgEbOx
                pass

            if "notebook creation mode" in state:
                self.data_model.create_notebook(input_text)  # Handle request to JSON file
            elif "notebook editing mode" in state:
                notebook_data['probably_changed_notebook'] = input_text  # Add the probably changed information from the field
                self.data_model.update_notebook(notebook_data)  # Handle request to JSON file

            input_field.clear()
            self.events_model.data_signal.emit()  # Emit signal to update TreeWidget
            self.events_model.notebook_form_state = "notebook creation mode"  # Go back to default

        ui.notebookActionButton.clicked.connect(lambda: state_verification(self.events_model.notebook_form_state))


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()

