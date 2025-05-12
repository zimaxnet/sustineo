.PHONY: setup start stop

# Setup both API and web application
setup:
	@echo "Setting up project..."
	@bash ./scripts/postCreate.sh

# Start both API and web servers
start:
	@bash ./scripts/start.sh

# Stop all running services
stop:
	@bash ./scripts/stop.sh
