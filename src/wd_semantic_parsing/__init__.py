# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from os import environ, path

DATA_DIR = environ.get('DATA_DIR')
if DATA_DIR is None:
    DATA_DIR = path.abspath(path.join(path.dirname(__file__), "..", '..', "data"))
