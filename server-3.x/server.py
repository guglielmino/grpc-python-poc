""" Sample Python 3.6.6 gRPC server """

from concurrent import futures
import time
import math

import os
import grpc
import json

import notification_pb2
import notification_pb2_grpc
import common_pb2

GRPC_HOST = os.getenv('GRPC_HOST', '[::]')
GRPC_PORT = os.getenv('GRPC_PORT', '50051')

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class NotificatorServiceServicer(notification_pb2_grpc.NotificatorServiceServicer):
    def SendNotification(self,  request, context):
        print("Receiing a request for sendNotification (req = {0})  ".format(request))
        return common_pb2.Result(status=True)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    notification_pb2_grpc.add_NotificatorServiceServicer_to_server(
       NotificatorServiceServicer(), server)
    server.add_insecure_port("{0}:{1}".format(GRPC_HOST, GRPC_PORT))
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()