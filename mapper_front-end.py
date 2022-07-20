import sys
import pytz
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, \
    QDateTimeEdit, QFileDialog
from geopy.geocoders import Nominatim

import Cell_tower_mapper


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CDR Mapper by Fetterly & Berg (2022)")
        self.setWindowIcon(QIcon("mobile-phone-cast.png"))

        ## build generate button
        self.generate_button = QPushButton("Generate!")
        self.generate_button.setCheckable(True)
        self.generate_button.clicked.connect(self.press_generate)
        self.generate_button.setIcon(QIcon("map--plus.png"))
        self.generate_button.setIconSize(QSize(16,16))
        self.generate_button.setFixedSize(100,50)

        ## build address input
        self.ILinput = QLineEdit()
        self.ILinput.setPlaceholderText("Incident Location Address:")
        self.ILinput.setFixedSize(500,25)

        ## build start, end time inputs
        self.STlabel = QLabel("Start Time:")
        self.STlabel.setFixedSize(200,10)
        self.STinput = QDateTimeEdit()
        self.STinput.setFixedSize(500,25)

        self.ETlabel = QLabel("End Time:")
        self.ETlabel.setFixedSize(200,10)
        self.ETinput = QDateTimeEdit()
        self.ETinput.setFixedSize(500,25)

        ## build file selector
        def openFileNameDialog(self):
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getOpenFileName(self,"Select your CDR file", "","Excel Files (*.xl*)", options=options)
            if fileName:
             return(fileName)

        ## call file selector before opening UI
        self.filename = openFileNameDialog(self)
        self.filenamelabel = QLabel("Selected File: "+self.filename)
        self.filenamelabel.setFixedHeight(25)

        ## set layout of the main window
        layout = QVBoxLayout()
        widgets = (
            self.filenamelabel,
            self.ILinput,
            self.STlabel,
            self.STinput,
            self.ETlabel,
            self.ETinput,
            self.generate_button
        )
        for w in widgets:
            layout.addWidget(w)
        container = QWidget()
        layout.setSpacing(0)
        container.setLayout(layout)

        self.setMinimumSize(QSize(600,300))
        self.setCentralWidget(container)

    ## define what pressing generate button does. first geolocates the address and converts to coordinates
    def press_generate(self):
        self.generate_button.setText("Generating...")
        locator = Nominatim(user_agent="PubDefenders")
        try:
            location = locator.geocode(self.ILinput.text())
        except:
            location = []

        timezone = pytz.timezone('US/Eastern')
        aware1 = timezone.localize(self.STinput.dateTime().toPyDateTime())
        aware2 = timezone.localize(self.ETinput.dateTime().toPyDateTime())
        timerange = [self.STinput.dateTime().toPyDateTime()-aware1.utcoffset(),
                     self.ETinput.dateTime().toPyDateTime()-aware2.utcoffset()]
        print(timerange)
        filepath = self.filename
        #CALL MAP GENERATOR HERE, PASS THROUGH FILEPATH, COORDS, TIMERANGE
        Cell_tower_mapper.main(filepath, location, timerange)
        print("Map generated!")
        self.generate_button.setText("Generate!")


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
