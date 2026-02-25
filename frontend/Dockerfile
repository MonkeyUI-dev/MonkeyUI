# Development Dockerfile for Frontend
FROM node:22-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 5173

# Default command
CMD ["npm", "run", "dev", "--", "--host"]
