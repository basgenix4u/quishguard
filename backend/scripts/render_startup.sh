#!/bin/bash
# Render Startup Script
# This runs before the application starts on Render.
# It sets up the persistent disk directory structure.

echo "🚀 QuishGuard Render Startup"

# Create directories on persistent disk
mkdir -p /data/uploads
mkdir -p /data/uploads/heatmaps
mkdir -p /data/models_pretrained

# Copy initial model files to persistent disk if they exist
if [ -d "./models_pretrained" ]; then
    cp -n ./models_pretrained/* /data/models_pretrained/ 2>/dev/null || true
fi

echo "✅ Persistent disk directories ready"
echo "📁 Upload directory: /data/uploads"
echo "🧠 Model directory: /data/models_pretrained"
