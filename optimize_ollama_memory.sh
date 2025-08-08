#!/bin/bash
# Ollama Memory Optimization Script for macOS

echo "🔧 Optimizing Ollama Memory Settings for gpt-oss:20b"
echo "=================================================="

# Stop Ollama if running
echo "🛑 Stopping Ollama service..."
pkill -f ollama || true
sleep 3

# Set memory-related environment variables
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_MAX_QUEUE=1
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_FLASH_ATTENTION=1

# For macOS, set memory limits
export OLLAMA_MAX_VRAM=8192  # 8GB VRAM limit
export OLLAMA_HOST=127.0.0.1:11434

echo "📊 Memory optimization settings:"
echo "   - Max loaded models: 1"
echo "   - Max queue: 1"
echo "   - Parallel processing: 1"
echo "   - Flash attention: enabled"
echo "   - VRAM limit: 8GB"

# Start Ollama with optimized settings
echo "🚀 Starting Ollama with optimized settings..."
ollama serve &
OLLAMA_PID=$!

echo "⏳ Waiting for Ollama to start..."
sleep 5

# Check if Ollama is running
if ps -p $OLLAMA_PID > /dev/null; then
    echo "✅ Ollama started successfully with PID: $OLLAMA_PID"
    echo "🔍 Testing model loading..."
    
    # Test model loading with memory constraints
    timeout 30 ollama run gpt-oss:20b "Hello" || echo "⚠️  Model test timed out - may need further optimization"
else
    echo "❌ Failed to start Ollama"
    exit 1
fi

echo "✨ Ollama optimization complete!"
echo "💡 If you still experience memory issues, consider using a smaller model like llama3.1:8b"
