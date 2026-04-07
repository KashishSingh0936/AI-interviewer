FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application
COPY . .

# Build for production
RUN npm run build

# Expose port
EXPOSE 3000

# Serve with a simple HTTP server
RUN npm install -g serve
CMD ["serve", "-s", "dist", "-l", "3000"]

