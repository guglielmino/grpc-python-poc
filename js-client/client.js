const messages = require('./notification_pb');
const services = require('./notification_grpc_pb');

const grpc = require('grpc');

function main() {
  const serverUrl = `${process.env.GRPC_HOST || 'localhost'}:${process.env.GRPC_PORT || '5001'}`;
  const client = new services.NotificatorServiceClient(
    serverUrl,
    grpc.credentials.createInsecure(),
  );
  let request = new messages.NotificationPayload();
  request.setDestination('Juan');
  request.setMessage('Hello from a JavaScript guy');
  client.sendNotification(request, function (err, response) {
    if (err) { console.log(`Unable to send notification: ${err}`); return }
    const sent = response.toObject().status;
    console.log(sent ? "Notificantion sent" : "Ops!");
  });
}

main();
