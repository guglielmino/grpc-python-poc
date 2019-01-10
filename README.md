# Refactor to Microservices with gRPC

## Description

In a perfect world you start a new project from scratch, you choose the architectural approach and tools which fits better for what you want to accomplish. Since we're not in a perfect world and, more often than not, you need to work on legacy code. In my career this happened to me a lot of times and, for sure, the case is so common that it worths a [great book](https://martinfowler.com/books/refactoring.html) entirely dedicated to it.

The PoC presented is to validate the progressive porting of a [monolithic application](https://github.com/guglielmino/pushetta-api-django), made in Django 1.8 running on Python 2.7, to a microservices architecture. Microservice is nowadays an abused term, or a buzzword if you like it, but there are some advantages in this kind of design if you adopt it with pragmatism. For example I would like to migrate the code base from Python 2.7 to Python 3.x, doing this on the current "monoliths" could be a pain. Instead splitting the project in small components (or services) and let them communicate each other can be a lot simpler. To do this you need a way to make the intra service communication efficient, simple, fast, scalable and battle tested, in other words a good RPC system (remote procedure calls), and gRPC seems the right tool for this. 

## What's gRPC and why it

Remote Procedure Call is a quite old idea, since the very first computer networks started to spread, some RPCs system were implemented. There are many RPC systems all around, and they often work in very different ways, even though the idea is always the same: let a process A call a procedure in a process B, those processes can run in the same host or in different ones, given that they are able to communicate each other through the network. 

## Project structured 

One of the project goals is to identify the right way to organize multiple projects communicating with gRPC. gRPC uses [protocol buffer](https://developers.google.com/protocol-buffers/) to define the service interface, that's a quite common approach in RPC systems called [IDL](https://en.wikipedia.org/wiki/Interface_description_language). IDL is a custom language specifically tailored to design the interface used by the services to communicate each other, focusing on the projects structure if you have an IDL you need at least two thing:

- One or more sources, for the services interfaces, written in IDL
- A way to compile or dinamically load the IDL in the code that need to use it

A consideration about the firts point is that you need the IDL either in the consumer and in the provider.

```

├── client-2.x
├── protos
│   ├── common.proto
│   └── notification.proto
└── server-3.x
```

### Note about the Makefile(s)

You'll notice that inside the client and the server folder there are two Makefile, that's not because I'm a nostalgic on when I was a C developer :-), more like because Python lacks a standard way to define scripts, like Node.js does with `scripts` in the `package.json`. I find the Makefile a good compromise, instead of creating custom shell script, and I'm using this approach

## Containers

The project I want to refactor is already a containerized project, the various architecture components run inside some Docker containers and this is a choice I'm not putting in discussion. Then the refactoring must consider this architecture as a requirement and put in place a solution that fits perfectly within it. 
