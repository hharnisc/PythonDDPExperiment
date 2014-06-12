PythonDDPExperiment
===================

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
_The short answer_ SRP

There are implementations for Node that seem to work, however I've had some issues getting all the way through the handshaking process. (It get's all the way to the last step and says it's got invalid credentials). There's most likely some other functionality that Meteor supports, but for now SRP is the big missing item.

## The Product

I'd like to turn DDPClient.py into a package and upload it to <https://pypi.python.org/pypi>. The source will be available on github with an MIT license.

## Getting Started
Clone this repository and install the depencies in requirements.txt

```bash
$ pip install -r requirements.txt
```