from __future__ import print_function

import logging
import random
import time

import os
import grpc

import notification_pb2
import notification_pb2_grpc
import common_pb2

logging.basicConfig(level=logging.DEBUG)

GRPC_HOST = os.getenv('GRPC_HOST', 'localhost')
GRPC_PORT = os.getenv('GRPC_PORT', '5001')

def run(): 
    
    with grpc.insecure_channel('{0}:{1}'.format(GRPC_HOST, GRPC_PORT)) as channel:
        stub = notification_pb2_grpc.NotificatorServiceStub(channel)
        while True:
           logging.debug("Client: sending notification calling gRPC server")
           res = stub.SendNotification(
                   notification_pb2.NotificationPayload(destination="Fabrizio", message="Hello!!!")
                   )
           if res:
              logging.debug("Client: notification sent")
           time.sleep(3)

if __name__ == '__main__':
    run()