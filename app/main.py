import sys
import socket
from PyQt5.QtWidgets import QApplication
from ui_main import MainWindow
from encryption import generate_rsa_keys
from peer import register_peer
from user_config import load_or_create_user_config

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def main():
    generate_rsa_keys()
    config = load_or_create_user_config()
    peer_code = config["user_code"]
    ip = get_local_ip()
    
    
    register_peer(peer_code, ip)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())



if __name__ == "__main__":
    main()
