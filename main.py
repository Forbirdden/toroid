import sys
import subprocess
import os
import time
from pathlib import Path
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QMainWindow, QMessageBox
from PySide6.QtCore import Qt, QTimer

class Toroid(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tor_process = None
        self.tor_running = False
        self.tor_pid = None
        self.torrc_path = self.get_torrc_path()
        self.initUI()
    
    def get_torrc_path(self):
        script_dir = Path(__file__).parent.absolute()
        return script_dir / "toroid.conf"
    
    def ensure_torrc_exists(self):
        if not self.torrc_path.exists():
            try:
                with open(self.torrc_path, 'w', encoding='utf-8') as f:
                    f.write("## Tor proxy configuration/torrc file\n")
                    f.write("SocksPort 9050\n")
                    f.write("DataDirectory /tmp/tor_temp_data\n")
                    f.write("Log notice stdout\n")
                return True
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Failed to create config file: {str(e)}')
                return False
        return True
    
    def initUI(self):
        self.setWindowTitle('Toroid')
        self.setGeometry(100, 100, 500, 450)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel('Tor proxy GUI')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        
        self.tor_button = QPushButton('Start proxy')
        self.tor_button.clicked.connect(self.toggle_tor)
        
        self.tor_status_label = QLabel('Proxy is offline')
        self.tor_status_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #fa0000;
                border-radius: 4px;
                color: white;
                font-weight: bold;
            }
        """)
        
        self.proxy_info_label = QLabel('Launch proxy to get an address')
        self.proxy_info_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
        """)
        
        self.torrc_info_label = QLabel(f'Config: {self.torrc_path}')
        self.torrc_info_label.setStyleSheet("""
            QLabel {
                padding: 6px;
                background-color: #e9ecef;
                border: 1px dashed #adb5bd;
                border-radius: 4px;
                font-size: 10px;
                color: #6c757d;
            }
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(self.tor_button)
        layout.addWidget(self.tor_status_label)
        layout.addWidget(self.proxy_info_label)
        layout.addWidget(self.torrc_info_label)
        layout.addStretch()
        
        central_widget.setLayout(layout)
        
        self.check_tor_installation(silent=True)
    
    def check_tor_installation(self, silent=False):
        try:
            result = subprocess.run(['which', 'tor'], capture_output=True, text=True)
            if result.returncode == 0:
                if not silent:
                    QMessageBox.information(self, 'Success', 'Tor package is installed')
                return True
            else:
                if not silent:
                    QMessageBox.warning(self, 'Error', 'Tor package is not installed')
                return False
        except Exception as e:
            if not silent:
                QMessageBox.critical(self, 'Error', f'Failed to check Tor installation: {str(e)}')
            return False
    
    def toggle_tor(self):
        if self.tor_running:
            self.stop_tor()
        else:
            self.start_tor()
    
    def start_tor(self):
        if not self.check_tor_installation(silent=True):
            QMessageBox.warning(self, 'Error', 'Tor package is not installed')
            return
        
        if not self.ensure_torrc_exists():
            return
        
        try:
            self.tor_process = subprocess.Popen([
                'tor',
                '-f', str(self.torrc_path)  
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
            
            self.tor_pid = self.tor_process.pid
            self.tor_running = True
            
            self.tor_button.setText('Stop proxy')
            self.tor_status_label.setText('Connecting to Tor...')
            self.tor_status_label.setStyleSheet("""
                QLabel {
                    padding: 8px;
                    background-color: #17a2b8;
                    border-radius: 4px;
                    color: white;
                    font-weight: bold;
                }
            """)
            
            QTimer.singleShot(2000, self.verify_tor_status)
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to start proxy: {str(e)}')
            self.tor_running = False
    
    def verify_tor_status(self):
        if self.tor_process and self.tor_process.poll() is None:
            self.tor_status_label.setText('Proxy is online')
            self.tor_status_label.setStyleSheet("""
                QLabel {
                    padding: 8px;
                    background-color: #28a745;
                    border-radius: 4px;
                    color: white;
                    font-weight: bold;
                }
            """)
            self.proxy_info_label.setText('SOCKS proxy is avaliable: 127.0.0.1:9050')
        else:
            self.tor_status_label.setText('Failed to launch proxy')
            self.tor_status_label.setStyleSheet("""
                QLabel {
                    padding: 8px;
                    background-color: #dc3545;
                    border-radius: 4px;
                    color: white;
                    font-weight: bold;
                }
            """)
            self.tor_running = False
            self.tor_button.setText('Start proxy')
    
    def stop_tor(self):
        if not self.tor_process:
            return
        
        try:
            if self.tor_pid:
                os.kill(self.tor_pid, 15)  
                time.sleep(1)
                
                if self.tor_process.poll() is None:
                    os.kill(self.tor_pid, 9) 
            
            self.tor_process = None
            self.tor_pid = None
            self.tor_running = False
            
            self.tor_button.setText('Start proxy')
            self.tor_status_label.setText('Proxy is offline')
            self.tor_status_label.setStyleSheet("""
                QLabel {
                    padding: 8px;
                    background-color: #fa0000;
                    border-radius: 4px;
                    color: white;
                    font-weight: bold;
                }
            """)
            self.proxy_info_label.setText('Launch proxy to get an address')
            
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to stop proxy: {str(e)}')
    
    def closeEvent(self, event):
        if self.tor_running:
            reply = QMessageBox.question(
                self,
                'Confirm',
                'Proxy is still running, stop it?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                self.stop_tor()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    try:
        app.setStyle('Fusion') 
    except:
        pass
    
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f8f9fa;
        }
        QPushButton {
            background-color: #c982ff;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #b35df5;
        }
        QPushButton:pressed {
            background-color: #d6abf7;
        }
    """)
    
    window = Toroid()
    window.show()
    sys.exit(app.exec_())