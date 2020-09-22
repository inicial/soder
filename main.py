import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import ui.design
from ui.editor import QCodeEditor
from ui.XMLhighlighter import XMLHighlighter
from ui.PYhighlighter import PythonHighlighter


ORGANIZATION_NAME = 'Soder App'
ORGANIZATION_DOMAIN = 'soder.com'
APPLICATION_NAME = 'Soder'
SETTINGS_TRAY = 'settings/tray'


class EditorApp(QMainWindow, ui.design.Ui_MainWindow):

    lines = None
    filename = "Untitled*" or None
    CURRENT_PATH = None
    CURRENT_PATH_FILE = None


    def __init__(self):
        super().__init__()
        self.setupUi(self)

        settings = QSettings()
        # Забираем состояние чекбокса, с указанием типа данных:
        # type=bool является заменой метода toBool() в PyQt5
        self.lines = settings.value(SETTINGS_TRAY, False, type=bool)
        # Устанавливаем состояние
        self.line_numbers.setChecked(self.lines)
        # подключаем слот к сигналу клика по чекбоксу, чтобы созранять его состояние в настройках
        self.line_numbers.clicked.connect(self.save_check_box_settings)
        self.line_numbers.clicked.connect(self.check_lines_state)

        self.codeEditor = self.check_lines_state()

        # self.tabWidget.addTab(self.codeEditor, self.filename)
        self.tabWidget.tabCloseRequested.connect(lambda index: self.tabWidget.removeTab(index))
        # self.tabWidget.insertTab(lambda index: self.tabWidget.addTab(index, self.filename))
        # self.verticalLayout.addWidget(self.codeEditor)

        self.action_Open.triggered.connect(self.file_open)
        self.action_Save.triggered.connect(self.save_file)
        self.action_Save_as.triggered.connect(self.save_file_as)
        
        self.set_active_saving()
        
        self.action_Exit.triggered.connect(qApp.quit)
        self.action_New.triggered.connect(self.new_file)
        self.action_Open_Project.triggered.connect(self.open_project)
        self.actionClose_Project.triggered.connect(self.close_project)

        self.treeView.doubleClicked.connect(self.choose_file)


    def check_sevefile_button(self):
        pass


    def check_lines_state(self):
        self.codeEditor = QCodeEditor(DISPLAY_LINE_NUMBERS=self.lines,
                                      HIGHLIGHT_CURRENT_LINE=True,
                                      SyntaxHighlighter=[x for x in (XMLHighlighter, PythonHighlighter)])
        return self.codeEditor


    def save_file(self):
        if os.path.exists(self.CURRENT_PATH_FILE) and "Untitled*" or None:
            with open(self.CURRENT_PATH_FILE, 'wb') as file:
                text = self.codeEditor.toPlainText()
                file.write(text.encode())
        else:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save file as...", "",
                                                       "Python Files (*.py)", options=options)
            if file_name:
                tab = QCodeEditor(DISPLAY_LINE_NUMBERS=self.lines,
                                  HIGHLIGHT_CURRENT_LINE=True,
                                  SyntaxHighlighter=[x for x in (XMLHighlighter, PythonHighlighter)])
                with open(file_name, 'wb') as file:
                    text = self.codeEditor.toPlainText()
                    file.write(text.encode())
                tab.setPlainText(text)
                self.filename = file_name
                title = os.path.split(self.filename)
                tab_index = self.tabWidget.addTab(tab, title[1])
                try:
                    self.tabWidget.removeTab(tab_index-1)
                except Exception as ex:
                    print(ex)
                tab.moveCursor(QTextCursor.End)
                self.CURRENT_PATH_FILE = self.filename


    def save_file_as(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save file as...", "",
                                                   "Python Files (*.py)", options=options)
        if file_name:
            tab = QCodeEditor(DISPLAY_LINE_NUMBERS=self.lines,
                              HIGHLIGHT_CURRENT_LINE=True,
                              SyntaxHighlighter=[x for x in (XMLHighlighter, PythonHighlighter)])
            with open(file_name, 'wb') as file:
                text = self.codeEditor.toPlainText()
                file.write(text.encode())
            tab.setPlainText(text)
            self.filename = file_name
            title = os.path.split(self.filename)
            tab_index = self.tabWidget.addTab(tab, title[1])
            try:
                self.tabWidget.removeTab(tab_index-1)
            except Exception as ex:
                print(ex)
            tab.moveCursor(QTextCursor.End)
            self.CURRENT_PATH_FILE = self.filename


    def file_open(self):
        self.set_active_saving(False)
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                                                   "All Files (*);;Python Files (*.py)", options=options)

        if file_name:

            tab = QCodeEditor(DISPLAY_LINE_NUMBERS=self.lines,
                              HIGHLIGHT_CURRENT_LINE=True,
                              SyntaxHighlighter=[x for x in (XMLHighlighter, PythonHighlighter)])
            with open(file_name, 'rb') as file:
                text = file.read()
                tab.setPlainText(text.decode())
            tab.moveCursor(QTextCursor.End)
            self.filename = file_name

            title = []

            if file_name not in title:
                global tab_index
                self.tabWidget.addTab(tab, self.filename)
                tab_index = self.tabWidget.addTab(tab, self.filename)
                self.codeEditor = tab
                self.tabWidget.setCurrentIndex(tab_index)
                title.append(self.tabWidget.tabText(tab_index))
            elif file_name in title:
                for x in title:
                    if x == file_name:
                        self.tabWidget.setCurrentWidget(tab)


    def new_file(self):
        self.set_active_saving(False)

        self.filename = "Untitled*" or None
        tab = QCodeEditor(DISPLAY_LINE_NUMBERS=self.lines,
                          HIGHLIGHT_CURRENT_LINE=True,
                          SyntaxHighlighter=[x for x in (XMLHighlighter, PythonHighlighter)])
        self.tabWidget.addTab(tab, self.filename)
        self.codeEditor = tab
        self.CURRENT_PATH_FILE = self.filename



    def open_project(self):
        path = QFileDialog.getExistingDirectory(self, "Select a folder", '', QFileDialog.ShowDirsOnly)
        model = QFileSystemModel()
        model.setRootPath(path)
        self.tree = self.treeView
        self.tree.setModel(model)
        self.tree.hideColumn(2)
        self.tree.hideColumn(3)
        self.tree.setRootIndex(model.index(path))
        self.tree.setColumnWidth(0, 250)
        self.tree.setAlternatingRowColors(True)
        self.CURRENT_PATH = path
        name = os.path.split(path)
        self.dockWidget_5.setWindowTitle("Project: "+name[1])

    def close_project(self):
        model = QFileSystemModel()
        self.tree = self.treeView
        self.tree.setModel(None)
        self.dockWidget_5.setWindowTitle("Project: ")


    # Слот для сохранения настроек чекбокса
    def save_check_box_settings(self):
        settings = QSettings()
        settings.setValue(SETTINGS_TRAY, self.line_numbers.isChecked())
        settings.sync()


    def choose_file(self, index: int):
        self.sender() == self.treeView
        path = self.sender().model().filePath(index)
        tab = QCodeEditor(DISPLAY_LINE_NUMBERS=self.lines,
                              HIGHLIGHT_CURRENT_LINE=True,
                              SyntaxHighlighter=[x for x in (XMLHighlighter, PythonHighlighter)])
        if path is not dir:
            with open(path, 'rb') as file:
                text = file.read()
                tab.setPlainText(text.decode())
            tab.moveCursor(QTextCursor.End)
            title = os.path.split(path)
            self.filename = title[1]
            self.CURRENT_PATH_FILE = path
            self.set_active_saving(False)

            title = []

            if path not in title:
                global tab_index
                self.tabWidget.addTab(tab, self.filename)
                tab_index = self.tabWidget.addTab(tab, self.filename)
                self.codeEditor = tab
                self.tabWidget.setCurrentIndex(tab_index)
                title.append(self.tabWidget.tabText(tab_index))
            elif path in title:
                for x in title:
                    if x == path:
                        self.tabWidget.setCurrentWidget(tab)
    
    
    def set_active_saving(self, state: bool = True):
        self.action_Save_as.setDisabled(state)
        self.action_Save.setDisabled(state)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    QCoreApplication.setApplicationName(ORGANIZATION_NAME)
    QCoreApplication.setOrganizationDomain(ORGANIZATION_DOMAIN)
    QCoreApplication.setApplicationName(APPLICATION_NAME)

    app = QApplication(sys.argv)

    editorApp = EditorApp()
    editorApp.show()

    sys.exit(app.exec_())
