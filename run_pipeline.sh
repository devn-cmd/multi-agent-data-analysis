#!/bin/bash

# 1. Start Ollama in the background with the correct network host flag
echo "🤖 Starting Ollama service..."
export OLLAMA_HOST=0.0.0.0
ollama serve > /dev/null 2>&1 &
OLLAMA_PID=$!

# Give Ollama a couple of seconds to wake up
sleep 2

# 2. Shut down any old containers and spin up the new build
echo "🐳 Building and starting Docker containers..."
docker compose down
docker compose up --build -d

# 3. Wait for FastAPI/Uvicorn to start responding on port 8000
echo "⏳ Waiting for Pipeline API to be ready..."
until $(curl --output /dev/null --silent --head --fail http://localhost:8000/docs); do
    printf '.'
    sleep 1
done
echo -e "\n✅ API is up and running!"

# 4. Trigger your pipeline execution automatically
echo "🚀 Triggering pipeline report..."
curl -X POST http://localhost:8000/trigger/telegram

echo -e "\n\n🎉 Pipeline completed! Streaming live logs now. Press Ctrl+C to exit."
# Show container logs so you see the agent printouts and the Drive upload link
docker compose logs -f