#!/bin/bash

# Create a file to store PIDs
echo "Starting services..."

# Start Python development server and save PID
python ./scripts/start_api.py & 
echo $! > .python.pid

# Start Node.js development server and save PID
cd web
npm run dev &
echo $! > ../.node.pid

echo "Services started. To stop them, run ./stop.sh"