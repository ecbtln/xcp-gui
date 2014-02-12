xcp-gui
=======
# Description
This is the Qt-based python GUI for the XCP currency and exchange that makes use of the RPC's it provides. See https://github.com/PhantomPhreak/counterpartyd.

# Dependencies
To compile and run the project has the following dependencies:
* [Python 3](http://python.org)
* [sip==4.15.4](http://www.riverbankcomputing.com/software/sip/download)
* [PyQt5==5.1](http://www.riverbankcomputing.com/software/pyqt/download5)
* [bitcoin-rpc](https://github.com/jgarzik/python-bitcoinrpc)

# Usage
To run the program, simply run `python main.py` from the command line, optionally specifying `--testnet` to use the default testnet ports.


# Installation
The project also is meant to be built as a standalone application (akin to Bitcoin-Qt). To freeze the application, the project relies on [cx_Freeze](http://cx-freeze.sourceforge.net). And, if installed correctly, the package can be compiled to an executable with `python setup.py build.`
