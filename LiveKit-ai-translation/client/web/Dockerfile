# Multi-stage build for LiveKit Web Client
# Stage 1: Build the Next.js application
FROM node:18-alpine as build

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY pnpm-lock.yaml ./

# Install pnpm and dependencies
RUN npm install -g pnpm
RUN pnpm install --no-frozen-lockfile

# Copy source code
COPY . .

    # Build the application (skip linting for Docker build)
    RUN SKIP_ENV_VALIDATION=true pnpm build

# Stage 2: Serve with Node.js
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy built app and dependencies
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/package*.json ./
COPY --from=build /app/pnpm-lock.yaml ./

# Install production dependencies
RUN npm install -g pnpm
RUN pnpm install --no-frozen-lockfile --prod

# Expose port 3000
EXPOSE 3000

# Start the Next.js server
CMD ["pnpm", "start"] 