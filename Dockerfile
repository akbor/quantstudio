FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

#RUN git clone https://github.com/akbor/quantstudio.git .
COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 8505

HEALTHCHECK CMD curl --fail http://localhost:8505/_stcore/health

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8505", "--server.address=0.0.0.0"]