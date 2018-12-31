from __future__ import print_function

import random

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
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('{0}:{1}'.format(GRPC_HOST, GRPC_PORT)) as channel:
        stub = notification_pb2_grpc.NotificatorServiceStub(channel)
        res = stub.SendNotification(notification_pb2.NotificationPayload(destination="user1", message="A notification message"))

        print("Res {0}".format(res))

if __name__ == '__main__':
    run()