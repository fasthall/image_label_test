#!/bin/bash

# pkgs=venv/lib/python3.6/site-packages/
pkgs=pkgs

rm -f lambda.zip
zip -r9 lambda.zip lambda_function.py gochariots.py cred.json
current_path=$PWD
cd $pkgs
zip -ur $current_path/lambda.zip *
cd $current_path
echo 'lambda_function.lambda_handler'

