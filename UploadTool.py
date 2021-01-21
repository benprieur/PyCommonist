import json, requests
from constants import URL
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from ProcessImageUpload import ProcessImageUpload

class UploadTool:

    '''
        uploadImages
         https://www.mediawiki.org/wiki/API:Upload
    '''
    def uploadImages(self, widget):

        self.login = widget.lineEditUserName.text()
        self.password = widget.lineEditPassword.text()

        if len(self.login) == 0:
            widget.statusBar.showMessage("          Login is not filled",)
            return

        if len(self.password) == 0:
            widget.statusBar.showMessage("          Password is not filled")
            return

        if len(widget._currentUpload) == 0:
            widget.statusBar.showMessage("          No image is selected")
            return

        self.S = requests.Session()

        # Step 1: Retrieve a login token
        PARAMS_1 = {
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json"
        }
        R = self.S.get(url=URL, params=PARAMS_1)
        DATA = R.json()
        print(DATA)

        LOGIN_TOKEN = DATA["query"]["tokens"]["logintoken"]
        print(LOGIN_TOKEN)

        # Step 2: Send a post request to login
        PARAMS_2 = {
            'action': "clientlogin",
            'username': self.login,
            'password': self.password,
            'loginreturnurl': URL,
            'logintoken': LOGIN_TOKEN,
            'format': "json"
        }

        R = self.S.post(URL, data=PARAMS_2)
        print(R.content)
        print(R.json()['clientlogin']['status'])
        if R.json()['clientlogin']['status'] != 'PASS':
            widget.statusBar.showMessage("          Client login failed")
            return

        self.numberImages = len(widget._currentUpload)
        print(str(QThread.currentThreadId().__int__()))

        widget.numberImagesChecked = 0
        for element in widget._currentUpload:
            if element.cbImport.isChecked():
                widget.numberImagesChecked = widget.numberImagesChecked + 1

        for thread in widget.threads:
            thread.wait()
            thread.quit()
        widget.threads.clear()
        widget.workers.clear()

        widget.currentImageIndex = 0
        for element in widget._currentUpload:
            if element.cbImport.isChecked():
                path = widget.currentDirectoryPath
                session = self.S
                index = widget.currentImageIndex

                thread = QThread()
                widget.threads.append(thread)
                process = ProcessImageUpload(element, widget, path, session, index)
                widget.workers.append(process)
                widget.workers[index].moveToThread(widget.threads[index])
                widget.threads[index].started.connect(widget.workers[index].process)
                widget.currentImageIndex = widget.currentImageIndex + 1

        widget.threads[0].start()