FROM python:2.7.15-slim-stretch

RUN apt-get update && apt-get install -y \
    build-essential

# Note: this requires to use a context set on the parent folder
#        build the contaniner with "docker build -f Dockerfile  .." or from the 
#        docker-compose.yaml 
COPY ./protos/ /usr/src/protos/
COPY ./client-2.x/ /usr/src/app

WORKDIR /usr/src/app

RUN  pip install -r requirements.txt
RUN make build

CMD ["python", "client.py"]
