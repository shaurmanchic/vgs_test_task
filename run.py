from flask import Flask, make_response, render_template, request, session
from flask_sessionstore import Session
import numpy as np
from PIL import Image
import requests
import time
import random
from collections import deque
import itertools


import config


IMAGE_NAME = "./static/very_good_security.png"
MAX_COOKIE_SIZE = 100

from werkzeug.debug import DebuggedApplication

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['ENV'] = 'development'
app.config['TESTING'] = True
app.wsgi_app = DebuggedApplication(app.wsgi_app, True)
app.debug = True


sess = Session()
sess.init_app(app)
if __name__ == "__main__":
    app.run(host='0.0.0.0:5000')


@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'GET':
        return initiate_page()
    if request.method == 'POST':
        return prepare_pixel_payload()


def initiate_page():
    # Download the image and get an RGB pixel array
    # Convert the image to a 2-dimentional array of pixel RGB values
    image_pixel_array = np.array(Image.open(IMAGE_NAME))
    width_pixels = range(image_pixel_array.shape[0])
    height_pixels = range(image_pixel_array.shape[1])

    # progress_pixel_array = np.zeros([len(width_pixels),len(height_pixels)], dtype=int)

    # unsent_pixels_index = list(itertools.product(width_pixels, height_pixels))
    # random.shuffle(unsent_pixels_index)
    session['processed_pixels'] = np.zeros([len(width_pixels), len(height_pixels)], dtype=int)
    #     random.shuffle(random_pixel_row)
    #     session['row_'+str(row)] = random_pixel_row
    # session['unsent_pixels_index'] = unsent_pixels_index
    # session['progress'] = progress_pixel_array
    response = make_response(render_template('index.html'))
    response.set_cookie('image-width', str(len(width_pixels)))
    response.set_cookie('image-height', str(len(height_pixels)))
    return response


def prepare_pixel_payload():
    response = make_response()
    response.headers['pixels'] = get_pixel_string()
    return response


def get_pixel_string():
    # Find available pixels and compress them into a string that can be saved in a cookie
    try:
        pixel_string = ''
        image_width = int(request.cookies['image-width'])
        image_height = int(request.cookies['image-height'])
        processed_pixels = session['processed_pixels']
        image_pixel_array = np.array(Image.open(IMAGE_NAME))
        while len(pixel_string) < 75:
            pixel_col = random.randint(0, image_width) - 1
            pixel_row = random.randint(0, image_height) - 1
            if processed_pixels[pixel_col, pixel_row] == 1:
                continue
            pixel_index = image_width * pixel_row * 4 + pixel_col * 4
            pixel_rgb = image_pixel_array[pixel_row, pixel_col]
            pixel = f'{pixel_index}={pixel_rgb[0]},{pixel_rgb[1]},{pixel_rgb[2]};'
            pixel_string = pixel_string + pixel
            processed_pixels[pixel_col, pixel_row] = 1
        session['processed_pixels'] = processed_pixels
        return pixel_string
    except Exception as e:
        print(session)
        print(e)

