import json, requests, traceback
from constants import URL
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, QTimer

"""
    class ProcessImageUpload
"""


class ProcessImageUpload(QObject):

    def __init__(self, element, widget, path, session, index):
        QObject.__init__(self)
        self.element = element
        self.widget = widget
        self.path = path
        self.S = session
        self.index = index

    @pyqtSlot()
    def process(self):

        print("process is running")
        print(str(QThread.currentThreadId().__int__()))
        self.widget.statusBar.setText("")

        element = self.element
        path = self.path
        widget = self.widget

        text = self.getText(element, widget)

        fileName = element.lineEditFileName.text()
        realFileName = element.lblRealFileName.text()

        FILE_PATH = path + '/' + realFileName

        # Step 3: Obtain a CSRF token
        PARAMS_3 = {
            "action": "query",
            "meta":"tokens",
            "format":"json"
        }

        R = self.S.get(url=URL, params=PARAMS_3)
        DATA = R.json()
        print(DATA)

        CSRF_TOKEN = DATA["query"]["tokens"]["csrftoken"]
        print(CSRF_TOKEN)

        # Step 4: Post request to upload a file directly
        PARAMS_4 = {
            "action": "upload",
            "filename": fileName,
            "format": "json",
            "token": CSRF_TOKEN,
            "ignorewarnings": 1,
            "comment": "PyCommonist upload: " + fileName,
            "text": text
        }

        try:
            # Here test if the file is still there...
            FILE = {'file':(fileName, open(FILE_PATH, 'rb'), 'multipart/form-data')}

            R = self.S.post(URL, files=FILE, data=PARAMS_4)
            print(R)
            resultUploadImage = R.json()['upload']['result']
            print(resultUploadImage)
            element.lblUploadResult.setText(resultUploadImage)
            self.widget.alreadyUploaded = self.widget.alreadyUploaded + 1
            self.widget.statusBar.setText("..." + str(self.widget.alreadyUploaded) + "/" + str(self.widget.numberImagesChecked) + " image(s) are successfully uploaded")
        except:
            traceback.print_exc()
            element.lblUploadResult.setText("FAILED")
            self.widget.alreadyUploaded = self.widget.alreadyUploaded + 1
            self.widget.statusBar.setText("..." + " something bad :(")

        self.runNextThread()


    """
        terminateThread
    """
    def runNextThread(self):
        if self.index < self.widget.numberImagesChecked - 1:
            print("Start next process")
            timer = QTimer()
            timer.setInterval(6); # To avoid a 502 error (first test ok with 10)
            timer.start()
            self.widget.threads[self.index + 1].start()
        elif self.index == self.widget.numberImagesChecked - 1:
            print("Call Clean threads")
            self.widget.cleanThreads()

    """
        getText
    """
    def getText(self, element, widget):

        location = element.lineEditLocation.text()
        if location != '':
            # replace comma with pipe when copying address from OSM
            location = location.replace(",", "|")
            location = '{{Location dec|''' + location + '''}}\n'''

        print(widget.lineEditCategories.text())
        print(element.lineEditCategories.text())
        cat_text = widget.lineEditCategories.text() + '|' + element.lineEditCategories.text()
        cat_text = cat_text.replace("| ", "|")
        cat_text = cat_text.replace(" | ", "|")
        cat_text = cat_text.strip()
        if cat_text == "|":
            cat_text = "Uploaded with PyCommonist"
        else:
            cat_text += "|Uploaded with PyCommonist"
        cat_text = cat_text.replace("||", "|")
        print (cat_text)

        categories = cat_text.split('|')

        catFinalText = ''
        for category in categories:
            catFinalText = catFinalText + "[[Category:" + category + "]]\n"

        text = \
"""== {{int:filedesc}} ==
{{Information
|Description = """ + widget.lineEditDescription.toPlainText()  + element.lineEditDescription.toPlainText()  + "\n" + \
"""|Source = """ + widget.lineEditSource.text() + "\n" + \
"""|Author = """ + widget.lineEditAuthor.text() + "\n" \
"""|Date = """ + element.lineEditDateTime.text() + "\n" + \
"""|Permission =
|other_versions =
}}\n""" + location + "\n" + \
"""== {{int:license-header}} == \n""" + widget.lineEditLicense.text() + "\n\n" + catFinalText

        return text

