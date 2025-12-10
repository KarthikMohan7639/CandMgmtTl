def main():
    """Entry point for the desktop application."""
    # Lazy import PyQt5 to avoid import-time errors in non-GUI contexts
    import sys
    import os
    
    # Suppress Qt font warnings
    os.environ['QT_LOGGING_RULES'] = 'qt.qpa.fonts.warning=false'
    
    # configure logging
    try:
        from app.utils.logging_config import configure_logging
        configure_logging()
    except Exception:
        pass

    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QFont
    from app.ui.main_window import MainWindow

    app = QApplication(sys.argv)
    
    # Set default application font to avoid font warnings
    try:
        default_font = QFont("Segoe UI", 9)
        if not default_font.exactMatch():
            # Fallback to Arial or system default
            default_font = QFont("Arial", 9)
        app.setFont(default_font)
    except Exception:
        pass
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
