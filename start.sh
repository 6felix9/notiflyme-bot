#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting NotiflyMeBot Setup & Run Script...${NC}"

# Function to kill background processes on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down processes...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit
}

# Trap exit signals to ensure cleanup
trap cleanup EXIT INT TERM

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}No .env file found. Copying from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}IMPORTANT: A new .env file has been created.${NC}"
    echo -e "${RED}Please edit .env and add your API keys before running the bot.${NC}"
    echo -e "${RED}Press Enter to continue anyway (bot might fail) or Ctrl+C to abort and edit the file.${NC}"
    read
fi

# Check for virtual environment
if [ ! -d ".venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv .venv
else
    echo -e "${GREEN}Virtual environment found.${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source .venv/bin/activate

# Install dependencies
echo -e "${BLUE}Installing/Updating dependencies...${NC}"
pip install -r requirements.txt

# Start Redis Check
if ! command -v redis-server &> /dev/null; then
    echo -e "${YELLOW}Redis server not found in PATH.${NC}"
    echo -e "${YELLOW}Assuming you have a running Redis instance or will use Docker for it.${NC}"
    # Minimal attempt to use docker for redis if available and running
    if docker info > /dev/null 2>&1; then
        echo -e "${BLUE}Docker is running. Starting Redis container...${NC}"
        docker run --name notiflyme-redis -p 6379:6379 -d redis:7-alpine 2>/dev/null || docker start notiflyme-redis 2>/dev/null
    fi
fi

# Start Mongo Check
if ! command -v mongod &> /dev/null; then
      echo -e "${YELLOW}MongoDB not found in PATH.${NC}"
      # Minimal attempt to use docker for mongo if available and running
      if docker info > /dev/null 2>&1; then
          echo -e "${BLUE}Docker is running. Starting MongoDB container...${NC}"
          docker run --name notiflyme-mongo -p 27017:27017 -d mongo:7 2>/dev/null || docker start notiflyme-mongo 2>/dev/null
      fi
fi


# Start Celery Worker
echo -e "${BLUE}Starting Celery Worker...${NC}"
# Use localhost configuration for local run
export MONGO_URI="mongodb://localhost:27017"
export REDIS_URL="redis://localhost:6379/0"

celery -A celery_worker worker --loglevel=info &

# Start Celery Beat
echo -e "${BLUE}Starting Celery Beat...${NC}"
celery -A celery_worker beat --loglevel=info &

# Start the Bot
echo -e "${GREEN}Starting Telegram Bot...${NC}"
python bot.py

# Wait for all background processes
wait
