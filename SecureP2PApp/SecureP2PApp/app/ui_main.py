import os
import threading
from transfer import send_file, receive_file

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QTextEdit, QProgressBar, QLineEdit, QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from user_config import load_or_create_user_config
from peer import get_peer_ip


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        config = load_or_create_user_config()
        self.user_code = config["user_code"]

        self.setWindowTitle("Secure P2P File Transfer")
        self.setFixedSize(600, 500)

        self.logo_label = QLabel()
        self.logo_label.setPixmap(QPixmap("resources/logo.png").scaledToHeight(60, Qt.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setObjectName("LogoLabel")

        self.user_code_label = QLabel(f"Your Code: {self.user_code}")
        self.user_code_label.setAlignment(Qt.AlignCenter)
        self.user_code_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.connect_input = QLineEdit()
        self.connect_input.setPlaceholderText("Enter peer code (e.g. 538 911 274)")

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_peer)

        connect_layout = QHBoxLayout()
        connect_layout.addWidget(self.connect_input)
        connect_layout.addWidget(self.connect_button)

        self.send_button = QPushButton("Send File")
        self.send_button.clicked.connect(self.select_file)

        self.receive_button = QPushButton("Receive File")
        self.receive_button.clicked.connect(self.receive_file)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.receive_button)

        self.progress = QProgressBar()
        self.progress.setValue(0)

        self.status_log = QTextEdit()
        self.status_log.setReadOnly(True)

        self.history_log = QTextEdit()
        self.history_log.setReadOnly(True)
        self.history_log.setFixedWidth(200)
        self.history_log.setStyleSheet("""
            QTextEdit {
                background-color: #252525;
                color: #b0b0b0;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }
        """)

        content_layout = QVBoxLayout()
        content_layout.addWidget(self.logo_label)
        content_layout.addWidget(self.user_code_label)
        content_layout.addLayout(connect_layout)
        content_layout.addLayout(button_layout)
        content_layout.addWidget(self.progress)
        content_layout.addWidget(self.status_log)

        full_layout = QHBoxLayout()
        full_layout.addWidget(self.history_log)
        full_layout.addLayout(content_layout)

        self.setLayout(full_layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }

            QLabel#LogoLabel {
                margin-top: 10px;
            }

            QLabel {
                color: #cccccc;
                font-weight: 500;
                font-size: 14px;
            }

            QPushButton {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                padding: 10px;
                border-radius: 6px;
            }

            QPushButton:hover {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #5a5a5a;
            }

            QLineEdit {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 6px;
            }

            QProgressBar {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 5px;
                text-align: center;
                color: #ffffff;
            }

            QProgressBar::chunk {
                background-color: #4a90e2;
                width: 20px;
            }

            QTextEdit {
                background-color: #2a2a2a;
                color: #c0c0c0;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px;
            }
        """)

    def connect_to_peer(self):
        peer_code = self.connect_input.text().strip()
        if peer_code == "":
            QMessageBox.warning(self, "Input Required", "Please enter a valid peer code.")
            return

        ip = get_peer_ip(peer_code)
        if ip:
            self.peer_ip = ip
            self.status_log.append(f"[INFO] Connected to peer with code {peer_code} @ {ip}")
            self.history_log.append(f"🟢 Connected to {peer_code}")
        else:
            QMessageBox.warning(self, "Not Found", "No peer found with that code.")

    def select_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select File to Send")
        if filename:
            self.status_log.append(f"[INFO] Selected file: {filename}")
            self.history_log.append(f"📤 Sending: {filename.split('/')[-1]}")

            if not hasattr(self, 'peer_ip'):
                QMessageBox.warning(self, "Peer Not Connected", "Please connect to a peer before sending.")
                return

            def run_sender():
                def progress_callback(sent, total):
                    percent = int((sent / total) * 100)
                    self.progress.setValue(percent)

                success = send_file(
                    original_file_path=filename,
                    peer_ip=self.peer_ip,
                    peer_public_key_path="peer_public.pem",
                    progress_callback=progress_callback
                )

                if success:
                    self.status_log.append("[SUCCESS] File sent successfully.")
                    self.history_log.append("✅ File sent")
                else:
                    self.status_log.append("[ERROR] Failed to send file.")
                    self.history_log.append("❌ File send failed")

                self.progress.setValue(0)

            threading.Thread(target=run_sender).start()

    def receive_file(self):
        self.status_log.append("[INFO] Waiting to receive a file...")
        self.history_log.append("📥 Waiting for incoming file...")

        save_path, _ = QFileDialog.getSaveFileName(self, "Save Received File As")
        if save_path:
            def run_receiver():
                def progress_callback(received, total):
                    percent = int((received / total) * 100)
                    self.progress.setValue(percent)

                success = receive_file(
                    save_to_path=save_path,
                    listen_port=5000,
                    progress_callback=progress_callback
                )

                if success:
                    self.status_log.append(f"[SUCCESS] File saved to: {save_path}")
                    self.history_log.append(f"✅ Received: {os.path.basename(save_path)}")
                else:
                    self.status_log.append("[ERROR] File receive failed.")
                    self.history_log.append("❌ Receive failed")

                self.progress.setValue(0)

            threading.Thread(target=run_receiver).start()
