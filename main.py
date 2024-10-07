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
    data_signal = pyqtSignal()
    notebook_edit_signal = pyqtSignal(dict)
    top_level_item_clicked = pyqtSignal(str)  # Signal to send item text

    notebook_form_state = None
    note_form_state = None

    def __init__(self, widget):
        super(Events, self).__init__()
        self.tree_widget = widget

        self.tree_event_data = None

    def _set_filtered_item_data(self, item):
        parent_item = item.parent()

        if parent_item:
            self.tree_event_data = {
                'parent_notebook': parent_item.text(0),
                'child_note': item.text(0)
            }

        else:
            self.tree_event_data = {
                'notebook': item.text(0),
            }

    def mousePressEvent(self, event):
        item = self.tree_widget.itemAt(event.pos())  # Locate the item
        self._set_filtered_item_data(item)  # The setup of a set containing item data based on the event

        index = self.tree_widget.indexAt(event.pos())
        tree_item_name = index.data(Qt.ItemDataRole.DisplayRole)

        # TODO: Updating the QlineEdit (QTreeWidget) is not possible because of the new MainWindow instance
        main_window = MainWindow()
        main_window.tree_event_data = self.tree_event_data
        if item: main_window.context_menu_func(event, main_window.edit_notebook_obj, tree_item_name, self.tree_event_data)  # Trigger the context menu if the item is there

        # Return to normal behavior
        QTreeWidget.mousePressEvent(self.tree_widget, event)

    def getFilteredChildNoteData(self):
        if 'child_note' in self.tree_event_data:
            return self.tree_event_data


class Widgets:
    tree_widget = None
    item_data_map = {}

    def __init__(self):
        super(Widgets, self).__init__()

    @staticmethod
    def TreeWidgetItems(widget):
        # Readability reference declaration
        data_elements = DataModel.load_data()

        # Iterate through the data and assign elements to QTreeWidget elements
        for notebook_name in data_elements["Notebooks"]:
            notebook_item = QTreeWidgetItem([notebook_name])
            widget.addTopLevelItem(notebook_item)

            Widgets.item_data_map[id(notebook_item)] = notebook_name

            for note_element in data_elements["Notebooks"][notebook_name]:
                note_item = QTreeWidgetItem([note_element])
                notebook_item.addChild(note_item)

                Widgets.item_data_map[id(note_item)] = note_element

    def context_menu(self, position, item_data):
        # Get the item at the clicked position
        selected_item = Widgets.tree_widget.itemAt(position)

        if selected_item:
            # Create a context menu
            menu = QMenu()

            # Add 'Show' option
            show_action = menu.addAction('Show')

            # Connect 'Show' action to a function
            show_action.triggered.connect(lambda: self.show_item(selected_item))

            # Display the context menu at the mouse position
            menu.exec(Widgets.tree_widget.viewport().mapToGlobal(position))
        # if event.button() == Qt.MouseButton.RightButton:
        #
        #     menu = QMenu()
        #
        #     delete_action = QAction("Delete")
        #     edit_action = QAction("Edit")
        #
        #     menu.setCursor(Qt.CursorShape.PointingHandCursor)
        #
        #     # TODO: Include both buttons for notebooks and notes
        #
        #     # edit_action.triggered.connect(MainWindow.view_note_obj)  # TODO: Forward to DataModel.update_x
        #     # delete_action.triggered.connect(lambda: verify_action(item_name, collected_item_data))  # TODO: Forward to DataModel.delete_x
        #
        #     # The open_note functionality already has the ability to edit
        #     if 'child_note' not in collected_item_data:
        #         edit_action.triggered.connect(lambda: obj(collected_item_data))
        #         menu.addAction(edit_action)
        #
        #     # open contextmenu
        #     menu.addAction(delete_action)
        #
        #     menu.exec(event.globalPosition().toPoint())

    def show_item(self, item):
        if item.parent() is None:
            # emit signal that the item has been clicked
            print(item, " has been pressed")
            pass


class MainWindow(QtWidgets.QMainWindow, Widgets, DataModel):
    context_menu_func = None

    edit_notebook_obj = None
    view_note_obj = None

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

        self.tree_widget_data = None

        self.content()

    def content(self):
        ui = self.ui

        self.setFixedSize(534, 834)

        ui.notebookManagerTitleLabel.setText("Management of my notebooks")
        ui.notebookManagerTitleLabel.adjustSize()

        tree_widget = ui.QtreeWidget

        # QTreeWidget customisation
        tree_widget.setHeaderHidden(True)

        # Execute functionality
        Widgets.TreeWidgetItems(tree_widget)

        def refresh_tree_widget():
            tree_widget.clear()  # Remove all items from the widget
            Widgets.TreeWidgetItems(tree_widget)  # Rebuild widget items

        # One time model declaration, need the same signals for passing through functions
        events_model = Events(tree_widget)

        # Set a connection from the view passed signal and connect it with functionality in order to rebuild QTreeWidget items
        events_model.data_signal.connect(refresh_tree_widget)

        Widgets.tree_widget = tree_widget

        # # Enable mouse tracking and override method for right-clicking support
        # tree_widget.setMouseTracking(True)
        # tree_widget.mousePressEvent = events_model.mousePressEvent

        tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tree_widget.customContextMenuRequested.connect(Widgets.context_menu)

        # self.context_menu_func = Widgets.context_menu

        # # TODO: open_note process
        # tree_widget.clicked.connect(
        #     lambda: read_note(events_model, events_model.getFilteredChildNoteData())
        #     if events_model.getFilteredChildNoteData() else None
        # )

        if not events_model.notebook_form_state:
            events_model.notebook_form_state = "notebook creation mode"

        def add_notebook():
            # Serve window properties as being the default mode
            notebook_name = ui.notebookAction_lineEdit.text()
            print(f"Create notebook using '{notebook_name}'")
            DataModel.create_notebook(notebook_name)

            # Send signal that the view side could be updated
            events_model.data_signal.emit()

        def edit_notebook(item_data):
            # events_model.notebook_form_state = "notebook editing mode"
            # print(events_model.notebook_form_state)
            # notebook_name = ui.notebookAction_lineEdit.text()

            print(f"notebook '{item_data['notebook']}' has been pressed - item_data: '{item_data}'")

            events_model.notebook_form_state = "notebook editing mode"
            events_model.notebook_edit_signal.emit(item_data)

            ui.notebookAction_lineEdit.connect(handle_notebook_input)

            print(f"Editing notebook '{item_data['notebook']}'")
            # DataModel.update_notebook(notebook_name)

            # Send signal that the view side could be updated
            events_model.data_signal.emit()

        def handle_notebook_input(item_data):
            notebook_text = item_data.get('notebook', '')  # Safely access the notebook value
            print(f"handle_notebook_input: {notebook_text}")

            if notebook_text:
                ui.notebookAction_lineEdit.setText(notebook_text)  # Update the QLineEdit
                ui.notebookAction_lineEdit.repaint()  # Force update

        events_model.notebook_edit_signal.connect(handle_notebook_input)

        self.edit_notebook_obj = edit_notebook

        def check_state(value):
            print("State: ", value, '\n')
            if "creation mode" in value and "notebook" in value:
                print('Creation mode active')
                add_notebook()
            # elif "editing mode" in value and "notebook" in value:
            #     # Signal has been set, continue to Edit mode
            #     print("Edit mode active")
            #     edit_notebook()

        button_text = "Save"
        ui.notebookActionButton.setText(button_text)
        ui.noteActionButton.setText(button_text)

        ui.notebookActionButton.clicked.connect(lambda: check_state(events_model.notebook_form_state))
        ui.notebookActionButton.setCursor(Qt.CursorShape.PointingHandCursor)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()

