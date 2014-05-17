xcp-gui
=======
# Description
A platform-independent, Qt-based python GUI for the XCP currency and exchange.
The intention of this app is to provided a standalone bundle that automatically takes care of running counterpartyd
in the background, much like Bitcoin's own Bitcoin-qt app. On startup, the app takes care of making sure that the
following prerequisites are satisifed, and if not alerts the user of this problem before quitting gracefully. In order,
these are:

1. Make sure bitcoind is up and running
2. Verify bitcoind has an up to date blockchain, and if not it will wait until it does
3. Starts ```counterpartyd```
4. Makes sure the counterparty db is up to date
5. Starts the app

# Dependencies
To run, the project has the following dependencies:
* [Python 3](http://python.org)
* [sip==4.15.4](http://www.riverbankcomputing.com/software/sip/download)
* [PyQt4==4.8](http://www.riverbankcomputing.com/software/pyqt/download)
* [bitcoin-rpc](https://github.com/jgarzik/python-bitcoinrpc)
* Bitcoind

If possible, the project will look for PyQt5 to be installed, and then fallback to PyQt4 if needed, as is the case for
Windows 7.

In addition, since the project bundles in [counterpartyd](https://github.com/PhantomPhreak/counterpartyd) within the
app, and the repo itself has added it as a submodule, the dependencies for counterpartyd are needed as well and
are reproduced below.
* Python 3 packages: apsw, requests, appdirs, prettytable, python-dateutil, json-rpc, cherrypy, pycoin, pyzmq(v2.2+) (see [this link](https://github.com/xnova/counterpartyd_build/blob/master/dist/reqs.txt) for exact working versions)

To initialize the counterpartyd submodule once cloned run this from within the git directory:
```git submodule init``` followed by ```git submodule update --recursive```

# Usage
To run the program, simply run `python gui.py` from the command line. The usage is the same as the usage for the
`counterpartyd.py` script, with a few exceptions.


For example, a simple command setting the appropriate RPC usernames and passwords is:

```python gui.py --rpc-user=rpcuser --rpc-password=rpcpassword --bitcoind-rpc-password=PASSWORD --testnet```

* Since the app is responsible for both the GUI and and the counterpartyd server, the RPC password is no longer required in configuration,
and the GUI will automatically choose one to give to both the server and the GUI.
* There is one additional configuration parameter, ``--no-counterpartyd``, that allows the GUI to be run without also
starting the counterpartyd server. In this case, the GUI relies on a server that is already running to connect to.

# Installation
The project also is meant to be built as a standalone application (akin to Bitcoin-Qt). To freeze the application,
the project relies on [py2app](https://pypi.python.org/pypi/py2app/).

If installed correctly, the package can be compiled to an executable with `python setup.py py2app` on any architecture
with all the above dependencies installed. The freezing process has not been tested so far, and there are expected to be
problems, but this demonstrates a proof of concept of the cross-platform nature of this project.
