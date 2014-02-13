xcp-gui
=======
# Description
A platform-independent, Qt-based python GUI for the XCP currency and exchange.
The intention of this app is to provided a standalone bundle that automatically takes care of running counterpartyd
in the background, much like Bitcoin's own Bitcoin-qt app.

# Dependencies
To compile and run, the project has the following dependencies:
* [Python 3](http://python.org)
* [sip==4.15.4](http://www.riverbankcomputing.com/software/sip/download)
* [PyQt5==5.1](http://www.riverbankcomputing.com/software/pyqt/download5)
* [bitcoin-rpc](https://github.com/jgarzik/python-bitcoinrpc)

In addition, since the project bundles in [counterpartyd](https://github.com/PhantomPhreak/counterpartyd) within the
app, the dependencies for counterpartyd are needed as well and are reproduced below.
* Python 3 packages: apsw, requests, appdirs, prettytable, python-dateutil, json-rpc, cherrypy, pycoin, pyzmq(v2.2+) (see [this link](https://github.com/xnova/counterpartyd_build/blob/master/dist/reqs.txt) for exact working versions)
* Bitcoind

# Usage
To run the program, simply run `python gui.py` from the command line. The usage is the same as the usage for the
`counterpartyd.py` script, with a few exceptions.

* Since the app is responsible for both the GUI and and the counterpartyd server, the RPC password is no longer required in configuration,
and the GUI will automatically choose one to give to both the server and the GUI.
* There is one additional configuration parameter, ``--no_web_server``, that allows the GUI to be run without also
starting the counterpartyd server. In this case, the gui relies on a server that is already running to connect to.

# Installation
The project also is meant to be built as a standalone application (akin to Bitcoin-Qt). To freeze the application,
the project relies on [cx_Freeze](http://cx-freeze.sourceforge.net).

If installed correctly, the package can be compiled to an executable with `python setup.py build` on any architecture
with all the above dependencies installed. The freezing process has not been tested so far, and there are expected to be
problems, but this demonstrates a proof of concept of the cross-platform nature of this project.

# GUI
...

