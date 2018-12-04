#!/usr/bin/env python
# coding=utf-8

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.curdir, '..', '..')))

from wittymail_server import flask_app

from flask import send_file, send_from_directory

# Static files are in the parent directory
base_path = '..'

@flask_app.route("/")
def index():
    '''
    Serve the 'index.html' page by default
    '''
    return send_file(os.path.join(base_path, "static" , "index.html"))

@flask_app.route('/<path:path>')
def route_static_files(path):
    '''
    Serve all other supporting files (*.js, *.css etc.)
    '''
    return send_from_directory(os.path.join(base_path, "static"), path)

@flask_app.route('/api/attachment/<path:path>')
def route_attachment_files(path):
    print(os.path.join(base_path, "attachment"))
    return send_from_directory(os.path.join(base_path, "attachment"), path)