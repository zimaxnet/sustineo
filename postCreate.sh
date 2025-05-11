#!/bin/bash

# This script is executed after the container is created and started.
# It installs the necessary dependencies for both the API and web applications.

# Install Python dependencies
cd api 
pip3 install --break-system-packages -r requirements.txt 

# Install Node.js dependencies
cd .. 
cd web 
npm install