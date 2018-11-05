#!/usr/bin/env python
# coding=utf-8

import os, sys
sys.path.insert(0, os.path.abspath('..'))
import time, webbrowser, threading, traceback

import util.bootstrap

import util.logger as logger

_logger = logger.get_logger(__name__)

def parse_cmd_args():
    import argparse
    import util.version as version

    parser = argparse.ArgumentParser()
    pretty_version = version.__pretty_version__
    parser.add_argument("--version", "-v", action = 'version', version = pretty_version)
    parser.add_argument("--skip-opening-browser", "-s", action='store_true', default=False, help = 'Do not automatically open a browser window (only serve REST API)')
    args = parser.parse_args()
    _logger.debug("CLI args: %s", args)
    return args

def start_flask_server():
    import wittymail_server
    flask_app = wittymail_server.flask_app
    flask_app.run()

def open_browser():
    print("A new browser window will open shortly, please wait...")
    # Wait for the HTTP server to start
    time.sleep(1)
    webbrowser.open("http://localhost:5000")

def main():
    ''' Main entry point for WittyMail
        - Start the REST API server
        - Open a browser window with the GUI
    '''
    try:
        args = parse_cmd_args()

        if not args.skip_opening_browser:
            # Wait for a few seconds for the REST API server to start accepting
            # connections, then launch a browser with the URL for the GUI
            t = threading.Thread(target=open_browser)
            t.start()

        # This call will block forever
        start_flask_server()
        
    except Exception:
        _logger.exception("Failed to start web server")
        sys.exit(1)
      
if __name__ == "__main__":
    main()
