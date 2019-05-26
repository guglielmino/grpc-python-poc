# Refactoring to Microservices with gRPC

## Introduction

Developer job is hard, often we are litterally exposed to infernal conditions (I have have a tendency to dramatize :-) ). Some time ago it was the [DLL Hell](https://en.wikipedia.org/wiki/DLL_Hell), more recently the [callbacks hell](http://callbackhell.com/), but the one that I fear the most is **THE LEGACY CODE HELL**.

![Legacy code Hell](https://24t9d72kcs873my15o9hr1pu-wpengine.netdna-ssl.com/wp-content/uploads/2014/12/06-programming-coding-is-hell.png)
<sub>credits toggl.com</sub>

In a perfect world you create project from scratch, choosing the architectural patterns and tools that fit for what you want to achieve. Since we're not in a perfect world, more often than not, we need to work on legacy code. In my career this happened a lot of times, and for sure I'm not alone, that's why psychologists earn a lot of money.

## Splitting the Hell

A piece of Hell is better than full Hell, or at least this is how is supposed to be. What I'm going to describe is an approach to split a legacy application in small pieces and try to rule them as an application.

Subject of the article is a monolithic Python 2.7 application. The approach is to create a proof of concept to validate the progressive porting of a monolith codebase to a microservices architecture.
Microservice is an abused term, a buzzword if you like, but it's an interesting architectural pattern with a lot of benefits, if adopted with pragmatism. For example, migrating the "monolith" code base from Python 2.7 to Python 3.x could be a pain. Instead, splitting the project in small components (or services), and let them communicate each other, can be a lot easier, divide et impera folks! The foundation to split a project in this way is to define an efficient way to manage service to service communication. It must be simple, fast, scalable and battle tested, the name for that thing is RPC system (Remote Procedure Call).

## RPC

Remote Procedure Call is a quite old idea, since the very first computer's networks started to spread, some RPC system was implemented. RPC is normally based on a request/response pattern, there are many RPC systems all around, often implemented in very different ways. Even though, the idea is always the same: a process _A_ makes a request to a process _B_ which can respond something to _A_. Those processes can run in the same host or in different ones, assumed that they are able to communicate each other through the network. This is a simplified view but, from a logical standpoint, it solves our requirement. Of, course there is a lot more to take in consideration to choose the right RPC, specifically it should be:

- Resilient
- Performant
- Secure
- Language agnostic

Last point is particular important nowadays, I'm a great opponent of the "silver bullet" approach, that often is "if all you have is a hammer, everything looks like a nail". Having the choice from a wide range of languages, you can discover that some components are better if developed with JavaScript, other in Python and some other in Go, it's powerfull! (and at the same time dangerous if aboused). 

## Validate the architectural change

It's a best practice to validate an architectural approach creating (at least) a pilot project, a PoC if you prefer. At the same time it's mandatory to clearly define a list of requirements to validate, in this case they are:

- Should be able to call services implemented in different Python versions (2.x and 3.x)
- Should be able to call services implemented in different Language, say JavaScript
- Should work in a containers environment

Normally it's better to keep the list quite short, validating what specifically we need. In this case the specific need, in plain English, is to check how gRPC works with different languages inside a containers environment.

### gRPC as service communication system

_gRPC is a modern, open source remote procedure call (RPC) framework that can run anywhere_, that's what you can read from the [official site FAQ](https://grpc.io/faq/). It looks exactly what we are looking for, then it worth to give it a try.

gRPC uses [protocol buffer](https://developers.google.com/protocol-buffers/) as a mechanism to serialize data and define the service interfaces. Using a specific language to create the interface it's a quite common approach, in RPC terms it's called [IDL](https://en.wikipedia.org/wiki/Interface_description_language). Tipically, IDL is a custom description language, specifically tailored to design the interface used in services comminications.
Focusing on the projects structure if you use an IDL you need at least two thing:

- One or more IDL sources, for the services interfaces
- A way to use (compile, or dynamically load) the IDL definitions in your code 

In simple words the IDL is a contract shared between processes that need to communicate each other, both one-way or two-ways. This is an important point in managing the project structure because you need to get a decision on how to keep the IDL sources shared by the projects using them.

## Defining the interface

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

It could be scary at first look but in fact it's quite simple. The main points here is the service definition, what operations the service provides and how data is structured. Translating the above IDL in plain English, we are defining a `NotificationService` exposing a single method called `SendNotification`, that method expects to receive a `NotificationPayload` as input and responds with a `Result` as output. `Result` is defined in an external file to test how IDL files can be organized splitting the code.
An important thing, that immediately shows up, is that there is an extra work to create and maintain those files. This is the core aspect of gRPC, having a strict interface definition, a contract between services, is very important to keep control of the communication between services.

Lastly, IDL files can be loaded at runtime or use gRPC tools to statically generate code from them. There is no ideal solution, it mostly depends on build and deploy infrascructure, in this project I used the latter approach.

## Implementation

It's time to start writing the code, but first it's mandatory to define a project structure. Since my preferred approach is to start as simple as I can, I created the project folders as below.

```

├── client-2.x
├── protos
│   ├── common.proto
│   └── notification.proto
└── server-3.x
```

Nothing special here, the two folders `client-2.x` and `server-3.x`contain the code of a hypothetical service and his consumer, I called them client and server to be clear on the roles but keep in mind that in gRPC there is no a role concept, it defines interfaces and how service interact each other isn't something it needs to know. The intersting folder is the `protos`, I put here the IDL sources with the interface definitions. The project consist of a service to send notifications (whathewer it's a push notification, SMS or anything else). Then, service definition defines a method to send the notification, the payload with message body and destination address. Traslated in Protocol Buffer IDL this is equivalent to code for IDL interface in the previous paragraph.

In Protocol Buffer method parameters, and return types, need to be always defined as custom types, in other terms you can't use primitive types, like `string` or `bool` as they are, it's mandatory to define a custom type. 
In our case `NotificationPayload`'s definition is shown in the bottom, while `Result` is imported from `common.proto`. One cavets in proto files type definition is about the numbers assigned to each property (like `destination = 1` or `message = 2` in the above sample). Those numbers are related to how [Protocol Buffer encoding](https://developers.google.com/protocol-buffers/docs/encoding) works. What it's important to know is that they must be unique in the message definition and, most important, if changed the encoded data is incompatible with a client using the old numeration.

There are many other details about Protocol Buffer, they are well documented in the [official Protocol Buffer Documentation](https://developers.google.com/protocol-buffers/docs/proto3).


## Installing dependencies

Both projects, `client-2.x` and `server-3-x`, come with a `requirements.txt` file. As a de facto standard, having this file it's trivial to install all the project dependencies with `pip install -r requirement.txt`.
Looking inside the requirements file can be interesting to see what the project needs, in particular the two core packages are `grpcio` and `grpcio-tools`, those are the gRPC implementation and a tool packages, core packages to use gRPC.

### Note about the Makefile(s)

You'll notice in the project some Makefiles, that's not because I'm a nostalgic C/C++ developer :-). It is because Python lacks a standard way to define scripts, like Node.js does with `scripts` in the `package.json`. I find the `Makefile` a good compromise, instead of creating custom shell script, so the project dependencies can be installed  with `make install`, typing simply `make` are listed all the commands provided. Of course, `make` must be present on the system, how to install it is out of scope and OS dependend but there is a HUGE amount of documentation all around about this.

## Calling a service

All right up here, but how we use the IDL to call a service via gRPC? As I wrote before there are two way to use the `proto` files, in this project we generate the code from the IDL. We noticed before that besides the Python gRPC package there is another one called `grpc_tools`. It's hard to guess, but it turns out to be a package providing tools for gRPC. One function provided is the code generation starting from the `proto` file, that's what we are going to use.
Let's start with `client-2.x` project, it's exactly the same for `server-3.x`, using the make file provided in the project it's matter of running `make build`. Actually the Makefile runs the Python gRPC tools, looking inside one of the Makefile provided inside the client or the server we can see how.

```bash
python -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/common.proto
python -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/notification.proto
```

Running the above commands will produce some new Python source files. These files are Python translation of service and the payloads defined in `proto` file. The thing to notice is that for each `proto` file are created two files. By convention these files have the same `proto`'s name and a postfix, one is `_pb2.py` and the other one is `_pb2_grpc.py`. Quite simply, the former is where data structures are defined, like `NotificationPayload`, the latter is where service stubs are.
Let's start from the client, calling the `NotificationService` is as simple as the following code.

```python
    with grpc.insecure_channel('{0}:{1}'.format(GRPC_HOST, GRPC_PORT)) as channel:
        stub = notification_pb2_grpc.NotificatorServiceStub(channel)
        stub.SendNotification(
                   notification_pb2.NotificationPayload(destination="Fabrizio", message="Hello!!!")
                   )
```

It's simple, isn't it? It's matter of creating a gRPC channel, instanciate the stub and calling our `SendNotification` on the stub as it was defined somewhere in our project, if you are familiar with design pattern it's a proxy. The `insecure_channel` it's to take a part the overhead of the security, gRPC address security seriously but to keep code readble I choose to bypass this part (anyway, it's well documented on the [official site](https://grpc.io/docs/guides/auth.html)).

One important note about the environment: I wrote that one requirement for the PoC is to test service communication between different Python versions. If you want to test the project without Docker (below more information about it) you need to use Python 2.7 for the client and Pythion 3.6 for the server, on the same machine. This can be done with `virtualenv`, a quick introduction to it can be found [here](https://blog.dbrgn.ch/2012/9/18/virtualenv-quickstart/), anyway if you prefer the "let me see how it works as soon as possibile" approach, read the "Running in Docker" paragraph below.

## Creating the service

At this point we have almost everything, we definded the IDL, developed the client but we miss the main dish: the service! 
I left the service implementation after the client on purpose, having already defined the IDL and the client it should be clear what we need from it. The important point to focus on is that we need somewhere in the code the implementation of the service we want to make available throught gRPC, below our super-mega-cool `NotificationService`.

```python
class NotificatorServiceServicer(notification_pb2_grpc.NotificatorServiceServicer):
    def SendNotification(self,  request, context):
        logging.debug(f"handling notification message '{request.message}' to {request.destination})  ")
        return common_pb2.Result(status=True)
```

It is immediately clear that we are implementing here the interface defined in our IDL, base class `notification_pb2_grpc.NotificatorServiceServicer` payload and result are the ones desinged in the IDL.
The implementation is trivial: we use `message` and `destination` coming from request, which is `NotificationPayload`, to log a message, responding with a `Result` wrapping a success status `status=True`.

Defining the service is not enough to make it available to client, we need a way to expose the service over the network, four line of code are all what we need for that.

```python
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
notification_pb2_grpc.add_NotificatorServiceServicer_to_server(
    NotificatorServiceServicer(), server)
server.add_insecure_port(f"0.0.0.0:5001")
server.start()
```

Shortly, we create a gRPC server instance, bound our service to it, define the port on which listening for requests and ran the server. Under the hood a lot of stuff is happeng but for now let us content ourselves with this.

At this point running the server in a `virtualenv` with Python 3.6 and the client in another one with Python 2.7 they should start calling each others, the full source code is available [here](https://github.com/guglielmino/grpc-python-poc)

## What about using other languages ?

I didn't forget one of the most important point to check with the PoC, testing the interoperability with other languages. Now, that we got a bit of confidence with gRPC and how it works, it's time to introduce a new client. This one uses JavaScript, working exactly in the same way of the Python 2.x one. Of course, there are gRPC bindings for almost any language (C, C++, Java, C#, ...) but I choose to use JavaScript because nowedays it is one of the most widespread laguages.
In the previous project strutture I lied, I omitted the JavaScript client, the real project structure is the one below.

```


├── client-2.x
├── js-client     <<<=== You are here!!!
├── protos
│   ├── common.proto
│   └── notification.proto
└── server-3.x
```

Obviously, the JavaScript client is intended to have the same behaviour of the Python one, if you are confident with the Node.js environment you know that the first step is to install dependencies (aka node modules).

```
npm intall
```

With all the modules in place we need to generate the gRPC proxy code, from the proto files, as we did in for the Python version. As usual in Node.js environment there is a script defined in `package.json` for that

```
npm run build
```

That's a shortcut but "under the hood" the command is quite similar to the one used for the Python client.

```
grpc_tools_node_protoc --js_out=import_style=commonjs,binary:. --grpc_out=. --plugin=protoc-gen-grpc=node_modules/grpc-tools/bin/grpc_node_plugin -I ../protos/ common.proto && grpc_tools_node_protoc --js_out=import_style=commonjs,binary:. --grpc_out=. --plugin=protoc-gen-grpc=node_modules/grpc-tools/bin/grpc_node_plugin -I ../protos/ notification.proto
```

In short, I used the `protoc` (aka the protobuf IDL compiler) specific for Node.js, this command creates four files, in the same way I did with  the `protoc` invoked with Python above


## Running in Docker

### Containers

If you followed all the article instructions at this point you are able to run everything locally, but since one of my requirements was to test the project inside a containers environment, the project contains Dockerfile(s) and docker-compose definition. Again, installation of Docker is out of scope (I feel like the skydivers lifesaver inventor joke (*) )

### Running locally with docker compose

Assuming that Docker environment is configured in the machine, running the project is matter of running `docker-compose up` in the root folder. After a while the console will be flooded by messages from both server and client.

![running docker compose](grpc_docker_compose.gif)

Each iteration three messages are printed on the standard ouput.

```bash
client_1  | DEBUG:root:Client: sending notification calling gRPC server
server_1  | DEBUG:root:handling notification message 'Hello!!!' to Fabrizio)  
client_1  | DEBUG:root:Client: notification sent
```

## Conclusion

We scratched just the tip of the iceberg, gRPC is quite complex and I have overlooked a lot of details. If at this point is clear how gRPC can help in splitting architectures in components, I achived my main goal. To 


**(*) skydivers lifesaver inventor joke**

An inventor went to the patent office saying: "I invented a hook to save life of skydivers and I want to patent it". 

*Employee* said: "Well, tell me how it works"

*Inventor*: "Simple, if the parachute doesn't open the skydiver can use the hook to save his life" 

*Employee*: "Ok, fine but where the skydiver is supposed to hook?" 

*Inventor*: "Hey, I can't just make up all the stuff by myself!"