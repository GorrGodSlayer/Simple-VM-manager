import sys
import psutil
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

class VMMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VM Resource Monitor")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.cpu_plot = pg.PlotWidget(title="CPU Usage")
        self.ram_plot = pg.PlotWidget(title="RAM Usage")
        self.net_plot = pg.PlotWidget(title="Network Usage")

        layout.addWidget(self.cpu_plot)
        layout.addWidget(self.ram_plot)
        layout.addWidget(self.net_plot)

        self.vm_data = {}
        self.time_axis = []
        self.update_interval = 100  # 100 ms = 0.1 seconds

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(self.update_interval)

    def update_plots(self):
        current_time = time.time()
        self.time_axis.append(current_time)
        if len(self.time_axis) > 100:
            self.time_axis = self.time_axis[-100:]

        for process in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
            if 'vm' in process.info['name'].lower():
                vm_name = process.info['name']
                if vm_name not in self.vm_data:
                    self.vm_data[vm_name] = {
                        'cpu': [],
                        'ram': [],
                        'net_sent': [],
                        'net_recv': []
                    }
                    self.cpu_plot.plot(pen=pg.intColor(len(self.vm_data), hues=len(self.vm_data), values=1, maxValue=255), name=vm_name)
                    self.ram_plot.plot(pen=pg.intColor(len(self.vm_data), hues=len(self.vm_data), values=1, maxValue=255), name=vm_name)
                    self.net_plot.plot(pen=pg.intColor(len(self.vm_data), hues=len(self.vm_data), values=1, maxValue=255), name=f"{vm_name} (Sent)")
                    self.net_plot.plot(pen=pg.intColor(len(self.vm_data), hues=len(self.vm_data), values=1, maxValue=255, alpha=128), name=f"{vm_name} (Recv)")

                self.vm_data[vm_name]['cpu'].append(process.info['cpu_percent'])
                self.vm_data[vm_name]['ram'].append(process.info['memory_percent'])

                net_io = process.io_counters()
                self.vm_data[vm_name]['net_sent'].append(net_io.bytes_sent)
                self.vm_data[vm_name]['net_recv'].append(net_io.bytes_recv)

                if len(self.vm_data[vm_name]['cpu']) > 100:
                    self.vm_data[vm_name]['cpu'] = self.vm_data[vm_name]['cpu'][-100:]
                    self.vm_data[vm_name]['ram'] = self.vm_data[vm_name]['ram'][-100:]
                    self.vm_data[vm_name]['net_sent'] = self.vm_data[vm_name]['net_sent'][-100:]
                    self.vm_data[vm_name]['net_recv'] = self.vm_data[vm_name]['net_recv'][-100:]

        self.cpu_plot.clear()
        self.ram_plot.clear()
        self.net_plot.clear()

        for i, (vm_name, data) in enumerate(self.vm_data.items()):
            self.cpu_plot.plot(self.time_axis, data['cpu'], pen=pg.intColor(i, hues=len(self.vm_data), values=1, maxValue=255), name=vm_name)
            self.ram_plot.plot(self.time_axis, data['ram'], pen=pg.intColor(i, hues=len(self.vm_data), values=1, maxValue=255), name=vm_name)
            self.net_plot.plot(self.time_axis, data['net_sent'], pen=pg.intColor(i, hues=len(self.vm_data), values=1, maxValue=255), name=f"{vm_name} (Sent)")
            self.net_plot.plot(self.time_axis, data['net_recv'], pen=pg.intColor(i, hues=len(self.vm_data), values=1, maxValue=255, alpha=128), name=f"{vm_name} (Recv)")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VMMonitor()
    window.show()
    sys.exit(app.exec_())
