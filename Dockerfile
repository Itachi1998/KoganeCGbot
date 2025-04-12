# Use the Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /kogane

# Copy the requirements file into the container
COPY requirements.txt ./ 
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Install system dependencies required for psycopg2
RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*


# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Define the command to run the application
CMD ["entrypoint.sh"]
