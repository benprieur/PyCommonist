'''
    UploadTool.py
'''
import traceback
import requests
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QTimer
from constants import URL
from ProcessImageUpload import ProcessImageUpload
from constants import TIMESTAMP_STATUSBAR


'''
    class UploadTool
'''
class UploadTool:
    session = None
    widget = None
    check_thread_timer = None
    login = ""
    password = ""

    def upload_images(self, w):
        """ upload_images """
        try:
            self.widget = w
            self.widget.clear_status()
            self.login = self.widget.line_edit_user_name.text()
            self.password = self.widget.line_edit_password.text()
            if len(self.login) == 0:
                self.widget.btn_import.setEnabled(True)
                self.widget.set_status("Login is not filled")
                return
            if len(self.password) == 0:
                self.widget.btn_import.setEnabled(True)
                self.widget.set_status("Password is not filled")
                return
            if len(self.widget.current_upload) == 0:
                self.widget.btn_import.setEnabled(True)
                self.widget.set_status("No image selected for upload")
                return
            self.widget.threads.clear()
            self.widget.workers.clear()
            self.session = requests.Session()
            print("UploadTool.py-40 session: " + str(self.session))
            params_1 = {
                "action": "query",
                "meta": "tokens",
                "type": "login",
                "format": "json"
            }
            http_ret = self.session.get(url=URL, params=params_1)
            print("UploadTool.py-50 http ret (1): " + str(http_ret.json()))
            login_token = http_ret.json()["query"]["tokens"]["logintoken"]
            params_2 = {
                'action': "clientlogin",
                'username': self.login,
                'password': self.password,
                'loginreturnurl': URL,
                'logintoken': login_token,
                'format': "json"
            }
            http_ret = self.session.post(URL, data=params_2)
            print("UploadTool.py-60 http ret (2): " + str(http_ret.json()))
            if http_ret.json()['clientlogin']['status'] != 'PASS':
                self.widget.btn_import.setEnabled(True)
                self.widget.set_status("Client login failed")
                return
            checked_image_count = 0
            for element in self.widget.current_upload:
                try:
                    if element.cb_import.isChecked():
                        checked_image_count = checked_image_count + 1
                except ValueError:
                    print("UploadTool.pu-70: element.cb_import.isChecked(")
            self.widget.init_upload(checked_image_count)
            if self.check_thread_timer is None:
                self.check_thread_timer = QTimer()
            self.check_thread_timer.stop()
            self.check_thread_timer.setInterval(TIMESTAMP_STATUSBAR)
            self.check_thread_timer.timeout.connect(self.update_status_bar)
            self.check_thread_timer.start(TIMESTAMP_STATUSBAR)
            self.widget.current_image_index = 0
            for element in self.widget.current_upload:
                if element.cb_import.isChecked():
                    path = self.widget.current_directory_path
                    session = self.session
                    index = self.widget.current_image_index
                    thread = QThread()
                    self.widget.threads.append(thread)
                    process = ProcessImageUpload(element, self.widget, path, session, index)
                    self.widget.workers.append(process)
                    self.widget.workers[index].moveToThread(self.widget.threads[index])
                    self.widget.threads[index].started.connect(self.widget.workers[index].process)
                    self.widget.current_image_index = self.widget.current_image_index + 1
            self.widget.threads[0].start()
        except ValueError:
            traceback.print_exc()

    def update_status_bar(self):
        """ update_status_bar """
        if not self.widget.update_uploading_status():
            self.check_thread_timer.stop()
