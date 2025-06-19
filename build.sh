#!/bin/bash

rm -rf ./output.ankiaddon
zip -r ./output.ankiaddon ./src/* -x "*.pyc" -x "__pycache__/*" -x ".git/*" -x ".gitignore" -x ".meta.json"
