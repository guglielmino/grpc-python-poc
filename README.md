# Refactor to Microservices with gRPC

## Description

In a perfect world you start a new project from scratch and you can use the last architectural approach and tools making with the best practice you know at the time. But we're not in a perfect world and, more often than not, you need to work on legacy code. In my career this happened to me a lot of times and, for sure, the case is so common that it worths a [glourious book](https://martinfowler.com/books/refactoring.html) entirely dedicated to it.

The PoC here presented is to validate the progressive porting of a [monolithic application](https://github.com/guglielmino/pushetta-api-django) made in Django 1.8 running on Python 2.7 to a microservices
architecture. Said this the client is developed to run in a Python 2.7 while the server is based on Python 3.x.

## Project structure

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

The project I started from it's already a containerized project, the various architecture components run inside a Docker containers and this is a choice I'm not putting in discussion. Then the refactoring must consider this architecture as a goal
