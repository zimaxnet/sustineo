#!/bin/bash

echo "Stopping services..."

# Kill Python server
if [ -f .python.pid ]; then
    kill $(cat .python.pid) 2>/dev/null || true
    rm .python.pid
fi

# Kill Node server
if [ -f .node.pid ]; then
    kill $(cat .node.pid) 2>/dev/null || true
    rm .node.pid
fi

# Kill any other processes that might be running
kill $(lsof -t -i:5173)
kill $(lsof -t -i:8000)
kill $(lsof -t -i:5678)

# Optionally, you can add a command to stop any other services you might have started

echo "Services stopped"