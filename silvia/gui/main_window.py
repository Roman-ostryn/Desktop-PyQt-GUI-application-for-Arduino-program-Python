# from serialcom.serial_manager import SerialManager
from serialcom.mock_serial_manager import SerialManager  # Use mock version

from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QVBoxLayout
# from PyQt6.QtCore import Qt
from gui.screens.home_screen import HomeScreen
from gui.screens.brew_screen import BrewScreen

from gui.screens.steam_screen import SteamScreen
from gui.screens.flush_screen import FlushScreen

from gui.screens.settings_screen import SettingsScreen




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Silvia Lever Coffee Controller")
        self.setFixedSize(600, 360)
        # self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowMinimizeButtonHint)
        # self.showNormal()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Create and start the serial manager
        self.serial = SerialManager()
        self.serial.start()

        # Pass serial and callback to screens
        self.home_screen = HomeScreen(self.serial)
        self.brew_screen = BrewScreen(self.serial, on_back=self.show_home_screen)

        self.stack.addWidget(self.home_screen)
        self.stack.addWidget(self.brew_screen)

        self.flush_screen = FlushScreen(self.serial, on_back=self.show_home_screen)        
        self.steam_screen = SteamScreen(self.serial, on_back=self.show_home_screen)
        self.stack.addWidget(self.steam_screen)
        self.stack.addWidget(self.flush_screen)
        
        self.settings_screen = SettingsScreen(on_save=self.set_temps, on_back=self.show_home_screen)
        self.stack.addWidget(self.settings_screen)

        # Current settings
        self.brew_temp = 93
        self.steam_temp = 130
        
        # Pass temperature settings to screens
        self.settings_screen.set_initial_temps(self.brew_temp, self.steam_temp)
        
        # Connect HomeScreen button to switch to BrewScreen
        self.home_screen.brew_btn.clicked.connect(self.show_brew_screen)
        self.home_screen.steam_button.clicked.connect(self.show_steam_screen)
        self.home_screen.flush_button.clicked.connect(self.show_flush_screen)
        
        self.home_screen.settings_button.clicked.connect(self.show_settings_screen)
        
        self.home_screen.start_button.clicked.connect(self.serial.start)
        self.home_screen.stop_button.clicked.connect(self.serial.stop)



    def show_brew_screen(self):
        self.stack.setCurrentWidget(self.brew_screen)

    def show_home_screen(self):
        self.stack.setCurrentWidget(self.home_screen)
        
    def show_steam_screen(self):
        self.stack.setCurrentWidget(self.steam_screen)
        
    def show_flush_screen(self):
        self.stack.setCurrentWidget(self.flush_screen)
        
    def set_temps(self, brew, steam):
        self.brew_temp = brew
        self.steam_temp = steam
        # Send temperature settings to hardware
        self.serial.send_command(f"SET_TEMP BREW {brew}")
        self.serial.send_command(f"SET_TEMP STEAM {steam}")
        print(f"Saved: Brew={brew}, Steam={steam}")
        self.show_home_screen()

    def show_settings_screen(self):
        self.stack.setCurrentWidget(self.settings_screen)

