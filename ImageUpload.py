from PyQt5.QtWidgets import QWidget

"""
    class ImageUpload
"""


class ImageUpload(QWidget):

    def __init__(self):
        super(ImageUpload, self).__init__()

    def onPressed(self):

        content = str(self.lineEditCategories.text())
        searchbox = str(self.searchBoxCategory.text())

        if content == "":
            self.lineEditCategories.setText(searchbox)
        else:
            self.lineEditCategories.setText(content + "|" + searchbox)
