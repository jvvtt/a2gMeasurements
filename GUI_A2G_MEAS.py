#from fbs_runtime.application_context.PyQt5 import ApplicationContext
import typing
from PyQt5.QtCore import QDateTime, Qt, QTimer, QObject, QThread, QMutex, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)

import sys
from a2gmeasurements import GimbalRS2, GpsSignaling, HelperA2GMeasurements

class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        # Parameters of the GUI
        self.number_lines_log_terminal = 5
        self.log_terminal_txt = ""
        
        self.originalPalette = QApplication.palette()

        # Combined button and pop-up list
        styleComboBox = QComboBox()
        styleComboBox.addItems(QStyleFactory.keys())

        styleLabel = QLabel("&Style:")
        styleLabel.setBuddy(styleComboBox)

        self.useStylePaletteCheckBox = QCheckBox("&Use style's standard palette")
        self.useStylePaletteCheckBox.setChecked(True)

        disableWidgetsCheckBox = QCheckBox("&Disable widgets")

        self.create_GPS_panel()
        self.create_log_terminal()
        self.create_Gimbal_TX_panel()
        self.create_Gimbal_RX_panel()
        self.create_FPGA_settings_panel()
        self.create_Beamsteering_settings_panel()
        self.create_Planning_Measurements_panel()
        self.create_pdp_plot_panel()
        
        self.createTopLeftGroupBox()
        self.createTopRightGroupBox()
        self.createBottomLeftTabWidget()
        self.createBottomRightGroupBox()
        self.createProgressBar()

        styleComboBox.activated[str].connect(self.changeStyle)
        self.useStylePaletteCheckBox.toggled.connect(self.changePalette)
        disableWidgetsCheckBox.toggled.connect(self.topLeftGroupBox.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.topRightGroupBox.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.bottomLeftTabWidget.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.bottomRightGroupBox.setDisabled)

        topLayout = QHBoxLayout()
        topLayout.addWidget(styleLabel)
        topLayout.addWidget(styleComboBox)
        topLayout.addStretch(1)
        topLayout.addWidget(self.useStylePaletteCheckBox)
        topLayout.addWidget(disableWidgetsCheckBox)

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.gimbalTXPanel, 0, 0)
        mainLayout.addWidget(self.gimbalRXPanel, 0, 1)
        mainLayout.addWidget(self.gpsPanel, 1, 0)
        mainLayout.addWidget(self.planningMeasurementsPanel, 1, 1)
        mainLayout.addWidget(self.fpgaSettingsPanel, 2, 0)
        mainLayout.addWidget(self.beamsteeringSettingsPanel, 2, 1)
        mainLayout.addWidget(self.pdpPlotPanel, 3, 0, 1, 2)        
        mainLayout.addWidget(self.log_widget, 4, 0, 1, 2)
        
        
        self.write_to_log_terminal('This is an example text')
        self.write_to_log_terminal('This is a new line')
        self.write_to_log_terminal('what ever')
        self.write_to_log_terminal('evasdgf')
        self.write_to_log_terminal('sadgfndsaf')
        self.write_to_log_terminal('dsgfmn')
        self.write_to_log_terminal('what ,mndsfb')
        self.write_to_log_terminal('sdafnb fd')        
                
        self.setLayout(mainLayout)

        self.setWindowTitle("Styles")
        self.changeStyle('Windows')        
        
        self.init_external_objs()


    def init_external_objs(self):
        1
        
    def write_to_log_terminal(self, newLine):
        '''
        New line to be written into the log terminal. The number of new lines it can handle is controlled
        by the parameter number_lines_log_terminal.
        
        TO BE CHECKED: THE NUMBER OF MAX CHARACTERS FOR A LINE HAS TO BE CHECKED IN THE CODE
        
        '''
        
        log_txt = self.log_terminal_txt.splitlines()
        
        if len(log_txt) < self.number_lines_log_terminal:
            self.log_terminal_txt = self.log_terminal_txt + newLine + "\n"
        else:
            for i in range(len(log_txt)-1, 0, -1):
                log_txt[i] = log_txt[i-1] + "\n"
            log_txt[0] = newLine + "\n"
            
            log_txt = ''.join(log_txt) 
            self.log_terminal_txt = log_txt
            
        self.log_widget.setPlainText(self.log_terminal_txt)
        
    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))
        self.changePalette()

    def changePalette(self):
        if (self.useStylePaletteCheckBox.isChecked()):
            QApplication.setPalette(QApplication.style().standardPalette())
        else:
            QApplication.setPalette(self.originalPalette)

    def advanceProgressBar(self):
        curVal = self.progressBar.value()
        maxVal = self.progressBar.maximum()
        self.progressBar.setValue(int(curVal + (maxVal - curVal) / 100))

    def create_log_terminal(self):
        '''
        Access the widget contents by using self.log_widget.setPlainText('')
        
        '''
        self.log_widget = QTextEdit(self)
        self.log_widget.setReadOnly(True) # make it read-only        
        
    def create_FPGA_settings_panel(self):
        self.fpgaSettingsPanel = QGroupBox('FPGA settings')
        
    def create_Beamsteering_settings_panel(self):
        self.beamsteeringSettingsPanel = QGroupBox('Beamsteering settings')
    
    def create_Gimbal_TX_panel(self):
        self.gimbalTXPanel = QGroupBox('Gimbal TX')
        
        yaw_label = QLabel('Yaw [D]:')
        pitch_label = QLabel('Pitch [D]:')
        
        self.tx_abs_radio_button = QRadioButton("Absolute")
        self.tx_rel_radio_button = QRadioButton("Relative")        
        self.tx_abs_radio_button.setChecked(True)
        
        self.tx_yaw_value_text_edit = QLineEdit('')
        self.tx_pitch_value_text_edit = QLineEdit('')
        
        self.tx_step_manual_move_gimbal_text_edit = QLineEdit('')
        
        self.tx_gimbal_manual_move_push_button = QPushButton('Move')
        self.tx_gimbal_move_left_push_button = QPushButton('<-')
        self.tx_gimbal_move_right_push_button = QPushButton('->')
        self.tx_gimbal_move_up_push_button = QPushButton('^')
        self.tx_gimbal_move_down_push_button = QPushButton('v')
        
        layout = QGridLayout()
        layout.addWidget(self.tx_abs_radio_button, 0, 0, 1, 3)
        layout.addWidget(self.tx_rel_radio_button, 0, 3, 1, 3)
        layout.addWidget(self.tx_gimbal_manual_move_push_button, 0, 6, 1, 4)
        
        layout.addWidget(yaw_label, 1, 0, 1, 1)
        layout.addWidget(self.tx_yaw_value_text_edit, 1, 1, 1, 4)
        layout.addWidget(pitch_label, 1, 5, 1, 1)        
        layout.addWidget(self.tx_pitch_value_text_edit, 1, 6, 1, 4)
        
        layout.addWidget(self.tx_gimbal_move_left_push_button, 3, 2, 1, 2)
        layout.addWidget(self.tx_gimbal_move_right_push_button, 3, 6, 1, 2)
        layout.addWidget(self.tx_gimbal_move_up_push_button, 2, 4, 1, 2)
        layout.addWidget(self.tx_gimbal_move_down_push_button, 4, 4, 1, 2)
        layout.addWidget(self.tx_step_manual_move_gimbal_text_edit, 3, 4, 1, 2)
        
        self.gimbalTXPanel.setLayout(layout)
        
    def create_Gimbal_RX_panel(self):
        self.gimbalRXPanel = QGroupBox('Gimbal RX')
        
        yaw_label = QLabel('Yaw [D]:')
        pitch_label = QLabel('Pitch [D]:')
        
        self.rx_abs_radio_button = QRadioButton("Absolute")
        self.rx_rel_radio_button = QRadioButton("Relative")        
        self.rx_abs_radio_button.setChecked(True)
        
        self.rx_yaw_value_text_edit = QLineEdit('')
        self.rx_pitch_value_text_edit = QLineEdit('')
        
        self.rx_step_manual_move_gimbal_text_edit = QLineEdit('')
        
        self.rx_gimbal_manual_move_push_button = QPushButton('Move')
        self.rx_gimbal_move_left_push_button = QPushButton('<-')
        self.rx_gimbal_move_right_push_button = QPushButton('->')
        self.rx_gimbal_move_up_push_button = QPushButton('^')
        self.rx_gimbal_move_down_push_button = QPushButton('v')
        
        layout = QGridLayout()
        layout.addWidget(self.rx_abs_radio_button, 0, 0, 1, 3)
        layout.addWidget(self.rx_rel_radio_button, 0, 3, 1, 3)
        layout.addWidget(self.rx_gimbal_manual_move_push_button, 0, 6, 1, 4)
        
        layout.addWidget(yaw_label, 1, 0, 1, 1)
        layout.addWidget(self.rx_yaw_value_text_edit, 1, 1, 1, 4)
        layout.addWidget(pitch_label, 1, 5, 1, 1)        
        layout.addWidget(self.rx_pitch_value_text_edit, 1, 6, 1, 4)
        
        layout.addWidget(self.rx_gimbal_move_left_push_button, 3, 2, 1, 2)
        layout.addWidget(self.rx_gimbal_move_right_push_button, 3, 6, 1, 2)
        layout.addWidget(self.rx_gimbal_move_up_push_button, 2, 4, 1, 2)
        layout.addWidget(self.rx_gimbal_move_down_push_button, 4, 4, 1, 2)
        layout.addWidget(self.rx_step_manual_move_gimbal_text_edit, 3, 4, 1, 2)
        
        self.gimbalRXPanel.setLayout(layout)
    
    def create_Planning_Measurements_panel(self):
        self.planningMeasurementsPanel = QGroupBox('Planning measurements')
        
    def create_GPS_panel(self):
        self.gpsPanel = QGroupBox('GPS Information')
        
        tx_info_label = QLabel('TX')
        rx_info_label = QLabel('RX')
        
        tx_info_label.setAlignment(Qt.AlignCenter)
        rx_info_label.setAlignment(Qt.AlignCenter)
        
        tx_x_label = QLabel('X:')
        tx_y_label = QLabel('Y:')
        tx_z_label = QLabel('Z:')
        tx_x_value_label = QLabel('')
        tx_y_value_label = QLabel('')
        tx_z_value_label = QLabel('')
        
        rx_x_label = QLabel('X:')
        rx_y_label = QLabel('Y:')
        rx_z_label = QLabel('Z:')
        rx_x_value_label = QLabel('')
        rx_y_value_label = QLabel('')
        rx_z_value_label = QLabel('')
        
        layout = QGridLayout()
        layout.addWidget(tx_info_label, 0, 0, 1, 5)
        layout.addWidget(rx_info_label, 0, 5, 1, 5)
        layout.addWidget(tx_x_label, 1, 0, 1, 1)
        layout.addWidget(tx_z_label, 2, 0, 1, 1)
        layout.addWidget(tx_y_label, 3, 0, 1, 1)
        layout.addWidget(tx_x_value_label, 1, 1, 1, 4)
        layout.addWidget(tx_y_value_label, 2, 1, 1, 4)
        layout.addWidget(tx_z_value_label, 3, 1, 1, 4)
        layout.addWidget(rx_x_label, 1, 5, 1, 1)
        layout.addWidget(rx_z_label, 2, 5, 1, 1)
        layout.addWidget(rx_y_label, 3, 5, 1, 1)
        layout.addWidget(rx_x_value_label, 1, 6, 1, 4)
        layout.addWidget(rx_y_value_label, 2, 6, 1, 4)
        layout.addWidget(rx_z_value_label, 3, 6, 1, 4)
        #layout.setRowStretch(3, 1)
        
        self.gpsPanel.setLayout(layout)
        
    def create_pdp_plot_panel(self):
        self.pdpPlotPanel = QGroupBox('PDP')
    
    def createTopLeftGroupBox(self):
        self.topLeftGroupBox = QGroupBox("Group 1")

        radioButton1 = QRadioButton("Radio button 1")
        radioButton2 = QRadioButton("Radio button 2")
        radioButton3 = QRadioButton("Radio button 3")
        radioButton1.setChecked(True)

        checkBox = QCheckBox("Tri-state check box")
        checkBox.setTristate(True)
        checkBox.setCheckState(Qt.PartiallyChecked)

        layout = QVBoxLayout()
        layout.addWidget(radioButton1)
        layout.addWidget(radioButton2)
        layout.addWidget(radioButton3)
        layout.addWidget(checkBox)
        layout.addStretch(1)
        self.topLeftGroupBox.setLayout(layout)    

    def createTopRightGroupBox(self):
        self.topRightGroupBox = QGroupBox("Group 2")

        defaultPushButton = QPushButton("Default Push Button")
        defaultPushButton.setDefault(True)

        togglePushButton = QPushButton("Toggle Push Button")
        togglePushButton.setCheckable(True)
        togglePushButton.setChecked(True)

        flatPushButton = QPushButton("Flat Push Button")
        flatPushButton.setFlat(True)

        layout = QVBoxLayout()
        layout.addWidget(defaultPushButton)
        layout.addWidget(togglePushButton)
        layout.addWidget(flatPushButton)
        layout.addStretch(1)
        self.topRightGroupBox.setLayout(layout)

    def createBottomLeftTabWidget(self):
        self.bottomLeftTabWidget = QTabWidget()
        self.bottomLeftTabWidget.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Ignored)

        tab1 = QWidget()
        tableWidget = QTableWidget(10, 10)

        tab1hbox = QHBoxLayout()
        tab1hbox.setContentsMargins(5, 5, 5, 5)
        tab1hbox.addWidget(tableWidget)
        tab1.setLayout(tab1hbox)

        tab2 = QWidget()
        textEdit = QTextEdit()

        textEdit.setPlainText("Twinkle, twinkle, little star,\n"
                              "How I wonder what you are.\n" 
                              "Up above the world so high,\n"
                              "Like a diamond in the sky.\n"
                              "Twinkle, twinkle, little star,\n" 
                              "How I wonder what you are!\n")

        tab2hbox = QHBoxLayout()
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2hbox.addWidget(textEdit)
        tab2.setLayout(tab2hbox)

        self.bottomLeftTabWidget.addTab(tab1, "&Table")
        self.bottomLeftTabWidget.addTab(tab2, "Text &Edit")

    def createBottomRightGroupBox(self):
        self.bottomRightGroupBox = QGroupBox("Group 3")
        self.bottomRightGroupBox.setCheckable(True)
        self.bottomRightGroupBox.setChecked(True)

        lineEdit = QLineEdit('s3cRe7')
        lineEdit.setEchoMode(QLineEdit.Password)

        spinBox = QSpinBox(self.bottomRightGroupBox)
        spinBox.setValue(50)

        dateTimeEdit = QDateTimeEdit(self.bottomRightGroupBox)
        dateTimeEdit.setDateTime(QDateTime.currentDateTime())

        slider = QSlider(Qt.Horizontal, self.bottomRightGroupBox)
        slider.setValue(40)

        scrollBar = QScrollBar(Qt.Horizontal, self.bottomRightGroupBox)
        scrollBar.setValue(60)

        dial = QDial(self.bottomRightGroupBox)
        dial.setValue(30)
        dial.setNotchesVisible(True)

        layout = QGridLayout()
        layout.addWidget(lineEdit, 0, 0, 1, 2)
        layout.addWidget(spinBox, 1, 0, 1, 2)
        layout.addWidget(dateTimeEdit, 2, 0, 1, 2)
        layout.addWidget(slider, 3, 0)
        layout.addWidget(scrollBar, 4, 0)
        layout.addWidget(dial, 3, 1, 2, 1)
        layout.setRowStretch(5, 1)
        self.bottomRightGroupBox.setLayout(layout)

    def createProgressBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 10000)
        self.progressBar.setValue(0)

        timer = QTimer(self)
        timer.timeout.connect(self.advanceProgressBar)
        timer.start(1000)


if __name__ == '__main__':
#    appctxt = ApplicationContext()
    app = QApplication([])
    gallery = WidgetGallery()
    gallery.show()
    #sys.exit(appctxt.app.exec())
    sys.exit(app.exec())
