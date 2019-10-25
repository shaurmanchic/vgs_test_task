from flask import Flask, make_response, render_template, request, session
from flask_sessionstore import Session
import numpy as np
from PIL import Image
import requests
import time
import random
import redis
from collections import deque
import itertools


import config


IMAGE_NAME = "./static/very_good_security.png"
MAX_COOKIE_SIZE = 100


app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'


sess = Session()
sess.init_app(app)
if __name__ == "__main__":
    app.run()


@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'GET':
        return initiate_page()
    if request.method == 'POST':
        print('Received request')
        return prepare_pixel_payload()


def initiate_page():
    # Download the image and get an RGB pixel array
    # Convert the image to a 2-dimentional array of pixel RGB values
    image_pixel_array = np.array(Image.open(IMAGE_NAME))
    width_pixels = range(image_pixel_array.shape[0])
    height_pixels = range(image_pixel_array.shape[1])

    progress_pixel_array = np.zeros([len(width_pixels),len(height_pixels)], dtype=int)
    
    # unsent_pixels_index = list(itertools.product(width_pixels, height_pixels))
    # random.shuffle(unsent_pixels_index)
    # for row in width_pixels:
    #     random_pixel_row = list(itertools.product([row], height_pixels))
    #     random.shuffle(random_pixel_row)
    #     session['row_'+str(row)] = random_pixel_row
    # session['unsent_pixels_index'] = unsent_pixels_index
    
    session['current_row'] = 0
    session['progress'] = progress_pixel_array
    response = make_response(render_template('index.html'))
    response.set_cookie('image-width', str(len(width_pixels)))
    response.set_cookie('image-height', str(len(height_pixels)))
    return response


def prepare_pixel_payload():
    response = make_response()
    response.set_cookie('pixels', get_pixel_string())
    return response


def get_pixel_string():
    # Find available pixels and compress them into a string that can be saved in a cookie
    pixel_string = ''
    image_width = int(request.cookies['image-width'])
    image_height = int(request.cookies['image-height'])
    pixel_row = session['current_row'] if session['current_row'] != image_width else 0
    progress_row = session['progress'][pixel_row]
    image_pixel_array = np.array(Image.open(IMAGE_NAME))
    while len(pixel_string) < 75:
        pixel_col = random.randint(0, image_height) - 1
        if progress_row[pixel_col] == 1:
            continue
        pixel_index = image_width * pixel_row * 4 + pixel_col * 4
        pixel_rgb = image_pixel_array[pixel_row, pixel_col]
        pixel = f'{pixel_index}+{pixel_rgb[0]}/{pixel_rgb[1]}/{pixel_rgb[2]} '
        pixel_string = pixel_string + pixel
    session['current_row'] = pixel_row + 1
    return pixel_string

