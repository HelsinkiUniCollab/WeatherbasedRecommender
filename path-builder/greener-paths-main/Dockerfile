FROM python:3.11
WORKDIR /greener_paths
# Python requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt update
COPY utils/ ./utils
COPY activity_definitions.py app.py ./
ENTRYPOINT [ "python", "./app.py" ]
