.PHONY: clean build

default:
	@echo 'Makefile for gRPC Python 3.x server'
	@echo
	@echo 'Usage:'
	@echo
	@echo '    make install    install the packages'
	@echo '    make clean      cleanup IDL generated file'
	@echo '    make build      generate code from IDL'
	@echo

install:
	python -m pip install -r requirements.txt 

clean:
	rm -f notification_pb2*
	rm -f common_pb2*

build:
	python -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/common.proto
	python -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/notification.proto

