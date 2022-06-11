'''
    ProcessImageUpload.py
'''
import os.path
import traceback
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QTimer
from constants import URL


'''
    class ProcessImageUpload
'''
class ProcessImageUpload(QObject):

    def __init__(self, element, widget, path, session, index):
        """ __init__ """
        QObject.__init__(self)
        self.element = element
        self.widget = widget
        self.path = path
        self.session = session
        self.index = index

    @pyqtSlot()
    def process(self):
        """ process """
        print("process is running")
        print(str(QThread.currentThreadId().__int__()))
        self.widget.clear_status()
        element = self.element
        path = self.path
        widget = self.widget
        text = self.get_text(element, widget)
        file_name = element.line_edit_file_name.text()
        real_file_name = element.lbl_real_file_name.text()
        FILE_PATH = path + '/' + real_file_name
        # Step 3: Obtain a CSRF token
        params_3 = {
            "action": "query",
            "meta":"tokens",
            "format":"json"
        }
        http_ret = self.session.get(url=URL, params=params_3)
        data = http_ret.json()
        print(data)
        CSRF_TOKEN = data["query"]["tokens"]["csrftoken"]
        print(CSRF_TOKEN)
        # Step 4: Post request to upload a file directly
        try:
            print("Bug dot:" + FILE_PATH)
            if os.path.isfile(FILE_PATH):
                file = {'file':(file_name, open(FILE_PATH, 'rb'), 'multipart/form-data')}
            else:
                element.lbl_upload_result.setText("FAILED")
                self.widget.set_upload_status(False)
                return
            # Manage dot in new filename (according physical file name)            
            physical_array = FILE_PATH.split('.')
            if len(physical_array) > 0:
                physical_ext = physical_array[-1]
                logical_array = file_name.split('.')
                if len(logical_array) > 1:
                    logical_ext = logical_array[-1]
                    if logical_ext != physical_ext:
                        file_name = str(file_name) + "." + str(physical_ext)
                else:
                    file_name = str(file_name) + "." + str(physical_ext)
            else:
                element.lbl_upload_result.setText("FAILED")
                self.widget.set_upload_status(False)
                return
            print("ProcessImageUpload.py-76 logical file name to be send: " + file_name)
            params_4 = {
                "action": "upload",
                "filename": file_name,
                "format": "json",
                "token": CSRF_TOKEN,
                "ignorewarnings": 1,
                "comment": "PyCommonist upload: " + file_name,
                "text": text
            }
            http_ret = self.session.post(URL, files=file, data=params_4)
            print(http_ret)
            print(http_ret.json())
            if 'upload' in http_ret.json():
                result_upload_image = http_ret.json()['upload']['result']
            else:
                result_upload_image = ""
                element.cb_import.setChecked(False)
                self.widget.set_upload_status(False)
                element.lbl_upload_result.setText("Failed")
                return
            element.lbl_upload_result.setText(result_upload_image)
            self.widget.set_upload_status(True)
            element.cb_import.setChecked(False)
        except ValueError:
            traceback.print_exc()
            element.lbl_upload_result.setText("FAILED")
            self.widget.set_upload_status(False)
        self.run_next_thread()

    def run_next_thread(self):
        """ run_next_thread """
        if self.index < self.widget.number_images_checked - 1:
            print("Start next process")
            timer = QTimer()
            timer.setInterval(6) # To avoid a 502 error (first test ok with 10)
            timer.start()
            self.widget.threads[self.index + 1].start()
        elif self.index == self.widget.number_images_checked - 1:
            print("Call Clean threads")
            self.widget.clean_threads()

    def get_text(self, element, widget):
        """ get_text """
        location = element.lineEditLocation.text()
        if location != '':
            location = location.replace(",", "|")
            location = '{{Location dec|''' + location + '''}}\n'''
        print(widget.line_edit_categories.text())
        print(element.line_edit_categories.text())
        cat_text = widget.line_edit_categories.text() + '|' + element.line_edit_categories.text()
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
            if category:
                catFinalText = catFinalText + "[[Category:" + category + "]]\n"
        description = widget.line_edit_description.toPlainText()  + element.line_edit_description.toPlainText()
        language = widget.line_edit_language.text()
        if language:
            description = "{{" + language + "|1=" + description + "}}"
        text = \
"""== {{int:filedesc}} ==
{{Information
|Description = """ + description + "\n" + \
"""|Source = """ + widget.line_edit_source.text() + "\n" + \
"""|Author = """ + widget.line_edit_author.text() + "\n" \
"""|Date = """ + element.line_edit_date_time.text() + "\n" + \
"""|Permission =
|other versions =
}}\n""" + location + "\n" + \
"""== {{int:license-header}} == \n""" + widget.line_edit_license.text() + "\n\n" + catFinalText
        return text


