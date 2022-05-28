'''
    PyCommonist.py
'''
import os
import traceback
from os.path import isfile, join
import re
from PyQt5.QtCore import Qt
from PyQt5.Qt import QDir
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QHBoxLayout, \
    QFrame, \
    QSplitter, \
    QFormLayout, \
    QLabel, \
    QLineEdit, \
    QPlainTextEdit, \
    QVBoxLayout, \
    QFileSystemModel, \
    QTreeView, \
    QScrollArea, \
    QWidget, \
    QCheckBox, \
    QPushButton, \
    QMenu, \
    QMessageBox
from UploadTool import UploadTool
from completer import SearchBox
import exifread
from gps_location import get_exif_location
from ImageUpload import ImageUpload
from config import LeftFrameConfig
from config import RightFrameConfig
from EXIFImage import EXIFImage

from constants import VERTICAL_TOP_SIZE, \
    VERTICAL_BOTTOM_SIZE, \
    HORIZONTAL_LEFT_SIZE, \
    HORIZONTAL_RIGHT_SIZE, \
    WIDTH_WIDGET, \
    WIDTH_WIDGET_RIGHT, \
    IMAGE_DIMENSION, \
    STYLE_IMPORT_BUTTON, \
    STYLE_IMPORT_STATUS, \
    STYLE_STATUSBAR, \
    IMPORT_BUTTON_NO_IMAGE, \
    IMPORT_BUTTON_N_IMAGES, \
    PYCOMMONIST_VERSION


'''
    Main class of software
'''
class PyCommonist(QWidget):

    tool = None

    def __init__(self):
        super(PyCommonist, self).__init__()
        self.init_ui()
        self.threads = []
        self.workers = []

        # copied image information
        self.copied_name = ''
        self.copied_description = ''
        self.copied_categories = ''

        # upload status
        self.init_upload(0)


    '''
        def init_ui
    '''
    def init_ui(self):
        self.current_directory_path = ''
        self.image_sort_order = RightFrameConfig.default_image_sort

        self.generate_splitter()
        self.generate_left_top_frame()
        self.generate_left_bottom_frame()

        self.showMaximized()
        self.setWindowTitle('PyCommonist version ' + PYCOMMONIST_VERSION + ' - Wikimedia Commons')

        self.show()

    '''
        def on_select_folder
    '''
    def on_select_folder(self, selected):

        try:
            current_index = selected.indexes()[0]
            self.current_directory_path = self.model_tree.filePath(current_index)
            print(self.current_directory_path)
        except:
            print("Something bad happened inside on_select_folder function")
            traceback.print_exc()

        self.load_media_from_current_folder()

    '''
        def load_media_from_current_folder
    '''
    def load_media_from_current_folder(self):

        try:
            self.clear_status()
            self.exif_image_collection = []

            list_dir = os.listdir(self.current_directory_path)
            files = [f for f in sorted(list_dir) if isfile(join(self.current_directory_path, f))]
            for file in files:
                full_file_path = os.path.join(self.current_directory_path, file)
                if full_file_path.upper().endswith(".JPEG") or \
                   full_file_path.upper().endswith(".JPG") or \
                   full_file_path.upper().endswith(".SVG") or \
                   full_file_path.upper().endswith(".PNG"):

                    current_exif_image = EXIFImage()
                    current_exif_image.full_file_path = full_file_path
                    current_exif_image.filename = file
                    tags = None

                    try:
                        f_exif = open(full_file_path, 'rb')
                        tags = exifread.process_file(f_exif)
                    except ValueError:
                        print("A problem with EXIF data reading: ")
                    '''
                        'GPS GPSLatitude', 'GPS GPSLongitude'] # [45, 49, 339/25] [4, 55, 716/25]
                        'GPS GPSImgDirection' 'GPS GPSLatitudeRef'
                    '''
                    try:
                        current_exif_image.lat, current_exif_image.long, current_exif_image.heading = get_exif_location(tags)
                    except ValueError:
                        print("A problem with EXIF data reading")
                    dt_timestamp = None
                    try:
                        dt_timestamp = tags['EXIF DateTimeOriginal'] # 2021:01:13 14:48:44
                    except ValueError:
                        print("A problem with EXIF data reading")
                    print (dt_timestamp)
                    dt_timestamp = str(dt_timestamp)
                    index_space = dt_timestamp.find(" ")
                    current_exif_image.date = dt_timestamp[0:index_space].replace(":", "-")
                    current_exif_image.time = dt_timestamp[index_space+1:]

                    self.exif_image_collection.append(current_exif_image)
                    print(current_exif_image)
            self.generate_right_frame()
        except:
            print("Something bad happened inside loadMediaFromCurrentFolder function")
            traceback.print_exc()

    '''
        def btn_toggle_image_sort_order
    '''
    def btn_toggle_image_sort_order(self):
        if hasattr(self, 'current_upload') is False:
            return
        if len(self.current_upload) > 0:
            if self.image_sort_order == "file_name":
                self.image_sort_order = "exif_date"
            else:
                self.image_sort_order = "file_name"
            self.generate_right_frame()

    '''
        def btn_toggle_image_sort_order
    '''
    def btn_select_no_image(self):
        if hasattr(self, 'current_upload') is False:
            return
        if len(self.current_upload) > 0:
            for element in self.current_upload:
                element.cb_import.setCheckState(False)

    '''
        def btn_toggle_image_sort_order
    '''
    def btn_select_all_images(self):
        if hasattr(self, 'current_upload') is False:
            return
        if len(self.current_upload) > 0:
            for element in self.current_upload:
                element.cb_import.setCheckState(True)

    '''
        def on_toggle_import
    '''
    def on_toggle_import(self):
        selected_imports = 0 # count selected imports
        for element in self.current_upload:
            if element.cb_import.isChecked():
                selected_imports = selected_imports + 1
        if selected_imports == 0: # update selected import counter
            self.btn_import.setText(IMPORT_BUTTON_NO_IMAGE)
        else:
            self.btn_import.setText(IMPORT_BUTTON_N_IMAGES.format(selected_imports))

    '''
        def on_click_import
    '''
    def on_click_import(self):
        try:
            self.btn_import.setEnabled(False)
            if hasattr(self, 'current_upload') is False:
                self.btn_import.setEnabled(True)
                return
            if len(self.current_upload) == 0:
                self.btn_import.setEnabled(True)
                return
            empty_descriptions = 0 # verify all fields are set
            empty_categories = 0
            for element in self.current_upload:
                if not element.cb_import.isChecked():
                    continue
                desc = self.line_edit_description.toPlainText() + element.line_edit_description.toPlainText()
                if not (desc and desc.strip()):
                    empty_descriptions = empty_descriptions + 1
                categs = self.line_edit_categories.text() + element.line_edit_categories.text()
                if not (categs and categs.strip()):
                    empty_categories = empty_categories + 1
            if empty_descriptions > 0:
                confirmation = QMessageBox.question(self, 'Incomplete Descriptions', 'There are %s image(s) without description, continue upload?' % empty_descriptions, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if confirmation == QMessageBox.No:
                    return
            if empty_categories > 0:
                confirmation = QMessageBox.question(self, 'Incomplete Categories', 'There are %s image(s) without category, continue upload?' % empty_categories, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if confirmation == QMessageBox.No:
                    return
            if self.tool is None:
                self.tool = UploadTool()
            self.tool.upload_images(self)
        except ValueError:
            self.btn_import.setEnabled(True)
            traceback.print_exc()

    '''
        def clean_threads
    '''
    def clean_threads(self):
        try:
            print("Clean threads properly")

            for thread in self.threads:
                print("Current thread proper deletion")
                thread.quit()
                thread.wait()
        except ValueError:
            print("A problem with clean_threads")

    '''
        def generate_splitter
    '''
    def generate_splitter(self):

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        self.left_top_frame = QFrame()
        self.left_top_frame.setFrameShape(QFrame.StyledPanel)
        self.right_widget = QWidget()
        self.right_widget.resize(300, 300)
        self.layout_right = QVBoxLayout()
        self.right_widget.setLayout(self.layout_right)
        self.generate_right_frame_buttons()
        self.scroll = QScrollArea()
        self.layout_right.addWidget(self.scroll)
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget(self.scroll)
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_content.setLayout(self.scroll_layout)
        self.scroll.setWidget(self.scroll_content)
        self.splitter_left = QSplitter(Qt.Vertical)
        self.left_botton_frame = QFrame()
        self.left_botton_frame.setFrameShape(QFrame.StyledPanel)
        self.splitter_left.addWidget(self.left_top_frame)
        self.splitter_left.addWidget(self.left_botton_frame)
        self.splitter_left.setSizes([VERTICAL_TOP_SIZE,VERTICAL_BOTTOM_SIZE])
        self.splitter_central = QSplitter(Qt.Horizontal)
        self.splitter_central.addWidget(self.splitter_left)
        self.splitter_central.addWidget(self.right_widget)
        self.splitter_central.setSizes([HORIZONTAL_LEFT_SIZE,HORIZONTAL_RIGHT_SIZE])
        hbox.addWidget(self.splitter_central)
        vbox.addLayout(hbox)
        self.status_bar = QLabel()
        self.status_bar.setStyleSheet(STYLE_STATUSBAR)
        vbox.addWidget(self.status_bar)
        self.setLayout(vbox)

    '''
        def generate_left_top_frame
    '''
    def generate_left_top_frame(self):
        self.layout_left_top = QFormLayout()
        self.layout_left_top.setFormAlignment(Qt.AlignTop)
        self.lbl_user_name = QLabel("Username: ")
        self.lbl_user_name.setAlignment(Qt.AlignLeft)
        self.line_edit_user_name = QLineEdit()
        self.line_edit_user_name.setText(LeftFrameConfig.username)
        self.line_edit_user_name.setFixedWidth(WIDTH_WIDGET)
        self.line_edit_user_name.setAlignment(Qt.AlignLeft)
        self.layout_left_top.addRow(self.lbl_user_name, self.line_edit_user_name)
        self.lbl_password = QLabel("Password: ")
        self.lbl_password.setAlignment(Qt.AlignLeft)
        self.line_edit_password = QLineEdit()
        self.line_edit_password.setFixedWidth(WIDTH_WIDGET)
        self.line_edit_password.setAlignment(Qt.AlignLeft)
        self.line_edit_password.setEchoMode(QLineEdit.Password)
        self.layout_left_top.addRow(self.lbl_password, self.line_edit_password)
        self.lbl_source = QLabel("Source: ")
        self.lbl_source.setAlignment(Qt.AlignLeft)
        self.line_edit_source = QLineEdit()
        self.line_edit_source.setFixedWidth(WIDTH_WIDGET)
        self.line_edit_source.setText(LeftFrameConfig.source)
        self.line_edit_source.setAlignment(Qt.AlignLeft)
        self.layout_left_top.addRow(self.lbl_source, self.line_edit_source)
        self.lblAuthor = QLabel("Author: ")
        self.lblAuthor.setAlignment(Qt.AlignLeft)
        self.line_edit_author = QLineEdit()
        self.line_edit_author.setFixedWidth(WIDTH_WIDGET)
        self.line_edit_author.setText(LeftFrameConfig.author)
        self.line_edit_author.setAlignment(Qt.AlignLeft)
        self.layout_left_top.addRow(self.lblAuthor, self.line_edit_author)
        self.lbl_categories = QLabel("Categories: ")
        self.lbl_categories.setAlignment(Qt.AlignLeft)
        self.line_edit_categories = QLineEdit()
        self.line_edit_categories.setText(LeftFrameConfig.categories)
        self.line_edit_categories.setFixedWidth(WIDTH_WIDGET)
        self.line_edit_categories.setAlignment(Qt.AlignLeft)
        self.layout_left_top.addRow(self.lbl_categories, self.line_edit_categories)
        self.lbl_license = QLabel("License: ")
        self.lbl_license.setAlignment(Qt.AlignLeft)
        self.line_edit_license = QLineEdit()
        self.line_edit_license.setFixedWidth(WIDTH_WIDGET)
        self.line_edit_license.setText(LeftFrameConfig.license)
        self.line_edit_license.setAlignment(Qt.AlignLeft)
        self.layout_left_top.addRow(self.lbl_license, self.line_edit_license)
        self.lbl_language = QLabel("Language code: ")
        self.lbl_language.setAlignment(Qt.AlignLeft)
        self.line_edit_language = QLineEdit()
        self.line_edit_language.setFixedWidth(WIDTH_WIDGET)
        self.line_edit_language.setText(LeftFrameConfig.language)
        self.line_edit_language.setAlignment(Qt.AlignLeft)
        self.layout_left_top.addRow(self.lbl_language, self.line_edit_language)
        self.lbl_description = QLabel("Description: ")
        self.lbl_description.setAlignment(Qt.AlignLeft)
        self.line_edit_description = QPlainTextEdit()
        self.line_edit_description.setFixedWidth(WIDTH_WIDGET)
        self.layout_left_top.addRow(self.lbl_description, self.line_edit_description)
        separation_left_top_frame = QLabel()
        self.layout_left_top.addWidget(separation_left_top_frame)
        import_widget = QWidget()
        import_layout = QHBoxLayout()
        import_widget.setLayout(import_layout)
        self.btn_import = QPushButton(IMPORT_BUTTON_NO_IMAGE)
        self.btn_import.clicked.connect(self.on_click_import)
        import_layout.addWidget(self.btn_import)
        self.layout_left_top.addWidget(import_widget)
        import_widget.setStyleSheet("border:1px solid #808080;")
        self.btn_import.setStyleSheet(STYLE_IMPORT_BUTTON)
        self.left_top_frame.setLayout(self.layout_left_top)

    '''
        def generate_left_bottom_frame
    '''
    def generate_left_bottom_frame(self):
        self.layout_left_bottom = QVBoxLayout()
        self.model_tree = QFileSystemModel()
        self.model_tree.setRootPath(QDir.currentPath())
        self.model_tree.setFilter(QDir.Dirs) # Only directories
        self.tree_left_bottom = QTreeView()
        self.tree_left_bottom.setModel(self.model_tree)
        self.tree_left_bottom.setAnimated(False)
        self.tree_left_bottom.setIndentation(10)
        self.tree_left_bottom.setColumnWidth(0, 300)
        self.tree_left_bottom.expandAll()
        self.tree_left_bottom.selectionModel().selectionChanged.connect(self.on_select_folder)
        self.layout_left_bottom.addWidget(self.tree_left_bottom)
        self.left_botton_frame.setLayout(self.layout_left_bottom)

    '''
        def generate_right_frame_buttons
    '''
    def generate_right_frame_buttons(self):
        import_command_widget = QWidget()
        import_command_layout = QHBoxLayout()
        import_command_widget.setLayout(import_command_layout)
        self.btn_toggle_image_sort = QPushButton("Images sorted by name")
        self.btn_toggle_image_sort.clicked.connect(self.btn_toggle_image_sort_order)
        self.btn_import_check_none = QPushButton("Check None")
        self.btn_import_check_none.clicked.connect(self.btn_select_no_image)
        self.btn_import_check_all = QPushButton("Check All")
        self.btn_import_check_all.clicked.connect(self.btn_select_all_images)
        self.btn_reload_folder = QPushButton("Reload Folder")
        self.btn_reload_folder.clicked.connect(self.load_media_from_current_folder)
        import_command_layout.addWidget(self.btn_toggle_image_sort)
        import_command_layout.addWidget(self.btn_import_check_none)
        import_command_layout.addWidget(self.btn_import_check_all)
        import_command_layout.addWidget(self.btn_reload_folder)
        self.layout_right.addWidget(import_command_widget)

    '''
        def generate_right_frame
    '''
    def generate_right_frame(self):

        self.current_upload = []
        layout = self.scroll_layout
        print(layout)
        print(layout.count())
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        if self.image_sort_order == "exif_date":
            self.exif_image_collection.sort(key=lambda image: image.date + ' ' + image.time)
            self.btn_toggle_image_sort.setText("Images sorted by date")
        else:
            self.exif_image_collection.sort(key=lambda image: image.filename)
            self.btn_toggle_image_sort.setText("Images sorted by name")
        for current_exif_image in self.exif_image_collection:
            local_widget = ImageUpload()
            local_layout = QHBoxLayout()
            local_layout.setAlignment(Qt.AlignRight)
            local_widget.setLayout(local_layout)
            self.scroll_layout.addWidget(local_widget)
            self.current_upload.append(local_widget)
            local_left_widget = QWidget()
            local_left_layout = QFormLayout()
            local_left_layout.setAlignment(Qt.AlignRight)
            local_left_widget.setLayout(local_left_layout)
            local_layout.addWidget(local_left_widget)
            cb_import = QCheckBox("Import")
            cb_import.toggled.connect(self.on_toggle_import)
            lbl_upload_result = QLabel()
            lbl_upload_result.setStyleSheet(STYLE_IMPORT_STATUS)
            btn_copy_paste = QPushButton("Copy/Paste")
            result_layout = QHBoxLayout()
            result_layout.addWidget(lbl_upload_result, 3)
            result_layout.addWidget(btn_copy_paste, 1)
            copy_paste_menu = QMenu()
            copy_action = copy_paste_menu.addAction("Copy")
            paste_action = copy_paste_menu.addAction("Paste name, description and categories")
            paste_with_numbering_action = copy_paste_menu.addAction("Paste name with numbering, description and categories")
            btn_copy_paste.setMenu(copy_paste_menu)
            local_left_layout.addRow(cb_import, result_layout)
            local_widget.cb_import = cb_import
            local_widget.lbl_upload_result = lbl_upload_result
            local_widget.btn_copy_paste = btn_copy_paste
            lbl_file_name = QLabel("Name: ")
            lbl_file_name.setAlignment(Qt.AlignLeft)
            line_edit_file_name = QLineEdit()
            line_edit_file_name.setFixedWidth(WIDTH_WIDGET_RIGHT)
            line_edit_file_name.setText(current_exif_image.filename)
            line_edit_file_name.setAlignment(Qt.AlignLeft)
            line_edit_file_name.textChanged.connect(lambda state, w=cb_import: w.setChecked(True))
            local_left_layout.addRow(lbl_file_name, line_edit_file_name)
            local_widget.line_edit_file_name = line_edit_file_name
            lbl_real_file_name = QLineEdit()
            lbl_real_file_name.setText(current_exif_image.filename)
            local_widget.lbl_real_file_name = lbl_real_file_name
            local_widget.lbl_real_file_name.isVisible = False
            lbl_description = QLabel("Description: ")
            lbl_description.setAlignment(Qt.AlignLeft)
            line_edit_description = QPlainTextEdit()
            line_edit_description.setFixedWidth(WIDTH_WIDGET_RIGHT)
            local_left_layout.addRow(lbl_description, line_edit_description)
            local_widget.line_edit_description = line_edit_description
            lbl_categories = QLabel("Categories: ")
            search_box_category = SearchBox()
            search_box_category.setFixedWidth(WIDTH_WIDGET_RIGHT)
            local_left_layout.addRow(lbl_categories, search_box_category)
            local_widget.searchBoxCategory = search_box_category
            line_edit_categories = QLineEdit()
            line_edit_categories.setFixedWidth(WIDTH_WIDGET_RIGHT)
            local_left_layout.addRow(QLabel(""), line_edit_categories)
            local_widget.line_edit_categories = line_edit_categories
            local_widget.searchBoxCategory.returnPressed.connect(local_widget.on_pressed)
            lbl_location = QLabel("Location: ")
            lbl_location.setAlignment(Qt.AlignLeft)
            line_edit_location = QLineEdit()
            line_edit_location.setFixedWidth(WIDTH_WIDGET_RIGHT)
            if current_exif_image.lat is None or current_exif_image.long is None:
                line_edit_location.setText('')
            else:
                line_edit_location.setText(str(current_exif_image.lat) + '|' + str(current_exif_image.long) + "|heading:" + str(current_exif_image.heading))
            line_edit_location.setAlignment(Qt.AlignLeft)
            local_left_layout.addRow(lbl_location, line_edit_location)
            local_widget.lineEditLocation = line_edit_location
            lbl_date_time = QLabel("Date Time: ")
            lbl_date_time.setAlignment(Qt.AlignLeft)
            line_edit_date_time = QLineEdit()
            line_edit_date_time.setFixedWidth(WIDTH_WIDGET_RIGHT)
            line_edit_date_time.setText(current_exif_image.date + ' ' + current_exif_image.time)
            line_edit_date_time.setAlignment(Qt.AlignLeft)
            local_left_layout.addRow(lbl_date_time, line_edit_date_time)
            local_widget.line_edit_date_time = line_edit_date_time
            copy_action.triggered.connect(lambda state, w=local_widget: self.copy_image_info(w))
            paste_action.triggered.connect(lambda state, w=local_widget: self.pasteImageInfo(w, False))
            paste_with_numbering_action.triggered.connect(lambda state, w=local_widget: self.pasteImageInfo(w, True))
            label = QLabel()
            pixmap = QPixmap(current_exif_image.full_file_path)
            pixmap_resize = pixmap.scaledToWidth(IMAGE_DIMENSION, Qt.FastTransformation)
            label.setPixmap(pixmap_resize)
            local_layout.addWidget(label)
            local_widget.full_file_path = current_exif_image.full_file_path
            self.update()

    '''
        def copy_image_info
    '''
    def copy_image_info(self, image_widget):
        # copy image information
        self.copied_name = image_widget.line_edit_file_name.text()
        self.copied_description = image_widget.line_edit_description.toPlainText()
        self.copied_categories = image_widget.line_edit_categories.text()


    '''
        def generate_right_frame
    '''
    def paste_image_info(self, image_widget, increase_number):
        name = self.copied_name
        if increase_number:
            numberList = re.findall(r'\d+', name)
            if len(numberList) > 0:
                val = numberList[-1]
                nextVal = str(int(val) + 1)
                if len(nextVal) < len(val):
                    nextVal = nextVal.zfill(len(val))
                remove_last_number = name.rsplit(val, 1)
                name = nextVal.join(remove_last_number)
                self.copied_name = name
        image_widget.line_edit_file_name.setText(name)
        image_widget.line_edit_description.setPlainText(self.copied_description)
        image_widget.line_edit_categories.setText(self.copied_categories)

    '''
        def clear_status
    '''
    def clear_status(self):
        self.status_bar.setText("")

    '''
        def set_status
    '''
    def set_status(self, message):
        self.status_bar.setText(message)

    '''
        def init_upload
    '''
    def init_upload(self, count):
        self.number_images_checked = count
        self.upload_successes = 0
        self.upload_failures = 0
        self.upload_status_dots = 0

    '''
        def update_uploading_status
    '''
    def update_uploading_status(self):
        total = self.upload_successes + self.upload_failures
        if total >= self.number_images_checked:
            return False
        self.upload_status_dots = self.upload_status_dots + 1
        if self.upload_status_dots > 10:
            self.upload_status_dots = 0
        message = "{}/{} ".format(total, self.number_images_checked)
        message = message + "." * self.upload_status_dots
        self.set_status(message)
        return True

    '''
        def set_upload_status
    '''
    def set_upload_status(self, success):
        if success:
            self.upload_successes = self.upload_successes + 1
        else:
            self.upload_failures = self.upload_failures + 1
        message = ""
        successes = self.upload_successes
        failures = self.upload_failures
        total = self.number_images_checked
        if successes > 0:
            message = message + " {}/{} image(s) successfully uploaded".format(successes, total)
        if failures > 0:
            if successes > 0:
                message = message + "; "
            message = message + "{} upload(s) failed!".format(failures)
        self.set_status(message)
        self.btn_import.setEnabled(True)

        
