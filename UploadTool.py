import json, requests, traceback, time
from constants import URL
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, QTimer
from ProcessImageUpload import ProcessImageUpload

class UploadTool:

    S = None
    widget = None
    checkThreadTimer = None

    '''
        uploadImages
         https://www.mediawiki.org/wiki/API:Upload
    '''
    def uploadImages(self, w):
        try:
            self.widget = w
            self.widget.statusBar.setText("")
            self.login = self.widget.lineEditUserName.text()
            self.password = self.widget.lineEditPassword.text()

            if len(self.login) == 0:
                self.widget.statusBar.setText("Login is not filled",)
                return

            if len(self.password) == 0:
                self.widget.statusBar.setText("Password is not filled")
                return

            if len(self.widget._currentUpload) == 0:
                self.widget.statusBar.setText("No image is selected")
                return

            #print(self.S)
            #
            self.S = requests.Session()
            print(self.S)

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
                self.widget.statusBar.setText("Client login failed")
                return

            self.numberImages = len(self.widget._currentUpload)

            self.widget.numberImagesChecked = 0
            for element in self.widget._currentUpload:
                if element.cbImport.isChecked():
                    self.widget.numberImagesChecked = self.widget.numberImagesChecked + 1

            self.widget.alreadyUploaded = 0

            print('''Cleaning previous threads''')
            for thread in self.widget.threads:
                thread.wait()
                thread.quit()
            self.widget.threads.clear()
            self.widget.workers.clear()

            if self.checkThreadTimer == None:
                self.checkThreadTimer = QTimer()
            self.checkThreadTimer.stop()
            self.checkThreadTimer.setInterval(500)
            self.checkThreadTimer.timeout.connect(self.updateStatusBar)
            self.checkThreadTimer.start(500)

            self.widget.numberImages = 0
            for element in self.widget._currentUpload:
                if element.cbImport.isChecked():
                    self.widget.numberImages = self.widget.numberImages + 1

            print('''For each image''')
            self.widget.currentImageIndex = 0

            for element in self.widget._currentUpload:
                if element.cbImport.isChecked():
                    path = self.widget.currentDirectoryPath
                    session = self.S
                    index = self.widget.currentImageIndex

                    thread = QThread()
                    self.widget.threads.append(thread)
                    process = ProcessImageUpload(element, self.widget, path, session, index)
                    self.widget.workers.append(process)
                    self.widget.workers[index].moveToThread(self.widget.threads[index])
                    self.widget.threads[index].started.connect(self.widget.workers[index].process)
                    self.widget.currentImageIndex = self.widget.currentImageIndex + 1

            self.widget.threads[0].start()

        except:
            traceback.print_exc()

    '''
        updateStatusBar
    '''
    def updateStatusBar(self):
        print("updateStatusBar")
        if (self.widget.alreadyUploaded >= self.widget.numberImagesChecked):
            self.checkThreadTimer.stop()
        else:
            current = self.widget.statusBar.text()
            self.widget.statusBar.setText(current + ".")