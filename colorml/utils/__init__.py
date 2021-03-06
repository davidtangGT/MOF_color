# -*- coding: utf-8 -*-
from __future__ import absolute_import

import contextlib
import os
import shutil
import tempfile


@contextlib.contextmanager
def make_temp_directory():
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


@contextlib.contextmanager
def temp():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    try:
        yield tmp
    finally:
        tmp.close()  # closes the file, so we can right remove it
        os.remove(tmp.name)
