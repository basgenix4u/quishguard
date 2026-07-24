# === Stage 1: Build ===
FROM node:20-alpine AS builder

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ .
ENV NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
RUN npm run build

# === Stage 2: Runtime ===
FROM node:20-alpine

WORKDIR /app

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

ENV PORT=3000
ENV NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

CMD ["node", "server.js"]
