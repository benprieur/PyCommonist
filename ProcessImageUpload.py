import json, requests
from constants import URL
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot

'''
    class ProcessImageUpload
'''
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
            "comment": "PyCommonist image upload: " + fileName,
            "text": text
        }

        FILE = {'file':(fileName, open(FILE_PATH, 'rb'), 'multipart/form-data')}

        R = self.S.post(URL, files=FILE, data=PARAMS_4)
        print(R)
        try:
            resultUploadImage = R.json()['upload']['result']
            print(resultUploadImage)
            element.lblUploadResult.setText(resultUploadImage)
        except:
            print("Something bad from the return value of the upload")
            element.lblUploadResult.setText("FAILED")

        self.runNextThread()

    '''
        terminateThread
    '''
    def runNextThread(self):
        if self.index < self.widget.numberImagesChecked - 1:
            print("Start next process")
            self.widget.threads[self.index + 1].start()
        elif self.index == self.widget.numberImagesChecked - 1:
            print("Clean threads")
            self.widget.cleanThreads()

    '''
        getText
    '''
    def getText(self, element, widget):

        editLocation = element.lineEditLocation.text().replace(" ", "")
        location = editLocation.split(",")

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
'''== {{int:filedesc}} ==
{{Information
|Description = ''' + widget.lineEditDescription.toPlainText()  + element.lineEditDescription.toPlainText()  + "\n" + \
'''|Source = ''' + widget.lineEditSource.text() + "\n" + \
'''|Author = ''' + widget.lineEditAuthor.text() + "\n" \
'''|Date = ''' + element.lineEditDateTime.text() + "\n" + \
'''|Permission =
|other_versions =
}}
{{Location dec|''' + location[0] + '|' + location[1] + '''}}\n''' + \
'''== {{int:license-header}} == \n''' + widget.lineEditLicense.text() + "\n\n" + catFinalText

        return text

