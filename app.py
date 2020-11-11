# -*- coding: utf-8 -*-
import os

import dash
import dash_bootstrap_components as dbc
import flask
import logging
from logging.handlers import RotatingFileHandler

from util.configutil import IMAGE_DIR

server = flask.Flask(__name__)
# https://dash-bootstrap-components.opensource.faculty.ai/
# https://bootswatch.com/
external_stylesheets = [
    dbc.themes.LUX,
    # Version 4.21.0
    '/css/vis.min.css'
]
external_scripts = [
    '/js/jquery-3.3.1.min.js',
    '/js/network.js',
]
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets, external_scripts=external_scripts)
app.config.suppress_callback_exceptions = True
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

handler = RotatingFileHandler('server.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.server.logger.addHandler(handler)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('DashApp')

matrics_ = None


@app.server.route('/css/<path:path>')
def static_css(path):
    """
    TODO
    there is also the possibility to create an assets folder
    https://dash.plot.ly/external-resources

    https://community.plot.ly/t/how-do-i-use-dash-to-add-local-css/4914/15
    """
    static_folder = os.path.join(os.getcwd(), 'css')
    return flask.send_from_directory(static_folder, path)


@app.server.route('/js/<path:path>')
def static_js(path):
    static_folder = os.path.join(os.getcwd(), 'js')
    return flask.send_from_directory(static_folder, path)


# Add a static image route that serves images from desktop
# Be *very* careful here - you don't want to serve arbitrary files
# from your computer or server.
# This could be refactored.
@app.server.route(f'/imgdir/<path:image_path>.png')
def serve_png(image_path):
    """
    https://community.plot.ly/t/adding-local-image/4896/4
    """
    image_name = f'{os.path.basename(image_path)}.png'
    # if image_name not in list_of_images:
    #     raise Exception('"{}" is excluded from the allowed static files'.format(image_path))
    return flask.send_from_directory(IMAGE_DIR, image_name)


@app.server.route(f'/imgdir/<path:image_path>.jpg')
def serve_jpg(image_path):
    """
    https://community.plot.ly/t/adding-local-image/4896/4
    """
    dir_ = os.path.join("/", os.path.dirname(image_path))
    image_name = f'{os.path.basename(image_path)}.jpg'
    # if image_name not in list_of_images:
    #     raise Exception('"{}" is excluded from the allowed static files'.format(image_path))
    return flask.send_from_directory(dir_, image_name)
