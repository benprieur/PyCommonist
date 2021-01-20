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
            widget.statusBar.showMessage("          Login is not filled.",)
            return

        if len(self.password) == 0:
            widget.statusBar.showMessage("          Password is not filled.")
            return

        if len(widget._currentUpload) == 0:
            widget.statusBar.showMessage("          No image is selected.")
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
            widget.statusBar.showMessage("          Client login failed.")
            return

        self.numberImages = len(widget._currentUpload)
        print(str(QThread.currentThreadId().__int__()))

        self.numberImagesChecked = 0
        for element in widget._currentUpload:
            if element.cbImport.isChecked():
                self.numberImagesChecked = self.numberImagesChecked + 1

        widget.threads = []
        widget.workers = []

        currentImageIndex = 0
        for element in widget._currentUpload:
            if element.cbImport.isChecked():
                path = widget.currentDirectoryPath
                session = self.S

                thread = QThread()
                widget.threads.append(thread)
                process = ProcessImageUpload(element, widget, path, session)
                widget.workers.append(process)
                widget.workers[currentImageIndex].moveToThread(widget.threads[currentImageIndex])
                widget.threads[currentImageIndex].finished.connect(lambda widget=widget, ii=currentImageIndex: self.terminateThread(widget, currentImageIndex))
                widget.threads[currentImageIndex].started.connect(widget.workers[currentImageIndex].process)
                widget.threads[currentImageIndex].start()
                currentImageIndex = currentImageIndex + 1


    '''
        terminateThread
    '''
    @pyqtSlot()
    def terminateThread(self, widget, ii):
        print("Current upload thread deleting.")
        widget.threads[ii].stop()
        widget.threads[ii].deletelater()