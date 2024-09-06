# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Expose the port that the app will run on
EXPOSE 8000

# Define the command to run the application
CMD ["gunicorn", "payment_api_service.wsgi:application", "--bind", "0.0.0.0:8000"]
