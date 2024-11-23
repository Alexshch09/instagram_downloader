# Use an official Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy project files
COPY bot.py /app/
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create a directory for persistent SQLite data
RUN mkdir -p /app/data

# Expose the data folder for persistence
VOLUME /app/data

# Run the bot
CMD ["python", "bot.py"]
