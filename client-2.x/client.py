from __future__ import print_function

import random
import time

import os
import grpc

import notification_pb2
import notification_pb2_grpc
import common_pb2


GRPC_HOST = os.getenv('GRPC_HOST', 'localhost')
GRPC_PORT = os.getenv('GRPC_PORT', '50051')

def send_notification(message):
    print("send_notification")

def run(): 
    
    with grpc.insecure_channel('{0}:{1}'.format(GRPC_HOST, GRPC_PORT)) as channel:
        stub = notification_pb2_grpc.NotificatorServiceStub(channel)
        while True:
           res = stub.SendNotification(
                   notification_pb2.NotificationPayload(destination="Fabrizio", message="Hello!!!")
                   )
           if res:
              print("Notification sent")
           time.sleep(1)

if __name__ == '__main__':
    run()