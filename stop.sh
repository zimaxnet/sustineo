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

echo "Services stopped"