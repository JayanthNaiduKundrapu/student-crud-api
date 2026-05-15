#!/bin/sh

flask db upgrade

python3 run.py