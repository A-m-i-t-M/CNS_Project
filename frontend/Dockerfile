# Step 1: Build the React app
FROM node:16-slim as build

# Set the working directory for the React app
WORKDIR /app

# Copy the package.json and package-lock.json
COPY package*.json ./

# Install the dependencies
RUN npm install

# Copy the rest of the app's files
COPY . .

# Build the app
RUN npm run build

# Step 2: Serve the React app using Nginx
FROM nginx:alpine

# Copy the build files from the previous stage
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80 to access the React app
EXPOSE 80

# Command to start Nginx (default behavior)
CMD ["nginx", "-g", "daemon off;"]
