#!/bin/bash

rm -rf ./output.ankiaddon
cd src && zip -r ../output.ankiaddon . -x "*.pyc" -x "*/__pycache__" -x "meta.json"
