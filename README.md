# Refactor to Microservices with gRPC

## Description

In a perfect world you create project from scratch, you choose the architectural approach and tools that fits better for what you want to accomplish. Since we're not in a perfect world and, more often than not, you need to work on legacy code. In my career this happened a lot of times and, for sure, I'm not alone, indeed this approach was worth to write a [book](https://martinfowler.com/books/refactoring.html) entirely dedicated to it.

The PoC here presented is to validate the progressive porting of a [monolithic application](https://github.com/guglielmino/pushetta-api-django), made in Django 1.8 running on Python 2.7, to a microservices architecture.
Microservice is nowadays an abused term, or a buzzword if you like it, but there are a lot of benefits in it, if adopted with pragmatism. For example I would like to migrate the code base from Python 2.7 to Python 3.x, doing this on the current "monoliths" could be a pain. Instead, splitting the project in small components (or services), and let them communicate each other, can be a lot simpler. To do this you need a way to make the service to service communication efficient, simple, fast, scalable and battle tested, in other words a good RPC system (remote procedure calls). Here is where gRPC comes into the picture.

## Why gRPC

Remote Procedure Call is a quite old idea, since the very first computer's networks started to spread, some RPC system was implemented. RPC is based on a request/response pattern, there are many RPC systems all around, and they often work in very different ways, even though the idea is always the same: a process A makes a request to a process B which can respond something to A. Those processes can run in the same host or in different ones, given that they are able to communicate each other through the network. Of course this is a simplified view of a RPC system,

## Validate the architectural change

I use to validate my architectural ideas creating a pilot project, a PoC if you prefer. Before starting writing the code I do a list of what I want to validate, in this case it is:

- Call from/to services implemented in different Pyuthon versions (2.x and 3.x)
- Work in a docker compose defined environment
- Best way to split the monolith in multiple project, how to organize them

Normally I keep the list quite short, the idea is to validate what specifically I need, in this case my specific need is to check ho gRPC works with different Python versions inside a docker compose environment.
gRPC uses [protocol buffer](https://developers.google.com/protocol-buffers/) as a mechanism to serialize data and define the service interfaces. Using a specific language to create the interface it's a quite common approach in RPC systems called [IDL](https://en.wikipedia.org/wiki/Interface_description_language). IDL is normally a custom language specifically tailored to design the interface used by the services to communicate each other, focusing on the projects structure if you have an IDL you need at least two thing:

- One or more IDL sources, for the services interfaces, written in IDL
- A way to compile or dinamically load the IDL in the code that need to use it

In simple word the IDL is a contract shared from processes that need to communicate each other, both one-way or two-ways. This is an important point in managing the project structure because you need to get a decision on how to keep the IDL sources shared by the projects using them.

## Implementation

It's time to start writing the code but before it's mandatory to define a project structure, since my preferred approach is to start as simple as I can I structured the project folders as below.

```

├── client-2.x
├── protos
│   ├── common.proto
│   └── notification.proto
└── server-3.x
```

Nothing special here, the two folders `client-2.x` and `server-3.x`contain the code of a hypothetical service and it's consumer, I called them client and server to be clear on the roles but keep in minf that in gRPC there is no a role concept, it defines interfaces and how service interact each other isn't something it needs to know. The intersting folder is the `protos`, I put here the IDL sources with the interface definitions. The idea is to create a service to send notifications (whathewer it's a push notificatio, SMS or anything else), then the service must expose a method to send the notification which require the payload and the destination address, in the Protocol Buffer IDL this is equivalent to the following code.

```
syntax = "proto3";

import "common.proto";

package notificator;

service NotificatorService {
    rpc SendNotification(NotificationPayload) returns (Result) {}
}

message NotificationPayload {
    string destination  = 1;
    string message = 2;

}
```

Protocol Buffer's IDL is quite readable, in fact in the code above we are defining a `NotificationService` made of a single method `SendNotification`. This method accepts a `NotificationPayload` as parameter and returns a `Result` as response.
In Protocol Buffer method parameters, and return types, need to be always defined as custom types, in other terms you can't use primitive types, like `string` or `bool` as they are, it's mandatory to define a custom type. The `NotificationPayload`'s definition is shown in the bottom, while `Result` is imported from `common.proto`, this is done on purpose to check how to organize `proto` files when types are shared across many services. One cavets in proto files type definition is about the numbers assigned to each property (like `destination = 1` or `message = 2` in the above sample). Those numbers are related to how Protocol Buffer [encodes](https://developers.google.com/protocol-buffers/docs/encoding) data. What is important to know it's that they should be unique in the message definition and, most important, if changed the encoded data is incompatible with a client using the old numeration.

There are many other details about Protocol Buffer, they are well documented in the [official Protocol Buffer Documentation](https://developers.google.com/protocol-buffers/docs/proto3).

### Note about the Makefile(s)

You'll notice that inside the client and the server folder there are two Makefile, that's not because I'm a nostalgic on when I was a C developer :-), more like because Python lacks a standard way to define scripts, like Node.js does with `scripts` in the `package.json`. I find the Makefile a good compromise, instead of creating custom shell script, and I'm using this approach

## Containers

The project I want to refactor is already a containerized project, the various architecture components run inside some Docker containers and this is a choice I'm not putting in discussion. Then the refactoring must consider this architecture as a requirement and put in place a solution that fits perfectly within it.
