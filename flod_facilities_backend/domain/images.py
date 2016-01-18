#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from flask import current_app, request, abort, safe_join, send_file
from PIL import Image


def get_thumbnail_filename(filename, size):
    """Get filename for thumbnail"""
    root, ext = os.path.splitext(os.path.basename(filename))
    return '{0}_{1}x{2}{3}'.format(root, size[0], size[1], ext)


def create_thumbnail(image_path, thumb_path, size):
    """Create a thumbnail of image using the given size. Returns the path
    to the created thumbnail. If requested size exceeds original dimensions,
    the path of the original image is returned."""

    image = Image.open(image_path)

    # Do not create thumbnail if x or y exceeds original dimensions
    x, y = size
    if x >= image.size[0] or y >= image.size[1]:
        current_app.logger.debug(('Not creating thumbnail for %s: Requested '
                                  'dimensions%s exceeds %s'), image_path,
                                 size, image.size)
        return image_path

    # Create thumbnail
    image.thumbnail(size, Image.ANTIALIAS)
    image.save(thumb_path)
    return thumb_path


def get_thumbnail(image_path, size):
    """Get (and create if necessary) a thumbnail for the given image.
    Returns the path and filename to the resulting thumbnail.
    """
    thumbs_path = os.environ.get('IMAGES_CACHE_PATH', '/tmp')
    thumb_filename = get_thumbnail_filename(image_path, size)
    thumb_path = safe_join(thumbs_path, thumb_filename)

    if os.path.exists(thumb_path):
        return thumb_path

    current_app.logger.debug('Resizing image %s to %s', image_path, size)
    return create_thumbnail(image_path, thumb_path, size)


def is_thumbnail(filename, thumb_file):
    """Returns true if thumb_file is a thumbnail for filename"""
    root, ext = os.path.splitext(filename)
    pattern = r'^{root}_\d+x\d+{ext}$'.format(root=root, ext=ext)
    return re.match(pattern, thumb_file) is not None


def find_thumbnails(filename):
    """Find thumbnails given a image filename"""
    thumb_path = os.environ.get('IMAGES_CACHE_PATH', '/tmp')
    return [os.path.join(thumb_path, f) for f in os.listdir(thumb_path)
            if is_thumbnail(filename, f)]


def remove_thumbnails(filename):
    """Remove (delete) all thumbnails for the given image filename"""
    for thumb_file in find_thumbnails(filename):
        os.remove(thumb_file)


def images(filename):
    images_path = os.environ.get('IMAGES_PATH', '/tmp')
    image_path = safe_join(images_path, filename)
    if not os.path.exists(image_path):
        abort(404)

    width = request.args.get('width', None, type=int)
    height = request.args.get('height', None, type=int)
    size = (width, height)
    if None in size:
        return send_file(image_path)

    return send_file(get_thumbnail(image_path, size))
