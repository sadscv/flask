#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from app import create_app, db

app = create_app('default')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)