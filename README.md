PythonDDPExperiment
===================

So I went ahead and implemented the ddp client (meteor specific bit are in progress) Source can be found here:

<https://github.com/hharnisc/python-ddp>

**Install it with pip**

```bash
$ pip install python-ddp
```

## The Project
The goal is to create a full featured event driven DDP client for python. This was derived from the Meteor unfinished [Python DDP Client](https://github.com/meteor/meteor/tree/devel/examples/unfinished/python-ddp-client) and some of the existing DDP clients for node.

The raw client bits have been kept inside of DDPClient.py and a simple command line client has been implemented to demonstrate the use of the callbacks.

With the introduction of [pyee](https://github.com/jesusabdullah/pyee) you can bind DDP events to functions:

```python
self.ddp_client.on('connected', self.connected)
self.ddp_client.on('socket_closed', self.closed)
self.ddp_client.on('failed', self.failed)
self.ddp_client.on('added', self.added)
self.ddp_client.on('changed', self.changed)
self.ddp_client.on('removed', self.removed)
```

This should make it easy to integrate into just about any project.

## What's missing
_The short answer_ ~~SRP~~ bcrypt

SRP is going away in favor of bcrypt <https://meteor.hackpad.com/SRP-bcrypt-J5mdBojeVfe>

There is a plaintext password login handler, so you can call the `login` method with a `password` option containing the plaintext password: <https://github.com/meteor/meteor/blob/release/0.8.1.3/packages/accounts-password/password_server.js#L134>

Also any DDP features missing mentioned on [meteor-talk list](https://groups.google.com/forum/#!forum/meteor-talk)

## The Product

I'd like to turn DDPClient.py into a package and upload it to <https://pypi.python.org/pypi>. The source will be available on github with an MIT license.

## Getting Started
Clone this repository and install the depencies in requirements.txt

```bash
$ pip install -r requirements.txt
```
