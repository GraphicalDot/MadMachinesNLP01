#!/usr/bin/env python

import os

file_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
csv_path = os.path.join(file_path +"/csv_files")
if not os.path.exists(csv_path):
	os.makedirs(csv_path)


