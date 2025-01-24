#!/usr/bin/env python3

import sys
from PySide2.QtWidgets import QApplication
import argparse
from gui.main_window import MainWindow

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", required=True, help="Raspberry Pi IP address")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = MainWindow(args.ip)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
