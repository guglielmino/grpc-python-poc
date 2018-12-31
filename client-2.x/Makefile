.PHONY: clean build

install:
	python -m pip install -r requirements.txt 

clean:
	rm -f notification_pb2*
	rm -f common_pb2*

build:
	python -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/common.proto
	python -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/notification.proto

