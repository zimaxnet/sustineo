#!/bin/bash

# # Check if .venv exists, if not create it
# if [[ ! -d ".venv" ]]; then
#   echo "Creating Python virtual environment..."
#   python3 -m venv .venv
# else
#   echo "Python virtual environment already exists."
# fi

# echo "Activating Python virtual environment..."
# source .venv/bin/activate

# echo "Installing Python dependencies..."
# cd api
# pip install -r requirements.txt
# cd ..

# # Install Node.js dependencies
# echo "Installing Node.js dependencies..."
# cd web
# npm install
# echo "Done!"

echo "Starting Node.js development server..."
npm run dev
