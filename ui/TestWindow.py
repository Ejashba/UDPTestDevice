from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QFormLayout
from PyQt5.QtCore import pyqtSlot, QThreadPool
import pyqtgraph
import pyqtgraph.exporters
import datetime
import socket
import matplotlib.pyplot as plt

class TestWindow(QWidget):
    def __init__(self, host: str, port: str):
        """
        defines test window
        """
        super().__init__(parent=None)
        print("setting up comms with host", host, "and port", port)
        self.default_frequency = 1000
        self.ENCODING = 'ISO-8859-1'
        self.test_data = []
        # Create UI elements
        self.setWindowTitle("Device Test App")
        self.setGeometry(125, 125, 1000, 800)
        self.thread_manager = QThreadPool()
        self.data = ''

        self.time_series, self.volt_series, self.ampere_series = [], [], []

        self.layout = QFormLayout()
        self._createConnectionFields()
        self._createDurationFields()
        self._createDiscoverButton()
        self._createStartButton()
        self._createIDReturnField()
        self._createOverwriteWarning()
        self._createStopButton()
        self._createSaveButton()
        self._createDiscardButton()
        self._createLivePlot() #TODO comment out
        self.setLayout(self.layout)

        self._initSocket(host, port)
    
    def _createIDReturnField(self):
        self.DeviceIDField = QLabel()
        self.DeviceIDField.setHidden(True)
        self.layout.addRow(self.DeviceIDField)

    def _initSocket(self, host: str, port: str):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, int(port)))     

    def _createDiscoverButton(self):
        self.discoverButton = QPushButton('Discover')
        self.discoverButton.clicked.connect(self.sendDiscoveryMsg)
        self.layout.addRow(self.discoverButton)

    def _createStartButton(self):
        self.startButton = QPushButton('Start Test')
        self.startButton.clicked.connect(self.onStartTestSafely)
        self.layout.addRow(self.startButton)

    def _createDurationFields(self):
        self.layout.addRow(QLabel('<b>Test Duration</b>'))

        self.secondsField = QLineEdit(self)
        self.layout.addRow('seconds:', self.secondsField)
        self.secondsField.setPlaceholderText('0')

        self.frequencyField = QLineEdit(self)
        self.layout.addRow('frequency (ms):', self.frequencyField)
        self.frequencyField.setPlaceholderText(str(self.default_frequency))
       
    def _createConnectionFields(self):
        self.layout.addRow(QLabel('<b>Connect To Device</b>'))

        self.HostField = QLineEdit(self)
        self.layout.addRow('IP Address', self.HostField)

        self.PortField = QLineEdit(self)
        self.layout.addRow('Port #', self.PortField)


    def _createStopButton(self):
        self.StopButton = QPushButton('Abort Test')
        self.StopButton.setStyleSheet("color : red")
        self.StopButton.clicked.connect(self.onStopTest)
        self.layout.addRow(self.StopButton)

    def _createOverwriteWarning(self):
        self.WarningLabel = QLabel('WARNING: Save or discard current test before starting new test')
        self.WarningLabel.setHidden(True)
        self.layout.addRow(self.WarningLabel)

    def _createDiscardButton(self):
        self.DiscardButton = QPushButton('Discard Test Data (Irreversible)')
        self.DiscardButton.clicked.connect(self.discardTest)
        self.layout.addRow(self.DiscardButton)

    def _longListen(self, expected_messages):
        for i in range(expected_messages+2): #add two for start and final idle messages
            self.data, addr = self.socket.recvfrom(1024)
            self.data = self.data.decode('ISO-8859-1')
            print(f"{addr} sent:", self.data)
            pieces = self.data.split(';')
            if pieces[0] == 'TEST' and pieces[1] != 'RESULT=STARTED':
                break
            elif pieces[0] == "STATUS" and pieces[1].split('=')[0] == "TIME":
                time = int(pieces[1].split('=')[1])
                mV = round(float(pieces[2].split('=')[1]), 2)
                mA = round(float(pieces[3].split('=')[1]), 2)
                self.test_data.append([time, mV, mA])
                self.updatePlot()


    def _shortListen(self):
        self.data, addr = self.socket.recvfrom(1024)
        self.data = self.data.decode('ISO-8859-1')
        print(f"{addr} sent:", self.data)
        self.DeviceIDField = QLabel(self.data)
        self.DeviceIDField.setHidden(False)
    
    def _createLivePlot(self):
        self.volt_graph = pyqtgraph.PlotWidget()
        self.ampere_graph = pyqtgraph.PlotWidget()

        volt_pen = pyqtgraph.mkPen(color=(255, 0, 0), width=3)
        ampere_pen = pyqtgraph.mkPen(color=(0, 0, 255), width=3)

        self.volt_line = self.volt_graph.plot(self.time_series, self.volt_series, pen=volt_pen, symbol='o', symbolSize='5', symbolBrush=('r'))
        self.ampere_line = self.ampere_graph.plot(self.time_series, self.ampere_series, pen=ampere_pen, symbol='o', symbolSize='5', symbolBrush=('b'))
        
        styles = {"color": "black", "font-size": "15px"}
        self.volt_graph.setLabel("left", "Voltage (mV)", **styles)
        self.volt_graph.setLabel("bottom", "Time (ms)", **styles)
        self.ampere_graph.setLabel("left", "Current (mA)", **styles)
        self.ampere_graph.setLabel("bottom", "Time (ms)", **styles)

        self.volt_graph.showGrid(x=True, y=True)
        self.ampere_graph.showGrid(x=True, y=True)

        self.volt_graph.setBackground('w')
        self.ampere_graph.setBackground('w')

        self.volt_graph.addLegend()
        self.ampere_graph.addLegend()

        self.layout.addRow(self.volt_graph)
        self.layout.addRow(self.ampere_graph)

    def _createSaveButton(self):
        self.saveButton = QPushButton('Save to PDF')
        self.saveButton.clicked.connect(self.saveTest)
        self.layout.addRow(self.saveButton)

    def send(self, msg):
        self.socket.sendto(bytes(msg, self.ENCODING), (self.HostField.text(), int(self.PortField.text())))

    def sendDiscoveryMsg(self):
        if self.HostField.text() and self.PortField.text():
            msg = 'ID;'
            self.send(msg)
            self._shortListen()


    @pyqtSlot()
    def onStartTestSafely(self):
        self.thread_manager.start(self.onStartTest)

    @pyqtSlot()
    def onStartTest(self):
        # Start device communication thread and show live plot
        if self.test_data:
            self.WarningLabel.setHidden(False)
            self.show()
        elif self.HostField.text() and self.PortField.text() and self.secondsField.text():
            self.WarningLabel.setHidden(True)
            self.show()
            seconds = float(self.secondsField.text())
            report_rate = self.default_frequency if not self.frequencyField.text() else int(self.frequencyField.text())
            msg = f"TEST;CMD=START;DURATION={seconds};RATE={report_rate};"
            self.send(msg)
            expected_messages = int((seconds*1000)//report_rate)
            self._longListen(expected_messages)
        
    def onStopTest(self):
        # Stop device communication thread
        if self.HostField.text() and self.PortField.text():
            msg = "TEST;CMD=STOP;"
            self.send(msg)
            self._shortListen()

    def updatePlot(self):
        # Update live plot
        self.time_series.append(self.test_data[-1][0])# = [item[0] for item in self.test_data]
        self.volt_series.append(self.test_data[-1][1])
        self.ampere_series.append(self.test_data[-1][2])

        self.volt_line.setData(self.time_series, self.volt_series)
        self.ampere_line.setData(self.time_series, self.ampere_series)
        self.show()

    def discardTest(self):
        self.test_data = []
        self.time_series = []
        self.volt_series = []
        self.ampere_series = []
        self.WarningLabel.setHidden(True)
        self.volt_graph = pyqtgraph.PlotWidget()
        self.ampere_graph = pyqtgraph.PlotWidget()

    def saveTest(self):
        # Save test results to a PDF
        if not self.test_data:
            print('No test data to save!')
            
        now = datetime.datetime.now()
        volt_filepath = f"../test_results/volts_Port-{self.PortField.text()}-Device_{now}.pdf"
        plt.plot(self.time_series, self.volt_series)
        plt.title('Voltage vs. Time')
        plt.xlabel('Time (ms)')
        plt.ylabel('Voltage (mV)')
        plt.savefig(volt_filepath)
        plt.clf()

        ampere_filepath = f"../test_results/amperes_Port-{self.PortField.text()}-Device_{now}.pdf"
        plt.plot(self.time_series, self.ampere_series)
        plt.title('Current vs. Time')
        plt.xlabel('Time (ms)')
        plt.ylabel('Current (mA)')
        plt.savefig(ampere_filepath)
     
        self.discardTest()
