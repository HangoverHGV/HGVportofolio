FROM python:3.9-slim

# Install the required dependencies
RUN apt update && apt install -y libgl1-mesa-dev libglib2.0-0
# Update pip
RUN /usr/local/bin/python -m pip install --upgrade pip

# Copy requirements.txt file and install the requirements
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copy the code
WORKDIR /workdir
COPY . /workdir

# Clean up the image
RUN apt-get clean && apt-get autoclean && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["python"]
CMD ["main.py"]
