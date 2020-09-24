from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from ui.QLine import QLineNumberArea


class QCodeEditor(QPlainTextEdit):
    # def __init__(self, parent=None):
    #     super().__init__(parent)
    #
    #     self.lineNumberArea = QLineNumberArea(self)
    #     self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
    #     self.updateRequest.connect(self.updateLineNumberArea)
    #     self.cursorPositionChanged.connect(self.highlightCurrentLine)
    #     self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, *e):
        '''overload resizeEvent handler'''

        if self.DISPLAY_LINE_NUMBERS:  # resize number_bar widget
            cr = self.contentsRect()
            rec = QRect(cr.left(), cr.top(), self.number_bar.getWidth(), cr.height())
            self.number_bar.setGeometry(rec)

        QPlainTextEdit.resizeEvent(self, *e)

    def highligtCurrentLine(self):
        newCurrentLineNumber = self.textCursor().blockNumber()
        if newCurrentLineNumber != self.currentLineNumber:
            self.currentLineNumber = newCurrentLineNumber
            hi_selection = QTextEdit.ExtraSelection()
            hi_selection.format.setBackground(self.currentLineColor)
            hi_selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            hi_selection.cursor = self.textCursor()
            hi_selection.cursor.clearSelection()
            self.setExtraSelections([hi_selection])

    def lineNumberAreaWidth(self):
        digits = 5
        max_value = max(1, self.blockCount())
        while max_value >= 10:
            max_value /= 10
            # digits += 1
        space = 0 + self.fontMetrics().width('5') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(Qt.darkGray).lighter(180)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)

        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        # Just to make sure I use the right font
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, top, self.lineNumberArea.width(), height, Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    # class NumberBar(QWidget):
    #     '''class that deifnes textEditor numberBar'''
    #
    #     def __init__(self, editor):
    #         QWidget.__init__(self, editor)
    #
    #         self.editor = editor
    #         self.editor.blockCountChanged.connect(self.updateWidth)
    #         self.editor.updateRequest.connect(self.updateContents)
    #         self.font = QFont()
    #         self.numberBarColor = QColor("#e8e8e8")
    #
    #     def paintEvent(self, event):
    #
    #         painter = QPainter(self)
    #         painter.fillRect(event.rect(), self.numberBarColor)
    #
    #         block = self.editor.firstVisibleBlock()
    #
    #         # Iterate over all visible text blocks in the document.
    #         while block.isValid():
    #             blockNumber = block.blockNumber()
    #             block_top = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top()
    #
    #             # Check if the position of the block is out side of the visible area.
    #             if not block.isVisible() or block_top >= event.rect().bottom():
    #                 break
    #
    #             # We want the line number for the selected line to be bold.
    #             if blockNumber == self.editor.textCursor().blockNumber():
    #                 self.font.setBold(True)
    #                 painter.setPen(QColor("#000000"))
    #             else:
    #                 self.font.setBold(False)
    #                 painter.setPen(QColor("#717171"))
    #             painter.setFont(self.font)
    #
    #             # Draw the line number right justified at the position of the line.
    #             paint_rect = QRect(0, block_top, self.width(), self.editor.fontMetrics().height())
    #             painter.drawText(paint_rect, Qt.AlignRight, str(blockNumber + 1))
    #
    #             block = block.next()
    #
    #         painter.end()
    #
    #         QWidget.paintEvent(self, event)
    #
    #     def getWidth(self):
    #         count = self.editor.blockCount()
    #         width = self.fontMetrics().width(str(count)) + 10
    #         return width
    #
    #     def updateWidth(self):
    #         width = self.getWidth()
    #         if self.width() != width:
    #             self.setFixedWidth(width)
    #             self.editor.setViewportMargins(width, 0, 0, 0);
    #
    #     def updateContents(self, rect, scroll):
    #         if scroll:
    #             self.scroll(0, scroll)
    #         else:
    #             self.update(0, rect.y(), self.width(), rect.height())
    #
    #         if rect.contains(self.editor.viewport().rect()):
    #             fontSize = self.editor.currentCharFormat().font().pointSize()
    #             self.font.setPointSize(fontSize)
    #             self.font.setStyle(QFont.StyleNormal)
    #             self.updateWidth()

    def __init__(self, DISPLAY_LINE_NUMBERS=True, HIGHLIGHT_CURRENT_LINE=True,
                 SyntaxHighlighter=None, *args):
        '''
        Parameters
        ----------
        DISPLAY_LINE_NUMBERS : bool
            switch on/off the presence of the lines number bar
        HIGHLIGHT_CURRENT_LINE : bool
            switch on/off the current line highliting
        SyntaxHighlighter : QSyntaxHighlighter
            should be inherited from QSyntaxHighlighter

        '''
        super(QCodeEditor, self).__init__()

        self.lineNumberArea = QLineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)

        self.setFont(QFont("Consolas", 10))
        self.setLineWrapMode(QPlainTextEdit.NoWrap)

        self.DISPLAY_LINE_NUMBERS = DISPLAY_LINE_NUMBERS

        # if DISPLAY_LINE_NUMBERS:
        #     self.number_bar = self.NumberBar(self)

        if HIGHLIGHT_CURRENT_LINE:
            self.currentLineNumber = None
            self.currentLineColor = self.palette().alternateBase()
            self.currentLineColor = QColor("#e8e8e8")
            # self.cursorPositionChanged.connect(self.highligtCurrentLine)

        for h in SyntaxHighlighter:
            if SyntaxHighlighter is not None:  # add highlighter to textdocument
                self.highlighter = h(self.document())

    # def resizeEvent(self, *e):
    #     '''overload resizeEvent handler'''
    #
    #     if self.DISPLAY_LINE_NUMBERS:  # resize number_bar widget
    #         cr = self.contentsRect()
    #         rec = QRect(cr.left(), cr.top(), self.number_bar.getWidth(), cr.height())
    #         self.number_bar.setGeometry(rec)
    #
    #     QPlainTextEdit.resizeEvent(self, *e)

    # def highligtCurrentLine(self):
    #     newCurrentLineNumber = self.textCursor().blockNumber()
    #     if newCurrentLineNumber != self.currentLineNumber:
    #         self.currentLineNumber = newCurrentLineNumber
    #         hi_selection = QTextEdit.ExtraSelection()
    #         hi_selection.format.setBackground(self.currentLineColor)
    #         hi_selection.format.setProperty(QTextFormat.FullWidthSelection, True)
    #         hi_selection.cursor = self.textCursor()
    #         hi_selection.cursor.clearSelection()
    #         self.setExtraSelections([hi_selection])
