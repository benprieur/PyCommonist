''' 
    ImageUpload.py
'''
from PyQt5.QtWidgets import QWidget


''' 
    class ImageUpload
'''


class ImageUpload(QWidget):

    def __init__(self):
        """ __init__ """
        super(ImageUpload, self).__init__()

    def on_pressed(self):
        """ on_pressed """
        content = str(self.line_edit_categories.text())
        searchbox = str(self.searchBoxCategory.text())
        if content == "":
            self.line_edit_categories.setText(searchbox)
        else:
            self.line_edit_categories.setText(content + "|" + searchbox)
