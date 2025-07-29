#!/bin/bash

echo "Installing BackupX dependencies..."

#  Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo
echo "BackupX installed successfully!"
