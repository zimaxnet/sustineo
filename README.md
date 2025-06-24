This is the website for Evently.

## About BuildEvents by Contoso
BuildEvents by Contoso is a website that allows people to capture ideas about events they go to and things that they enjoy, then add some agentic features to that website, support voice input and support them as they build their own event.

## Roles and Responsibilities
These are the experts on the evently team where issues should be assigned to for triaging
 - Showing how GitHub Copilot's agentic feature can help speed up development: @jldeen
 - Migrating legacy Java code @jldeen
 - Show how to take advantage of the latest models @sethjuarez
 - Build with LLMs locally to add my own Agentic Features to my BuildEvents app @martinwoodward

## Setting up your Dev Environment
This project uses Visual Studio Code Dev Containers for a consistent development environment. The dev container comes pre-configured with:
- Python3 and pip
- Node.js and npm
- Required VS Code extensions
- All necessary development tools
- Add the configuration for the GitHub MCP server and the Figma MCP server
- You will need to create a GitHub token for the GitHub MCP as well as an API key for the Figma MCP Server *todo* - add instructions with links

### Getting Started
1. Install the [Remote Development](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack) extension pack in VS Code
2. Clone this repository
3. Open the project in VS Code
4. When prompted, click "Reopen in Container" or run the "Remote-Containers: Reopen in Container" command
5. The container will build and set up your development environment automatically, running the setup scripts and starting the services
6. **Note** This project can also be run in GitHub Codespaces

### Development Lifecycle
The dev container automatically handles the complete setup and startup process for you:
- When the container is built, it runs `./scripts/postCreate.sh` to initialize all dependencies
- When the container starts, it runs `./scripts/start.sh` to launch all services

### Manual Commands (if needed)
While the dev container handles these automatically, you can also run these commands manually if needed:

- `make setup` - Reinitialize the project:
  - Creates Python virtual environment
  - Installs Python dependencies
  - Installs Node.js dependencies

- `make start` - Start the development servers:
  - Python API server (listens on port 8000 with debugger on port 5678)
  - Node.js development server (listens on port 5173)
  
- `make stop` - Stop all running services and clean up processes

These commands are useful if you need to reset your environment or restart services manually.

### Additional Information
- magic function calling mapping for generic local function calls (A)
- figure out backchannel with utility function calls (A+S)*

## Automated Testing and Deployment by Zimax Networks

Zimax Networks is actively managing the testing and deployment of this project using a modern CI/CD pipeline:

- **Continuous Integration & Deployment:**
  - Every push to the `main` branch triggers a GitHub Actions workflow.
  - The workflow builds Docker images for both the API and web frontend.
  - Images are pushed to the Azure Container Registry (`zimax.azurecr.io`).
  - The latest images are deployed to Azure Container Instances (ACI) with public endpoints for both services.

- **Testing:**
  - Automated tests are run as part of the workflow to ensure code quality and reliability.

- **Managed by Zimax Networks:**
  - Zimax Networks oversees the entire process, ensuring rapid iteration, robust testing, and reliable deployment to Azure infrastructure.

For more information or support, contact Zimax Networks.

---

_Deployment triggered by Zimax Networks on $(date)_
