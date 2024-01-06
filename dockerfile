# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose ports 53 (UDP) and 8080 (HTTP)
EXPOSE 53/udp 8080

# Define environment variable
ENV NAME World

# Run the application
CMD ["python", "app.py"]
