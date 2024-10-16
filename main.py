"""

    Created by Colin Gelling on 27/09/2024 (CEST)
    Using Pycharm Professional

"""

import json
import os

from PyQt6 import uic, QtWidgets, QtGui
from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QApplication, QTreeWidgetItem, QMenu


class DataModel:
    source = os.path.dirname(os.path.realpath(__file__))
    json_file = f"{source}/notebook_information.json"

    def __init__(self):
        super().__init__()
        self._write_file_template()

    @staticmethod
    def prepare_context_data(item):
        parent_item = item.parent()

        if parent_item: return {'notebook': parent_item.text(0), 'child_note': item.text(0)}
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

    def create_note(self, note_name, notebook_name, note_text):
        json_data = DataModel.load_data()
        json_data["Notebooks"][notebook_name].update({note_name: {'text': note_text}})

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
            return None  # Do nothing if nothing has been changed

    def update_note(self, form_data):
        # Assign note values from before the button click
        first_note_value = form_data['viewed_data'].get('note_name')
        first_notebook_value = form_data['viewed_data'].get('parent_notebook')
        first_text_value = form_data['viewed_data'].get('note_text')

        # Assign note values from after the button click
        second_note_value = form_data['probably_changed_data'].get('note_name')
        second_notebook_value = form_data['probably_changed_data'].get('parent_notebook')
        second_text_value = form_data['probably_changed_data'].get('note_text')

        # Load existing JSON data
        json_data = self.load_data()

        # Move or update the note to a new notebook if necessary
        target_notebook = second_notebook_value if first_notebook_value != second_notebook_value else first_notebook_value
        if target_notebook is not first_notebook_value:
            json_data['Notebooks'].setdefault(target_notebook, {})[second_note_value] = {
                "text": second_text_value
            }
        else:
            json_data['Notebooks'][first_notebook_value][second_note_value] = {  # Notebook did not change, others did
                "text": second_text_value
            }

        # Remove the old note if the notebook or note name has changed
        if first_notebook_value != second_notebook_value or first_note_value != second_note_value:
            del json_data['Notebooks'][first_notebook_value][first_note_value]

        # Save the updated JSON data
        self._dump(json_data)

    @staticmethod
    def delete_notebook(notebook):
        json_data = DataModel.load_data()
        del json_data["Notebooks"][notebook]  # Remove the entire notebook
        DataModel._dump(json_data)  # Handle changes to the JSON file

    @staticmethod
    def delete_note(notebook, note):
        json_data = DataModel.load_data()
        json_data["Notebooks"][notebook].pop(note)  # Remove the note inside the notebook
        DataModel._dump(json_data)  # Handle changes to the JSON file

    @staticmethod
    def _dump(data):
        with open(DataModel.json_file, 'w') as file:
            return json.dump(data, file, indent=4)


class Events(QObject):
    edit_signal = pyqtSignal(dict, str)
    delete_signal = pyqtSignal(dict, str)

    data_changed_signal = pyqtSignal()

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

        # Extend to context menu display
        widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        widget.customContextMenuRequested.connect(self.context_menu)

    def add_tree_items(self, widget):
        data_elements = DataModel.load_data()

        # Iterate through the data and assign elements to QTreeWidget elements
        for notebook_name in data_elements["Notebooks"]:
            notebook_item = QTreeWidgetItem([notebook_name])
            widget.addTopLevelItem(notebook_item)

            # Store object data to keep positions for comparable situations later
            self.item_data_map[id(notebook_item)] = notebook_name

            for note_element in data_elements["Notebooks"][notebook_name]:
                note_item = QTreeWidgetItem([note_element])
                notebook_item.addChild(note_item)

                self.item_data_map[id(note_item)] = note_element

    def refresh_tree_widget(self, widget):
        widget.clear()  # Remove all items from the widget
        self.add_tree_items(widget)  # Rebuild widget items freshly

    def context_menu(self, position):
        selected_item = Widgets.tree_widget.itemAt(position)  # Receive the item's clicked position

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

        # Emit signals for each action and process the information
        if action == "Edit":
            self.events_model.edit_signal.emit(item_data, action)
        elif action == "Delete":
            self.events_model.delete_signal.emit(item_data, action)


class MainWindow(QtWidgets.QMainWindow):

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
        self.events_model.data_changed_signal.connect(lambda: self.widgets_model.refresh_tree_widget(parent_tree_widget))

        ui.notebookActionLabel.setText("The name of your notebook")
        ui.noteActionLabel.setText("The name of your note")
        ui.noteActionSelectorLabel.setText("Parent notebook for this note")
        ui.noteActionDescriptionLabel.setText("Note text")

        ui.noteAction_comboBox.addItem("")  # Show as empty at first
        ui.noteAction_comboBox.addItems(self.data_model.load_data()["Notebooks"])  # But also fill with data

        def handle_notebook_selector():
            ui.noteAction_comboBox.clear()  # Clear content
            ui.noteAction_comboBox.addItems(self.data_model.load_data()["Notebooks"])  # Update with fresh data

        self.events_model.data_changed_signal.connect(handle_notebook_selector)

        notebook_save_button = ui.notebookActionButton
        note_save_button =  ui.noteActionButton

        save_button_text = "Save"
        notebook_save_button.setText(save_button_text)
        note_save_button.setText(save_button_text)

        notebook_save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        note_save_button.setCursor(Qt.CursorShape.PointingHandCursor)

        # Set default state for both at the beginning
        self.events_model.notebook_form_state = "notebook creation mode"
        self.events_model.note_form_state = "note creation mode"

        form_data = {}

        def prepare_forms(data, action):

            if data.get('notebook') == data.get('pressed_item'):
                self.events_model.notebook_form_state = "notebook editing mode"  # Change mode

                notebook_name = data.get('pressed_item')  # Assign value of the item where 'Edit' was pressed on
                form_data['not_changed_notebook'] = notebook_name  # Add notebook_name to notebook_data for remembering

                ui.notebookAction_lineEdit.setText(notebook_name)  # Set input field text
            elif data.get('child_note') == data.get('pressed_item'):
                self.events_model.note_form_state = "note editing mode"  # Change mode

                notebook_name = data.get('notebook')
                note_name = data.get('child_note')
                note_text = self.data_model.load_data()['Notebooks'][notebook_name][note_name]['text']

                ui.noteAction_lineEdit.setText(note_name)  # Set input field text
                ui.noteAction_comboBox.setCurrentText(notebook_name)
                ui.noteAction_textEdit.setText(note_text)

                form_data['viewed_data'] = {'note_name': note_name, 'parent_notebook': notebook_name, 'note_text': note_text}

        self.events_model.edit_signal.connect(prepare_forms)

        def state_verification(state):
            notebook_input_field = ui.notebookAction_lineEdit

            note_input_field = ui.noteAction_lineEdit
            notebook_selector_field = ui.noteAction_comboBox
            note_text_field = ui.noteAction_textEdit

            notebook_input_text = notebook_input_field.text()

            note_input_text = note_input_field.text()
            notebook_selector_text = notebook_selector_field.currentText()
            note_input_description = note_text_field.toPlainText()

            if 'notebook creation mode' in state and notebook_input_text:
                self.data_model.create_notebook(notebook_input_text)  # Handle request to JSON file
            elif 'notebook editing mode' in state and notebook_input_text:
                form_data['probably_changed_notebook'] = notebook_input_text  # Add the probably changed information from the field
                self.data_model.update_notebook(form_data)  # Handle request to JSON file
            elif 'note creation mode' in state and note_input_text:
                self.data_model.create_note(note_input_text, notebook_selector_text, note_input_description)
            elif 'note editing mode' in state and note_input_text:
                form_data['probably_changed_data'] = {'note_name': note_input_text, 'parent_notebook': notebook_selector_text, 'note_text': note_input_description}
                self.data_model.update_note(form_data)

            # Clear input fields after task has been completed
            if notebook_input_text: notebook_input_field.clear()
            if note_input_text: note_input_field.clear()
            if note_input_description: note_text_field.clear()

            if form_data: form_data.clear()

            self.events_model.data_changed_signal.emit()  # Emit signal to update both the TreeWidget and notebook selector

            self.events_model.notebook_form_state = "notebook creation mode"  # Go back to default
            self.events_model.note_form_state = "note creation mode"  # Go back to default

        ui.notebookActionButton.clicked.connect(lambda: state_verification(self.events_model.notebook_form_state))
        ui.noteActionButton.clicked.connect(lambda: state_verification(self.events_model.note_form_state))

        def delete_item(item_data, action):
            if item_data['pressed_item'] == item_data['notebook']:  # When item is a notebook
                self.data_model.delete_notebook(item_data['notebook'])
            elif item_data['pressed_item'] == item_data['child_note']:  # When item is a note
                self.data_model.delete_note(item_data['notebook'], item_data['child_note'])

            self.events_model.data_changed_signal.emit()

        self.events_model.delete_signal.connect(delete_item)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
