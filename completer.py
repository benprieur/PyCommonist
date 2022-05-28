import json
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QMetaObject
from PyQt5.QtWidgets import QTreeWidget
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtNetwork import QNetworkAccessManager
from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtNetwork import QNetworkReply
from PyQt5.QtGui import QPalette
from constants import WIDTH_WIDGET_RIGHT , \
                      WIDTH_WIDGET


''' 
    class SuggestCompletion
'''
class SuggestCompletion(QObject):

    def __init__(self, parent):
        QObject.__init__(self, parent)
        self.parent = parent
        self.editor = parent
        self.popup = QTreeWidget()
        self.popup.setWindowFlags(Qt.Popup)
        self.popup.setFocusProxy(self.parent)
        self.popup.setMouseTracking(True)
        self.popup.setColumnCount(1)
        self.popup.setFixedWidth(WIDTH_WIDGET_RIGHT)
        self.popup.setUniformRowHeights(True)
        self.popup.setRootIsDecorated(False)
        self.popup.setEditTriggers(QTreeWidget.NoEditTriggers)
        self.popup.setSelectionBehavior(QTreeWidget.SelectRows)
        self.popup.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.popup.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
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
        if obj != self.popup:
            return False
        if event.type() == QEvent.MouseButtonPress:
            self.popup.hide()
            self.editor.setFocus()
            return True
        if event.type() == QEvent.KeyPress:
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
        if not choices:
            return
        palette = self.editor.palette()
        palette.color(QPalette.Disabled, QPalette.WindowText)
        self.popup.setUpdatesEnabled(False)
        self.popup.clear()
        for choice in choices:
            item = QTreeWidgetItem(self.popup)
            item.setText(0, choice)
        self.popup.setCurrentItem(self.popup.topLevelItem(0))
        #self.popup.resizeColumnToContents(0)
        self.popup.setUpdatesEnabled(True)
        self.popup.move(self.editor.mapToGlobal(QPoint(0, self.editor.height())))
        self.popup.setFocus()
        self.popup.show()

    def done_completion(self):
        self.timer.stop()
        self.popup.hide()
        self.editor.setFocus()
        item = self.popup.currentItem()
        if item:
            self.editor.setText(item.text(0))
            QMetaObject.invokeMethod(self.editor, 'returnPressed')

    def auto_suggest(self):
        text = self.editor.text()
        req = "https://commons.wikimedia.org/w/api.php?action=query&list=prefixsearch&format=json"
        req += "&pssearch=" + "Category:" + text
        url = QUrl(req)
        self.network_manager.get(QNetworkRequest(url))

    def prevent_suggest(self):
        self.timer.stop()

    def handle_network_data(self, network_reply):
        choices = []
        if network_reply.error() == QNetworkReply.NoError:
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
        super(SearchBox, self).__init__(parent)
        self.completer = SuggestCompletion(self)
        self.setFixedWidth(round(WIDTH_WIDGET_RIGHT / 2))
        self.setClearButtonEnabled(True)