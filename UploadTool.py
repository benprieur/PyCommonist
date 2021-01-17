import json, requests
from constants import URL

class UploadTool:
    def __init__(self, login, password):
        self.login = login
        self.password = password

    '''
    def connect(self):
        try:
            ret = requests.get(URL_TOKEN)
            retToken = json.loads(ret.content)
            #print(retToken)
            self.token = retToken['query']['tokens']['logintoken']
            self.cookies = ret.cookies

            urlLogin = URL_LOGIN + self.login + URL_LOGIN2
            paramsLogin = {'password' : self.password, 'logintoken': self.token}
            ret = requests.post(urlLogin, paramsLogin, cookies=self.cookies)
            print(ret.json())

            return True

        except:
            return False
    '''

    '''
        uploadImages
         https://www.mediawiki.org/wiki/API:Upload
    '''
    def uploadImages(self, widget):

        if len(widget._currentUpload.listImageUpload) > 0:

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
            'username': login,
            'password': password,
            'loginreturnurl': URL,
            'logintoken': LOGIN_TOKEN,
            'format': "json"
        }

        R = self.S.post(URL, data=PARAMS_2)
        print(R.content)

        for element in widget._currentUpload.listImageUpload:
                    if element.cbImport.isChecked():
                        self.uploadImage(element, widget.currentDirectoryPath)

    '''
        uploadImage
             https://www.mediawiki.org/wiki/API:Upload
    '''
    def uploadImage(self, element, path):

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
            "comment": "PyCommonist image upload"
        }

        FILE = {'file':(fileName, open(FILE_PATH, 'rb'), 'multipart/form-data')}

        R = self.S.post(URL, files=FILE, data=PARAMS_4)
        DATA = R.json()
        print(DATA)




























