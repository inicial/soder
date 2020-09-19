# import sys
# from PyQt5.QtWidgets import *
# from PyQt5.QtGui import *
# from PyQt5.QtCore import *
# import design
#
# import numpy as np
#
#
# class QLineNumberArea(QWidget):
#     def __init__(self, editor):
#         super().__init__(editor)
#         self.codeEditor = editor
#
#     def sizeHint(self):
#         return QSize(self.editor.lineNumberAreaWidth(), 0)
#
#     def paintEvent(self, event):
#         self.codeEditor.lineNumberAreaPaintEvent(event)
#
#
# class EditorApp(QMainWindow, design.Ui_MainWindow):
#
#     def __init__(self):
#         super().__init__()
#         self.setupUi(self)
#
#         self.action_Open.triggered.connect(self.file_open)
#         self.action_Save_File.triggered.connect(self.file_save)
#         self.action_Exit.triggered.connect(qApp.quit)
#
#         self.lineNumberArea = QLineNumberArea(self)
#         self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
#         self.updateRequest.connect(self.updateLineNumberArea)
#         self.cursorPositionChanged.connect(self.highlightCurrentLine)
#         self.updateLineNumberAreaWidth(0)
#
#     def file_save(self):
#         options = QFileDialog.Options()
#         options |= QFileDialog.DontUseNativeDialog
#         file_name, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
#                                                    "All Files (*);;Python Files (*.py)", options=options)
#         if file_name:
#             with open(file_name, 'w') as file:
#                 text = self.textEditor.toPlainText()
#                 file.write(text)
#                 file.close()
#
#     def file_open(self):
#         options = QFileDialog.Options()
#         options |= QFileDialog.DontUseNativeDialog
#         file_name, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
#                                                    "All Files (*);;Python Files (*.py)", options=options)
#         if file_name:
#             with open(file_name, 'r+') as file:
#                 text = file.read()
#                 self.textEditor.setPlainText(text)
#             self.textEditor.moveCursor(QTextCursor.End)
#
#     def lineNumberAreaWidth(self):
#         digits = 1
#         max_value = max(1, self.blockCount())
#         while max_value >= 10:
#             max_value /= 10
#             digits += 1
#         space = 3 + self.fontMetrics().width('9') * digits
#         return space
#
#     def updateLineNumberAreaWidth(self, _):
#         self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)
#
#     def updateLineNumberArea(self, rect, dy):
#         if dy:
#             self.lineNumberArea.scroll(0, dy)
#         else:
#             self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
#         if rect.contains(self.viewport().rect()):
#             self.updateLineNumberAreaWidth(0)
#
#     def resizeEvent(self, event):
#         super().resizeEvent(event)
#         cr = self.contentsRect()
#         self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))
#
#     def highlightCurrentLine(self):
#         extraSelections = []
#         if not self.isReadOnly():
#             selection = QTextEdit.ExtraSelection()
#             lineColor = QColor(Qt.yellow).lighter(160)
#             selection.format.setBackground(lineColor)
#             selection.format.setProperty(QTextFormat.FullWidthSelection, True)
#             selection.cursor = self.textCursor()
#             selection.cursor.clearSelection()
#             extraSelections.append(selection)
#         self.setExtraSelections(extraSelections)
#
#     def lineNumberAreaPaintEvent(self, event):
#         painter = QPainter(self.lineNumberArea)
#
#         painter.fillRect(event.rect(), Qt.lightGray)
#
#         block = self.firstVisibleBlock()
#         blockNumber = block.blockNumber()
#         top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
#         bottom = top + self.blockBoundingRect(block).height()
#
#         # Just to make sure I use the right font
#         height = self.fontMetrics().height()
#         while block.isValid() and (top <= event.rect().bottom()):
#             if block.isVisible() and (bottom >= event.rect().top()):
#                 number = str(blockNumber + 1)
#                 painter.setPen(Qt.black)
#                 painter.drawText(0, top, self.lineNumberArea.width(), height, Qt.AlignRight, number)
#
#             block = block.next()
#             top = bottom
#             bottom = top + self.blockBoundingRect(block).height()
#             blockNumber += 1
#
#
# def main():
#     app = QApplication(sys.argv)
#     window = EditorApp()
#     window.show()
#     sys.exit(app.exec_())
#
#
# if __name__ == '__main__':
#     main()
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
        self.action_Save_as.triggered.connect(self.save_file)
        self.action_Exit.triggered.connect(qApp.quit)
        self.action_New.triggered.connect(self.new_file)
        self.action_Open_Project.triggered.connect(self.open_project)

    def check_lines_state(self):
        self.codeEditor = QCodeEditor(DISPLAY_LINE_NUMBERS=self.lines,
                                      HIGHLIGHT_CURRENT_LINE=True,
                                      SyntaxHighlighter=[x for x in (XMLHighlighter, PythonHighlighter)])
        return self.codeEditor

    def save_file(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'wb') as file:
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
                tab_index = self.tabWidget.addTab(tab, self.filename)
                try:
                    self.tabWidget.removeTab(tab_index)
                except Exception as ex:
                    print(ex)
                self.tabWidget.addTab(tab, self.filename)
                tabs = self.tabWidget
                self.codeEditor = tab

    def file_open(self):
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
        self.filename = "Untitled*" or None
        tab = QCodeEditor(DISPLAY_LINE_NUMBERS=self.lines,
                          HIGHLIGHT_CURRENT_LINE=True,
                          SyntaxHighlighter=[x for x in (XMLHighlighter, PythonHighlighter)])
        self.tabWidget.addTab(tab, self.filename)
        self.codeEditor = tab

    def open_project(self):
        path = QFileDialog.getExistingDirectory(self, "Select a folder", "", QFileDialog.ShowDirsOnly)
        startpath = os.listdir(path)
        # for root, dirs, files in os.walk(path):
        self.model = QFileSystemModel()
        self.tree = self.treeView
        self.tree.setRootIndex(self.model.index(path))
        self.tree.setModel(self.model)
            # h = QTreeWidgetItem([os.path.basename(root), ''])
            # h.setDisabled(True)
            # tw.addTopLevelItem(h)

            # level = root.replace(path, '').count(os.sep)
            # indent = ' ' * 4 * (level)
            # print('{}{}/'.format(indent, os.path.basename(root)))
            # subindent = ' ' * 4 * (level + 1)
            # for f in files:
            #     print('{}{}'.format(subindent, f))

    # Слот для сохранения настроек чекбокса
    def save_check_box_settings(self):
        settings = QSettings()
        settings.setValue(SETTINGS_TRAY, self.line_numbers.isChecked())
        settings.sync()


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
