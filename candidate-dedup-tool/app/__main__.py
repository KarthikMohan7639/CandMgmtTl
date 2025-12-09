"""CLI wrapper so `python -m app` starts the GUI.

Usage:
  python -m app [--debug] [--demo]

--debug: enable console logging
--demo: attempt to load a bundled demo dataset (if implemented)
"""
import argparse
import logging


def _enable_logging():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s: %(message)s')


def main():
    parser = argparse.ArgumentParser(prog='python -m app')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging to console')
    parser.add_argument('--demo', action='store_true', help='Load demo dataset after startup (if available)')
    args = parser.parse_args()

    if args.debug:
        try:
            from app.utils.logging_config import configure_logging
            configure_logging(level=10)
        except Exception:
            _enable_logging()

    # Import the GUI entry point from app.main
    try:
        from app.main import main as gui_main
    except Exception:
        # If import fails, re-raise with context
        raise

    # If demo flag is used we set an environment variable that main.py or the UI can check.
    if args.demo:
        import os
        os.environ['APP_LOAD_DEMO'] = '1'

    gui_main()


if __name__ == '__main__':
    main()
