"""
This tool is used to create a TOP overlay that shows your streaming chat (Twitch, Kick) or anything

on Top of your game so you can't lose what your viewers are Saying

version: 0.0.1
created: 13/04/2024
by: Skander BOUDAWARA

History of changes:
- 13/04/2024: first creation
"""

import json
import sys

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QColor, QIcon, QPainter
from PyQt5.QtWebEngineWidgets import QWebEngineProfile, QWebEngineView
from PyQt5.QtWidgets import (
    QApplication,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizeGrip,
    QSizePolicy,
    QSlider,
    QStyle,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class Overlay(QWidget):
    """
    This method creates a transparent window interface that contains the web engine

    :param id_window: (integer), each window is identified by a unique ID

    :returns: None
    """

    def __init__(self, id_window: int) -> None:
        super().__init__()
        # Variables
        self.id_window: str = str(id_window)  # unique id of the window
        self.offset: int = None  # define offset for moving the window
        self.hovered: bool = False  # if the window is hovered or not
        self.x_pos: int = 100  # position of the window on the x-axis
        self.y_pos: int = 100  # position of the window on the y-axis
        self.url: str = ""  # URL to be used in the web engine
        self.transparent_value: int = 50  # value of transparency of the window

        # load window configurations
        self.load_window_size()

        # setup window interface
        self.window_layout_interface(f"Overlay {self.id_window}")
        


        # create Layout
        layout = QVBoxLayout(self)

        # add quit button on top
        self.quit_button_layout()
        layout.addWidget(self.close_button, alignment=Qt.AlignTop | Qt.AlignRight)

        # add web engine
        self.web_engine_interface()
        layout.addWidget(self.web_view)

        # For resizing
        self.add_window_grip()
        self.updateGripPosition()  # Update grip position initially

    def window_layout_interface(self, title: str) -> None:
        """
        This defines the overall settings of the main window

        :param title: (str), title of the overlay

        :returns: None
        """
        self.setWindowTitle(title)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint
        )  # Set window flags to keep it on top and remove frame
        self.setStyleSheet(
            "font-size: 24px; color: rgba(255, 255, 255, 0); background-color: rgba(255, 255, 255, 0);"
        )
        self.setAttribute(
            Qt.WA_TranslucentBackground, True
        )  # Make background transparent
        self.setGeometry(self.x_pos, self.y_pos, self.width_value, self.height_value)  # Set position and size
        self.setMouseTracking(True)
        self.setContentsMargins(0, 0, 0, 0)

    def web_engine_interface(self) -> None:
        """
        web interface to be created with custom CSS

        :param: None

        :returns: None
        """
        self.web_view = QWebEngineView()
        self.web_view.setUrl(QUrl(self.url))
        self.web_view.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0);"
        )  # Set background color to transparent
        self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Set a more permissive CSP policy
        self.web_view.page().profile().setHttpCacheType(
            QWebEngineProfile.MemoryHttpCache
        )
        self.web_view.page().profile().setPersistentCookiesPolicy(
            QWebEngineProfile.NoPersistentCookies
        )
        self.web_view.page().profile().setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        )
        # self.web_view.page().setUrlRequestInterceptor(lambda details: None)

        self.set_transparent_background(self.web_view)

    def quit_button_layout(self) -> None:
        """
        Quit button to be created

        :param: None

        :returns: None
        """
        self.close_button = QToolButton(self)
        self.close_button.setStyleSheet(
            "QToolButton { background-color: rgba(0, 0, 0, 0); border: none; }"
            "QToolButton:hover { background-color: rgba(255, 0, 0, 128); }"
            "QToolButton:pressed { background-color: rgba(255, 0, 0, 255); }"
            "QToolButton::menu-indicator { image: none; }"
        )
        self.close_button.setIcon(
            self.style().standardIcon(QStyle.SP_TitleBarCloseButton)
        )
        self.close_button.clicked.connect(self.close)
        self.close_button.hide()

    def add_window_grip(self):
        """
        Grip to be used for window resizing

        :param: None

        :returns: None
        """
        # Add QSizeGrip directly to the window for resizing
        self.grip = QSizeGrip(self)
        self.grip.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0);"
        )  # Set background color to transparent
        self.grip.setFixedSize(20, 20)  # Set grip size

    def set_transparent_background(self, web_view: any) -> None:
        """
        add transparency to the web page

        :param: None

        :returns: None
        """
        page = web_view.page()
        page.setBackgroundColor(Qt.transparent)

    def mousePressEvent(self, event: any) -> None:
        """
        Event when button clicked for moving the window

        :param: None

        :returns: None
        """
        if event.buttons() == Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event: any) -> None:
        """
        When moving -> set to follow the Mouse

        :param: None

        :returns: None
        """
        if self.offset is not None:
            self.move(self.mapToGlobal(event.pos() - self.offset))
            self.save_configuration()

    def mouseReleaseEvent(self, event: any) -> None:
        """
        Event when Mouse is released

        :param: None

        :returns: None
        """
        if event.button() == Qt.LeftButton:
            self.offset = None

    def paintEvent(self, event: any) -> None:
        """
        TO create the Painter Layout

        :param: None

        :returns: None
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.hovered:
            painter.setBrush(QColor(0, 0, 0, 128))  # 10% gray transparent (25% of 255)
        else:
            alpha = self.transparent_value * 255 // 100
            painter.setBrush(
                QColor(25, 25, 25, alpha)
            )  # 5% gray transparent (13 out of 255)
        painter.drawRect(self.rect())

    def resizeEvent(self, event: any) -> None:
        """
        To be used in resize event

        :param: None

        :returns: None
        """
        self.layout().update()
        self.updateGripPosition()

    def updateGripPosition(self):
        """
        To update the grip position of the PyQT

        :param: None

        :returns: None
        """
        self.grip.move(
            self.width() - self.grip.width(), self.height() - self.grip.height()
        )
        self.save_configuration()
        

    def enterEvent(self, event):
        """
        When hovering on the window

        :param: None

        :returns: None
        """
        self.close_button.show()  # Show the close button when entering the overlay widget
        self.hovered = True
        self.update()

    def leaveEvent(self, event):
        """
        When leaving the window

        :param: None

        :returns: None
        """
        self.close_button.hide()  # Hide the close button when leaving the overlay widget
        self.hovered = False
        self.update()

    def promptForURL(self):
        """
        If No URL is assigned ask for URL to show

        :param: None

        :returns: None
        """
        url, okPressed = QInputDialog.getText(
            self, "Enter WebView URL", "Insert URL:", QLineEdit.Normal, ""
        )
        if okPressed and url.strip():
            return url.strip()
        else:
            return ""

    def save_configuration(self):
        """
        To save configuration in json file

        :param: None

        :returns: None
        """
        # Save configuration to config.json
        try:
            with open("config.json", "r") as file:
                config_data = json.load(file)
        except FileNotFoundError:
            config_data = {}
        config_data[self.id_window] = {
            "url": self.url,
            "width": self.width(),
            "height": self.height(),
            "transparent": self.transparent_value,
            "x_pos": self.x(),
            "y_pos": self.y(),
        }
        with open("config.json", "w") as file:
            json.dump(config_data, file, indent=4)

    def load_window_size(self):
        # Load window size from config.json
        try:
            with open("config.json", "r") as file:
                config_data = json.load(file)
        except FileNotFoundError:
            self.url = self.promptForURL()
        finally:
            config_data[self.id_window] = {
                "url": config_data[self.id_window].get("url", self.url),
                "width": config_data[self.id_window].get("width", 300),
                "height": config_data[self.id_window].get("height", 100),
                "transparent": config_data[self.id_window].get("transparent", self.transparent_value),
                "x_pos": config_data[self.id_window].get("x_pos", self.x_pos),
                "y_pos": config_data[self.id_window].get("y_pos", self.y_pos),
            }
            self.resize(
                config_data[self.id_window]["width"], config_data[self.id_window]["height"]
            )
            self.url = config_data[self.id_window]["url"]
            self.transparent_value = config_data[self.id_window]["transparent"]
            self.x_pos = config_data[self.id_window]["x_pos"]
            self.y_pos = config_data[self.id_window]["y_pos"]
            self.width_value = config_data[self.id_window]["width"]
            self.height_value = config_data[self.id_window]["height"]
            self.save_configuration()


class MainWindow(QWidget):
    """
    This class is the Main window to be run that has all the necessary configuration
    
    :param: None
    
    :returns: None
    """
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("URL Configuration")
        self.setGeometry(100, 100, 800, 100)
        self.layout = QVBoxLayout()

        self.slider_value_1 = 0
        self.slider_value_2 = 0

        self.window_1_configuration()
        self.window_2_configuration()

        self.load_config()
        # Save configuration
        self.save_button()

        self.setLayout(self.layout)

    def window_1_configuration(self) -> None:
        """
        This method creates the first label, url input and the transparency slider
        
        :param: None
        
        :returns: None
        """
        # Window 1 Config
        self.url_label_1 = QLabel("URL Window 1:")
        self.url_input_1 = QLineEdit()
        self.layout.addWidget(self.url_label_1)
        self.layout.addWidget(self.url_input_1)

        self.transparency_label_1 = QLabel("Transparency Window 1:")
        self.layout.addWidget(self.transparency_label_1)

        self.transparency_slider_1 = QSlider(Qt.Horizontal)
        self.transparency_slider_1.setRange(0, 100)

        self.transparency_slider_1.valueChanged.connect(self.set_transparency_1)
        self.layout.addWidget(self.transparency_slider_1)
    
    def window_2_configuration(self) -> None:
        """
        This method creates the seconds label, url input and the transparency slider
        
        :param: None
        
        :returns: None
        """
        # Window 2 Config
        self.url_label_2 = QLabel("URL Window 2:")
        self.url_input_2 = QLineEdit()
        self.layout.addWidget(self.url_label_2)
        self.layout.addWidget(self.url_input_2)

        self.transparency_label_2 = QLabel("Transparency Window 2:")
        self.layout.addWidget(self.transparency_label_2)

        self.transparency_slider_2 = QSlider(Qt.Horizontal)
        self.transparency_slider_2.setRange(0, 100)

        self.transparency_slider_2.valueChanged.connect(self.set_transparency_2)
        self.layout.addWidget(self.transparency_slider_2)

    def save_button(self) -> None:
        """
        This method creates the save button
        
        :param: None
        
        :returns: None
        """
        self.load_chat_button = QPushButton("Save configuration & Open window(s)")
        self.load_chat_button.clicked.connect(self.open_windows)
        self.layout.addWidget(self.load_chat_button)

    def set_transparency_1(self) -> None:
        """
        This method updates the transparency 1
        
        :param: None
        
        :returns: None
        """
        # Update transparency when slider value changes
        self.transparency_label_1.setText(
            f"Transparency: {self.transparency_slider_1.value()}%"
        )

    def set_transparency_2(self) -> None:
        """
        This method updates the transparency 2
        
        :param: None
        
        :returns: None
        """
        # Update transparency when slider value changes
        self.transparency_label_2.setText(
            f"Transparency: {self.transparency_slider_2.value()}%"
        )

    def load_config(self) -> None:
        """
        This method loads configuration from the json file
        
        :param: None
        
        :returns: None
        """
        config_data = {"0": {}, "1": {}}
        try:
            with open("config.json", "r") as config_file:
                config_data = json.load(config_file)
        except Exception as e:
            print(e)
        
        config_data = {
            "0" : {
                "url": config_data["0"].get("url", ""),
                "transparent": config_data["0"].get("transparent", 50),
                "width": config_data["0"].get("width", 300),
                "height": config_data["0"].get("height", 100),
                "x_pos": config_data["0"].get("x_pos", 100),
                "y_pos": config_data["0"].get("y_pos", 100),
            },
            "1" : {
                "url": config_data["1"].get("url", ""),
                "transparent": config_data["1"].get("transparent", 50),
                "width": config_data["1"].get("width", 300),
                "height": config_data["1"].get("height", 100),
                "x_pos": config_data["1"].get("x_pos", 100),
                "y_pos": config_data["1"].get("y_pos", 300),
            }
        }
        self.url_input_1.setText(config_data["0"].get("url", ""))
        self.slider_value_1 = config_data["0"].get("transparent", 50)
        self.transparency_slider_1.setValue(
            self.slider_value_1
        )  # Default value
        self.transparency_label_1.setText(
            f"Transparency: {self.transparency_slider_1.value()}%"
        )
        self.url_input_2.setText(config_data["1"].get("url", ""))
        self.slider_value_2 = config_data["1"].get("transparent", 50)
        self.transparency_slider_2.setValue(
            self.slider_value_2
        )  # Default value
        self.transparency_label_2.setText(
            f"Transparency: {self.transparency_slider_2.value()}%"
        )
        with open("config.json", "w") as file:
            json.dump(config_data, file, indent=4)

    def save_configuration(self):
        """
        This method saves the configuration in the json file
        
        :param: None
        
        :returns: None
        """
        # Save configuration to config.json
        if self.url_input_1.text() or self.url_input_2.text():
            try:
                with open("config.json", "r") as config_file:
                    config_data = json.load(config_file)
                config_data["0"]["url"] = self.url_input_1.text()
                config_data["0"]["transparent"] = self.transparency_slider_1.value()
                config_data["1"]["url"] = self.url_input_2.text()
                config_data["1"]["transparent"] = self.transparency_slider_2.value()
                with open("config.json", "w") as file:
                    json.dump(config_data, file, indent=4)
                QMessageBox.information(self, "Saved", "Your configuration is Saved")
            except FileNotFoundError:
                QMessageBox.warning(self, "File Not Found", "Config file not found.")
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))
        else:
            QMessageBox.warning(self, "URL not filled", "you must put a valid URL")
    
    def open_windows(self) -> None:
        """
        This Method opens the windows 1 & 2 if the URL exists
        
        :param: None
        
        :returns: None
        """
        self.save_configuration()
        if self.url_input_1.text():
            self.overlay1 = Overlay(0)
            self.overlay1.show()
        if self.url_input_2.text():
            self.overlay2 = Overlay(1)
            self.overlay2.show()
        self.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("khormo.ico"))
    url_window = MainWindow()
    url_window.show()

    sys.exit(app.exec_())
