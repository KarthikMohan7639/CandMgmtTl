def main():
    """Entry point for the desktop application."""
    # Lazy import PyQt5 to avoid import-time errors in non-GUI contexts
    import sys
    # configure logging
    try:
        from app.utils.logging_config import configure_logging
        configure_logging()
    except Exception:
        pass

    from PyQt5.QtWidgets import QApplication
    from app.ui.main_window import MainWindow

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
