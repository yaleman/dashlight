#!/bin/bash

screen rshell -p /dev/cu.usbmodem0000000000001 --buffer-size 512 cp dashlight.py /pyboard/main.py
