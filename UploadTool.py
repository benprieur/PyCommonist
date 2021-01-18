import json, requests
from constants import URL

class UploadTool:
    def __init__(self, login, password):
        self.login = login
        self.password = password

    '''
        uploadImages
         https://www.mediawiki.org/wiki/API:Upload
    '''
    def uploadImages(self, widget):

        if len(widget._currentUpload) > 0:

            self.S = requests.Session()

        # Step 1: Retrieve a login token
        PARAMS_1 = {
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json"
        }
        print("Step 1")
        R = self.S.get(url=URL, params=PARAMS_1)
        DATA = R.json()

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

        for element in widget._currentUpload:
            if element.cbImport.isChecked():
                text = self.getText(element, widget)
                self.uploadImage(element, widget.currentDirectoryPath, text)

    '''
        uploadImage
             https://www.mediawiki.org/wiki/API:Upload
    '''
    def uploadImage(self, element, path, text):

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
            "comment": "PyCommonist image upload",
            "text": text

        }

        FILE = {'file':(fileName, open(FILE_PATH, 'rb'), 'multipart/form-data')}

        R = self.S.post(URL, files=FILE, data=PARAMS_4)
        DATA = R.json()
        print(DATA)

    '''
        getText
    '''
    def getText(self, element, widget):

        editLocation = element.lineEditLocation.text().replace(" ", "")
        location = editLocation.split(",")

        catFinalText = ''
        cat_text = widget.lineEditCategories.text() + '|' + element.lineEditCategories.text()
        cat_text = cat_text.replace("| ", "|")
        cat_text = cat_text.replace(" | ", "|")
        cat_text = cat_text.strip()

        cat_text += "Category:Uploaded with PyCommonist"
        categories = cat_text.split('|')
        for category in categories:
            catFinalText = catFinalText + "[[Category:" + category + "]]\n"

        text =  \
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
'''== {{int:license-header}} == \n''' + \
widget.lineEditLicense.text() + "\n\n" + catFinalText

        return text
