FROM python:3.6.8-stretch

# Note: this requires to use a context set on the parent folder
#        build the contaniner with "docker build -f Dockerfile  .." or from the 
#        docker-compose.yaml 
COPY ./protos/ /usr/src/protos/
COPY ./server-3.x/ /usr/src/app
WORKDIR /usr/src/app

RUN  pip install -r requirements.txt
RUN make build

CMD ["python", "server.py"]
