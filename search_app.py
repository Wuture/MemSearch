from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QPushButton, QGridLayout, QLineEdit, QHBoxLayout, QVBoxLayout, QScrollArea, QSizePolicy, QSpacerItem
from PyQt5.QtCore import Qt
import sys
from PIL import Image
import io
from PyQt5.QtGui import QImage, QPixmap, QIcon

from search import search_keyword

class ImageGalleryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search your OS memory")
        self.initUI()

    def initUI(self):
        self.central_widget = QWidget()  # Central widget that holds everything
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)  # Main layout for central_widget

        # Search bar and button setup
        self.search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Enter search keyword...")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.perform_search)
        self.search_layout.addWidget(self.search_bar)
        self.search_layout.addWidget(self.search_button)
        self.main_layout.addLayout(self.search_layout)  # Add search bar at the top

        # Scroll area setup for gallery
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.gallery_widget = QWidget()  # This widget will hold the grid of images
        self.gallery_layout = QGridLayout(self.gallery_widget)
        self.scroll_area.setWidget(self.gallery_widget)
        self.main_layout.addWidget(self.scroll_area)  # Add scroll area below the search bar

        self.resize(1500, 1000)
        self.centerWindow()

    # def update_gallery(self, image_objects):
    #     # print (len(image_objects))
    #     # if image_objects is empty, show a message

    #     # Clear existing widgets in gallery layout
    #     for i in reversed(range(self.gallery_layout.count())): 
    #         widget = self.gallery_layout.itemAt(i).widget()
    #         if widget is not None:
    #             widget.deleteLater()

    #     if not image_objects:
    #         no_images_widget = QWidget()
    #         no_images_layout = QVBoxLayout(no_images_widget)
            
    #         label = QLabel("No images found for the search keyword.")
    #         label.setAlignment(Qt.AlignCenter)
            
    #         no_images_layout.addWidget(label)
    #         no_images_layout.setAlignment(Qt.AlignCenter)
            
    #         self.gallery_layout.addWidget(no_images_widget, 0, 0, self.gallery_layout.rowCount(), self.gallery_layout.columnCount())
    #         return
        
    #     num_columns = 4  # Adjust this value to change the number of columns in the grid
    #     for index, image_object in enumerate(image_objects):
    #         # The fourth element in the image_object tuple is the PIL Image object
    #         img = image_object[3]
    #         # First element is the software name, second is the date, third is the time
    #         software_name = image_object[0]
    #         date = image_object[1]
    #         time = image_object[2]
    #         # Get the original dimensions
    #         original_width, original_height = img.size

    #         # Calculate the new dimensions, which are 8% of the original (fixed typo from 0.08 to 0.8)
    #         new_width = int(original_width * 0.1)
    #         new_height = int(original_height * 0.1)
            
    #         thumbnail_size = (new_width, new_height)  # Using LANCZOS filter for high-quality downsampling
    #         original_img = img.copy()
    #         img.thumbnail(thumbnail_size, Image.LANCZOS)
    #         byte_array = io.BytesIO()
    #         img.save(byte_array, format='PNG')
    #         byte_array.seek(0)
    #         qt_img = QPixmap()
    #         qt_img.loadFromData(byte_array.getvalue())
            
    #         btn = QPushButton()
    #         btn.setFixedSize(*thumbnail_size)
    #         btn.setIcon(QIcon(qt_img))
    #         btn.setIconSize(qt_img.size())
    #         # Correctly bind the lambda function to use the current image in the loop
    #         btn.clicked.connect(lambda ch, img=original_img.copy(): self.show_image(img))
    #         self.gallery_layout.addWidget(btn, index // num_columns, index % num_columns)

    #         # Create a label for the software name and date-time
    #         text_label = QLabel(f"{software_name}\n{date} {time}")
    #         text_label.setAlignment(Qt.AlignCenter)
            
    #         # Add the text label to the image layout
    #         self.gallery_layout.addWidget(text_label)
        
    #     # Update the layout and adjust the size of the gallery widget
    #     self.gallery_layout.update()
    #     self.gallery_widget.adjustSize()

    def update_gallery(self, image_objects):
        # print (len(image_objects))
        # if image_objects is empty, show a message

        # Clear existing widgets in gallery layout
        for i in reversed(range(self.gallery_layout.count())): 
            widget = self.gallery_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        if not image_objects:
            no_images_widget = QWidget()
            no_images_layout = QVBoxLayout(no_images_widget)
            
            label = QLabel("No images found for the search keyword.")
            label.setAlignment(Qt.AlignCenter)
            
            no_images_layout.addWidget(label)
            no_images_layout.setAlignment(Qt.AlignCenter)
            
            self.gallery_layout.addWidget(no_images_widget, 0, 0, self.gallery_layout.rowCount(), self.gallery_layout.columnCount())
            return
        
        num_columns = 4  # Adjust this value to change the number of columns in the grid
        for index, image_object in enumerate(image_objects):
             # Process the image object
            img = image_object[3]
            software_name = image_object[0]
            date = image_object[1]
            time = image_object[2]

            # Create a QWidget to hold the image and label
            image_widget = QWidget()
            image_layout = QVBoxLayout(image_widget)
            image_layout.setContentsMargins(5, 0, 5, 5)  # Margin around the QWidget
            image_layout.setSpacing(10)

             # Get the original dimensions
            original_width, original_height = img.size

            # Calculate the new dimensions, which are 8% of the original (fixed typo from 0.08 to 0.8)
            new_width = int(original_width * 0.1)
            new_height = int(original_height * 0.1)
            
            thumbnail_size = (new_width, new_height)  # Using LANCZOS filter for high-quality downsampling
            original_img = img.copy()
            # print (original_img)
            img.thumbnail(thumbnail_size, Image.LANCZOS)
            byte_array = io.BytesIO()
            img.save(byte_array, format='PNG')
            byte_array.seek(0)
            qt_img = QPixmap()
            qt_img.loadFromData(byte_array.getvalue())

            # Create and configure the QPushButton for the image
            btn = QPushButton()
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Ensure the button does not expand
            btn.setFixedSize(*thumbnail_size)
            btn.setIcon(QIcon(qt_img))
            btn.setIconSize(qt_img.size())
            btn.clicked.connect(lambda ch, img=original_img: self.show_image(img))

            # Add the button to the QVBoxLayout within the image_widget
            image_layout.addWidget(btn, alignment=Qt.AlignCenter)

            # Create and configure the QLabel for the software name and date-time
            text_label = QLabel(f"{software_name}\n{date.strftime('%Y-%m-%d')} {time.strftime('%H:%M:%S')}")
            text_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Ensure the label does not expand
            text_label.setAlignment(Qt.AlignCenter)

            # Add the text label to the QVBoxLayout within the image_widget
            image_layout.addWidget(text_label, alignment=Qt.AlignCenter)

            # Create a spacer item with zero height and add it to the bottom of the QVBoxLayout to push the contents up
            spacer_item = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
            image_layout.addSpacerItem(spacer_item)


            # Add the image_widget to the main gallery layout
            self.gallery_layout.addWidget(image_widget, index // num_columns, index % num_columns)


    def perform_search(self):
        keyword = self.search_bar.text()
        image_objects = search_keyword(keyword)
        self.update_gallery(image_objects)

    def show_image(self, img):
            # Get the original dimensions
            original_width, original_height = img.size

            # Calculate the new dimensions, which are 80% of the original
            new_width = int(original_width * 0.40)
            new_height = int(original_height * 0.40)

            # Resize the image
            img = img.resize((new_width, new_height), Image.LANCZOS)  # Using LANCZOS filter for high-quality downsampling

            # Convert PIL Image to QImage
            img_byte_array = io.BytesIO()
            img.save(img_byte_array, format='JPEG')
            qimg = QImage()
            qimg.loadFromData(img_byte_array.getvalue())

            # Convert QImage to QPixmap
            pixmap = QPixmap.fromImage(qimg)

            # Create a new window to display the image
            image_window = QMainWindow(self)
            image_window.setWindowTitle("Image Viewer")
            img_label = QLabel()
            img_label.setPixmap(pixmap)
            img_label.setAlignment(Qt.AlignCenter)
            image_window.setCentralWidget(img_label)
            image_window.resize(pixmap.size())
            
            # Center the image window on the screen
            screen = QApplication.primaryScreen().geometry()
            screen_width = screen.width()
            screen_height = screen.height()

            # Calculate the center position
            center_x = (screen_width - self.width()) // 2
            center_y = (screen_height - self.height()) // 2

            image_window.move(center_x, center_y)
            image_window.show()

    def centerWindow(self):
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ImageGalleryApp()
    ex.show()
    sys.exit(app.exec_())