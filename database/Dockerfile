# Use the official MongoDB image from Docker Hub
FROM mongo

# Create a directory to store MongoDB initialization scripts
RUN mkdir -p /docker-entrypoint-initdb.d

# Copy MongoDB initialization script into the container
COPY init-mongo.js /docker-entrypoint-initdb.d/

# Expose default MongoDB port
EXPOSE 27017
