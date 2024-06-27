"""This module contains helper functions for the lab notebook."""

import io
import matplotlib.pyplot as plt 
import numpy as np
import cv2 as cv
from PIL import Image

def get_image_bytes(image): 
    """Converts image to a byte array."""
    byte_arr = io.BytesIO()
    image.save(byte_arr, format="PNG")
    img_byte_arr = byte_arr.getvalue()
    return img_byte_arr 


def get_hist(image, title):
    fig = plt.figure();
    plt.title(f'{title} histogram');
    if image.mode == "RGB":
        plt.plot(image.getchannel(0).histogram(), c='r');
        plt.plot(image.getchannel(1).histogram(), c='g');
        plt.plot(image.getchannel(2).histogram(), c='b');
    else: 
        plt.plot(cat.histogram(), c='gray')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png');
    plt.close(fig)
    return buffer.getvalue()    

def segment_image(num_clusters, img):
    # https://docs.opencv.org/3.4/d1/d5c/tutorial_py_kmeans_opencv.html
    features = np.float32(img.reshape((-1, 3)))
    
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    
    ret, label, center = cv.kmeans(
        features, num_clusters, None, criteria, 10, cv.KMEANS_RANDOM_CENTERS
    )
    
    center = np.uint8(center)
    res2 = center[label.flatten()].reshape((img.shape))
    return Image.fromarray(res2)