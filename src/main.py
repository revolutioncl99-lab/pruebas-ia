"""Editor de Video RevoCL - Entry point"""
import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Editor de Video RevoCL")
    app.setOrganizationName("RevoCL")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
