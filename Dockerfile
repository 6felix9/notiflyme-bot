# Use official Python 3.11 image
FROM python:3.11

# Set working directory inside the container
WORKDIR /app

# Copy all project files into the container
COPY . .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Default command (optional – overridden by docker-compose)
CMD ["python", "bot.py"]
