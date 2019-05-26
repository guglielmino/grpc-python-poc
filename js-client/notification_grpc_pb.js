// GENERATED CODE -- DO NOT EDIT!

'use strict';
var grpc = require('grpc');
var notification_pb = require('./notification_pb.js');
var common_pb = require('./common_pb.js');

function serialize_Result(arg) {
  if (!(arg instanceof common_pb.Result)) {
    throw new Error('Expected argument of type Result');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_Result(buffer_arg) {
  return common_pb.Result.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_notificator_NotificationPayload(arg) {
  if (!(arg instanceof notification_pb.NotificationPayload)) {
    throw new Error('Expected argument of type notificator.NotificationPayload');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_notificator_NotificationPayload(buffer_arg) {
  return notification_pb.NotificationPayload.deserializeBinary(new Uint8Array(buffer_arg));
}


var NotificatorServiceService = exports.NotificatorServiceService = {
  sendNotification: {
    path: '/notificator.NotificatorService/SendNotification',
    requestStream: false,
    responseStream: false,
    requestType: notification_pb.NotificationPayload,
    responseType: common_pb.Result,
    requestSerialize: serialize_notificator_NotificationPayload,
    requestDeserialize: deserialize_notificator_NotificationPayload,
    responseSerialize: serialize_Result,
    responseDeserialize: deserialize_Result,
  },
};

exports.NotificatorServiceClient = grpc.makeGenericClientConstructor(NotificatorServiceService);
