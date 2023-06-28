import json
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QUrl
from PyQt6.QtCore import QObject
from PyQt6.QtCore import QTimer
from PyQt6.QtCore import QEvent
from PyQt6.QtCore import QPoint
from PyQt6.QtCore import QMetaObject
from PyQt6.QtWidgets import QTreeWidget
from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtWidgets import QFrame
from PyQt6.QtWidgets import QTreeWidgetItem
from PyQt6.QtWidgets import QAbstractItemView
from PyQt6.QtNetwork import QNetworkAccessManager
from PyQt6.QtNetwork import QNetworkRequest
from PyQt6.QtNetwork import QNetworkReply
from PyQt6.QtGui import QPalette
from constants import WIDTH_WIDGET_RIGHT


''' 
    class SuggestCompletion
'''


class SuggestCompletion(QObject):

    def __init__(self, parent):
        """ __init__ """
        QObject.__init__(self, parent)
        self.parent = parent
        self.editor = parent
        self.popup = QTreeWidget()
        self.popup.setWindowFlags(Qt.WindowType.Popup)
        self.popup.setFocusProxy(self.parent)
        self.popup.setMouseTracking(True)
        self.popup.setColumnCount(1)
        self.popup.setFixedWidth(WIDTH_WIDGET_RIGHT)
        self.popup.setUniformRowHeights(True)
        self.popup.setRootIsDecorated(False)
        self.popup.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.popup.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.popup.setFrameStyle(QFrame.Shape.Box) 
        self.popup.setLineWidth(1) # | QFrame Plain
        self.popup.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.popup.header().hide()
        self.timer = None
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(500)
        self.network_manager = QNetworkAccessManager(self)
        self.popup.installEventFilter(self)
        self.popup.itemClicked.connect(self.done_completion)
        self.timer.timeout.connect(self.auto_suggest)
        self.editor.textEdited.connect(self.timer.start)
        self.network_manager.finished.connect(self.handle_network_data)

    def eventFilter(self, obj, event):
        """ eventFilter """
        if obj != self.popup:
            return False
        if event.type() == QEvent.Type.MouseButtonPress:
            self.popup.hide()
            self.editor.setFocus()
            return True
        if event.type() == QEvent.Type.KeyPress:
            consumed = False
            key = event.key()
            if key in [Qt.Key_Enter, Qt.Key_Return]:
                self.done_completion()
                consumed = True
            elif key == Qt.Key_Escape:
                self.editor.setFocus()
                self.popup.hide()
                consumed = True
            elif key in [Qt.Key_Up, Qt.Key_Down, Qt.Key_Home, Qt.Key_End, Qt.Key_PageUp, Qt.Key_PageDown]:
                pass
            else:
                self.editor.setFocus()
                self.editor.event(event)
                self.popup.hide()
            return consumed
        return False

    def show_completion(self, choices):
        """ show_completion """
        if not choices:
            return
        palette = self.editor.palette()
        palette.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText)
        self.popup.setUpdatesEnabled(False)
        self.popup.clear()
        for choice in choices:
            item = QTreeWidgetItem(self.popup)
            item.setText(0, choice)
        self.popup.setCurrentItem(self.popup.topLevelItem(0))
        # self.popup.resizeColumnToContents(0)
        self.popup.setUpdatesEnabled(True)
        self.popup.move(self.editor.mapToGlobal(
            QPoint(0, self.editor.height())))
        self.popup.setFocus()
        self.popup.show()

    def done_completion(self):
        """ done_completion """
        self.timer.stop()
        self.popup.hide()
        self.editor.setFocus()
        item = self.popup.currentItem()
        if item:
            self.editor.setText(item.text(0))
            QMetaObject.invokeMethod(self.editor, 'returnPressed')

    def auto_suggest(self):
        """ auto_suggest """
        text = self.editor.text()
        req = "https://commons.wikimedia.org/w/api.php?action=query&list=prefixsearch&format=json"
        req += "&pssearch=" + "Category:" + text
        url = QUrl(req)
        self.network_manager.get(QNetworkRequest(url))

    def prevent_suggest(self):
        """ prevent_suggest """
        self.timer.stop()

    def handle_network_data(self, network_reply):
        """ handle_network_data """
        choices = []
        if network_reply.error() == QNetworkReply.NetworkError.NoError:
            data = json.loads(network_reply.readAll().data())
            for location in data['query']['prefixsearch']:
                choice = location['title']
                choices.append(choice.replace("Category:", ""))
            self.show_completion(choices)
        network_reply.deleteLater()


''' 
    class SearchBox
'''


class SearchBox(QLineEdit):

    def __init__(self, parent=None):
        """ __init__ """
        super(SearchBox, self).__init__(parent)
        self.completer = SuggestCompletion(self)
        self.setFixedWidth(round(WIDTH_WIDGET_RIGHT / 2))
        self.setClearButtonEnabled(True)
