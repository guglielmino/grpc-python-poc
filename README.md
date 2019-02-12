# Refactor to Microservices with gRPC

![The Monolith](https://blogs.egu.eu/network/geosphere/2012/10/24/geology-photo-of-the-week-9-oct-21-27/network/geosphere/files/2012/10/IMG_2360-1024x768.jpg)

## Description

In a perfect world you create project from scratch, you choose the architectural approach and tools that fits better for what you want to accomplish. Since we're not in a perfect world, more often than not, we need to work on legacy code. In my career this happened a lot of times and for sure I'm not alone, indeed this approach was worth to write a famous [book](https://martinfowler.com/books/refactoring.html) entirely dedicated to it.

The PoC here presented is to validate the progressive porting of a monolithic application, made in Django 1.8 running on Python 2.7, to a microservices architecture.
Microservice is an abused term, a buzzword if you like, but there are a lot of benefits if adopted with pragmatism. For example migrating the "monolith" code base from Python 2.7 to Python 3.x could be a pain. Instead, splitting the project in small components (or services), and let them communicate each other, can be a lot simpler, divide et impera folks!. The foundation to split a project in this way is to define an efficient service to service communication protocol. It must be simple, fast, scalable and battle tested,the name for that thing is RPC system (Remote Procedure Call). Here is where gRPC comes into the picture.

## RPC

Remote Procedure Call is a quite old idea, since the very first computer's networks started to spread, some RPC system was implemented. RPC is based on a request/response pattern, there are many RPC systems all around, often implemented in very different ways, even though the idea is always the same: a process A makes a request to a process B which can respond something to A. Those processes can run in the same host or in different ones, assumed that they are able to communicate each other through the network. This is a simplified view but from the logical standpoint it solves the requirement, of course there is a lot more to take in consideration to chose the right RPC, specifically:

- Performing
- Open standard
- Security
- Language agnostic

Last point is a nice to have, but it opens some good opportunities like implementing part of the system with languages more suitable for some specific tasks.

## Validate the architectural change

It's a best practice to validate an architectural change creating (at least) a pilot project, a PoC if you prefer. At the same time it's mandatory to clearly define a list of what requirements to validate, in this case they are:

- Should be able to call services implemented in different Python versions (2.x and 3.x)
- Should work in a Docker containers environment
- Should be useful to identify how to organize splitted projects

Normally it's a good idea to keep the list quite short, validating what specifically we need, in this case the specific need is to check how gRPC works with different Python versions inside a docker compose environment.

### gRPC as sercice communication system

gRPC uses [protocol buffer](https://developers.google.com/protocol-buffers/) as a mechanism to serialize data and define the service interfaces. Using a specific language to create the interface it's a quite common approach, in RPC terms it's called [IDL](https://en.wikipedia.org/wiki/Interface_description_language). IDL is tipically a custom language, specifically tailored to design the interface used by the services to communicate each other, focusing on the projects structure if you use an IDL you need at least two thing:

- One or more IDL sources, for the services interfaces
- A way to compile or dinamically load the IDL in the code that need to use it

In simple word the IDL is a contract shared from processes that need to communicate each other, both one-way or two-ways. This is an important point in managing the project structure because you need to get a decision on how to keep the IDL sources shared by the projects using them.

Let's start with an example of the IDL interface we are going to use in the PoC.

```protobuf
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

It could be scary at first look but in fact it's quite simple. The main points here is the service definition, what operations the service wants to expose outside, and messages, how data is structured. Translating the above IDL in plain English, we are defining a `NotificationService` who exposes a single method called `SendNotification`, that method expects to receive a `NotificationPayload` as input and respond with a `Result` as output. `Result` is defined in an external file to test how IDL files can be organized.
An important thing, that immediately shows up, is that there is an extra work to create and maintain those files. This is the core aspect of gRPC, having a strict interface definition, a contract between services, is very important to keep control of the communication between services.

Lastly, IDL file can be loaded at runtime or use some gRPC tools to statically generate code from them. There is no better solutions, it mostly depends on build and deploy infrascructure, in this project we used the latter approach.

## Implementation

It's time to start writing the code, but before it's mandatory to define a project structure. Since my preferred approach is to start as simple as I can, I structured the project folders as below.

```

├── client-2.x
├── protos
│   ├── common.proto
│   └── notification.proto
└── server-3.x
```

Nothing special here, the two folders `client-2.x` and `server-3.x`contain the code of a hypothetical service and it's consumer, I called them client and server to be clear on the roles but keep in mind that in gRPC there is no a role concept, it defines interfaces and how service interact each other isn't something it needs to know. The intersting folder is the `protos`, I put here the IDL sources with the interface definitions. Tthe project consist of a service to send notifications (whathewer it's a push notification, SMS or anything else). Then, service definition defines a method to send the notification, the payload with message body and destination address. Traslated in Protocol Buffer IDL this is equivalent to code for IDL interface of the previous paragraph.

Protocol Buffer's IDL is quite readable, in fact in the code above we are defining a `NotificationService` made of a single method `SendNotification`. This method accepts a `NotificationPayload` as parameter and returns a `Result` as response.

In Protocol Buffer method parameters, and return types, need to be always defined as custom types, in other terms you can't use primitive types, like `string` or `bool` as they are, it's mandatory to define a custom type. The `NotificationPayload`'s definition is shown in the bottom, while `Result` is imported from `common.proto`, this is done on purpose to check how to split `proto` files when types are shared across many services. One cavets in proto files type definition is about the numbers assigned to each property (like `destination = 1` or `message = 2` in the above sample). Those numbers are related to how Protocol Buffer [encodes](https://developers.google.com/protocol-buffers/docs/encoding) data. What is important to know it's that they should be unique in the message definition and, most important, if changed, the encoded data is incompatible with a client using the old numeration.

There are many other details about Protocol Buffer, they are well documented in the [official Protocol Buffer Documentation](https://developers.google.com/protocol-buffers/docs/proto3).

## Installing dependencies

Both projects, `client-2.x` and `server-3-x`, come with a `requitements.txt` file. As a de facto standard in Python with this file it's trivial to install all the project dependencies with `pip install -r requirement.txt`.
Looking inside the requirements file can be interesting to see what the project need, in particular the two core packages are `grpcio` and `grpcio-tools`, those are the gRPC implementation and a tool package that we'll see later is very important.

### Note about the Makefile(s)

You'll notice in the project some makefiles, that's not because I'm a nostalgic C/C++ developer :-). It is because Python lacks a standard way to define scripts, like Node.js does with `scripts` in the `package.json`. I find the `Makefile` a good compromise, instead of creating custom shell script, and so the project dependencies can be installed simply with `make install`, typing simply `make` are listed all the commands provided. Of course, `make` must be present on the system, how to install it's out of scope and OS dependend but there is a HUGE amount of documentation all around about this.

## Calling a service

All right up here, but how we use the IDL to call a service via gRPC? As I wrote before there are two way to use the `proto` file, in this project we generate the code from the IDL. We noticed before that besides the Python gRPC package there is another one called `grpc_tools`. It's hard to guess, but it turns out to be a package providing tools for gRPC. One function provided is the code generation starting from the `proto` file, that's what we are going to use.
Let's start with `client-2.x` project, but it's exactly the same for `server-3.x`, using the make file provided in the project it's matter of running `make build`. Actually the Makefile runs the Python gRPC tools, looking inside one of the Makefile provided inside the client or the server we can see how.

```bash
python -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/common.proto
python -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/notification.proto
```



## Running in Docker

## Containers

The project I want to refactor is already a containerized project, the various architecture components run inside some Docker containers and this is a choice I'm not putting in discussion. Then the refactoring must consider this architecture as a requirement and put in place a solution that fits perfectly within it.
