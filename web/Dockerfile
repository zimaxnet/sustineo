FROM node:slim AS development-dependencies-env
COPY . /app
WORKDIR /app
RUN npm install -g npm@11.3.0
RUN npm ci

FROM node:slim AS production-dependencies-env
COPY ./package.json package-lock.json /app/
WORKDIR /app
RUN npm install -g npm@11.3.0
RUN npm ci --omit=dev

FROM node:slim AS build-env
COPY . /app/
COPY --from=development-dependencies-env /app/node_modules /app/node_modules
WORKDIR /app
RUN npm install -g npm@11.3.0
RUN npm run build

FROM node:slim
COPY ./package.json package-lock.json /app/
COPY --from=production-dependencies-env /app/node_modules /app/node_modules
COPY --from=build-env /app/build /app/build
WORKDIR /app
RUN npm install -g npm@11.3.0

# Install a static file server for production
RUN npm install -g serve

# Expose port 80 for the web server
EXPOSE 80

# Start the static file server to serve the build directory
CMD ["serve", "-s", "build", "-l", "80"]