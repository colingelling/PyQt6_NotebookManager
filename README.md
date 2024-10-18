# Notable desktop app (PyQt6_NotebookManager) - v1.0
---
This repository contains various versions of a desktop app made with Python (3.9) and PyQt6. The app itself had two requirements mentioned below:

1. Maximum amount of 4 classes
2. Maximum amount of 400 lines

This project was originally designed to serve as a note-taking application for creating, modifying and removing notebooks. The same thing for notes, except that they would have parent notebooks and that notes would be movable between notebooks.

---

#### Minimal functionality

The application needed to have the functionality that was described earlier, this project was a huge learning process while making something that follows the MVP guidelines.

---

#### Functionality explained (MainWindow) 
The initialization part begins with the MainWindow class which is the application center for version 1.0 of the desktop app. 

###### 1. QTreeWidget
Besides some basic window properties, the main window called 'Overview' contains the execution of QTreeWidget for showing data out of a JSON file. Which will be created if you launch the application for the first time through a Python interpreter.

###### 2. Notebook form
Below the top widget, the window has one of two forms which could be used to either create a new notebook or edit an existing notebook. That, if you right-click on it, coming from the tree.

###### 3. Note form
Below that, another form is available for either creating or editing notes. And again, editing goes through right-clicking on an existing note.

---

### States
Either creation or editing events for both are featured as to be different states. The default state is for both 'creation mode' and 'editing mode' will be activated as soon as you click 'Edit' on one of the two, notebook or note alike. This was a practical decision because of choosing what to do between notebooks and notes related to the generated JSON file. 

---

### Refreshing QTreeWidget and the QcomboBox notebook selector
Actions such as a button click, or context-menu option have connections with functionality to update both the tree and parent-notebook selections. 

---

Input fields within the form of your choice will be cleared after the task has been completed. The active notebook selector will be set to be blank incase of a completed note form task.