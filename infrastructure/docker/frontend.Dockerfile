# ==========================================
# Stage 1: Base
# ==========================================
FROM node:20-alpine AS base

# Install pnpm
RUN corepack enable && corepack prepare pnpm@8.15.4 --activate

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# ==========================================
# Stage 2: Development
# ==========================================
FROM base AS development

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Set environment
ENV NODE_ENV=development
ENV VITE_ENVIRONMENT=development

# Expose port
EXPOSE 5173

# Development command
CMD ["pnpm", "dev", "--host", "0.0.0.0"]

# ==========================================
# Stage 3: Builder
# ==========================================
FROM base AS builder

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Build application
RUN pnpm build

# ==========================================
# Stage 4: Production
# ==========================================
FROM nginx:alpine AS production

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
