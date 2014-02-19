import sys
import argparse
from gui.main_window import MainWindow
from application import XCPApplication
from gui.startup_view import XCPSplashScreen
import counterpartyd.lib.config as config
import threading
from rpcclient.xcp_client import XCPClient
from constants import GUI_VERSION
import appdirs
import configparser
import os
import exceptions
import time
from startup import verify_app_pre_reqs


def set_options (data_dir=None, bitcoind_rpc_connect=None, bitcoind_rpc_port=None,
                 bitcoind_rpc_user=None, bitcoind_rpc_password=None, rpc_host=None, rpc_port=None,
                 rpc_user=None, rpc_password=None, log_file=None, database_file=None, testnet=False, testcoin=False, unittest=False, headless=False, start_server=False):

    # Unittests always run on testnet.
    if unittest and not testnet:
        raise Exception # TODO

    # Data directory
    if not data_dir:
        config.DATA_DIR = appdirs.user_data_dir(appauthor='Counterparty', appname='counterpartyd', roaming=True)
    else:
        config.DATA_DIR = data_dir
    if not os.path.isdir(config.DATA_DIR): os.mkdir(config.DATA_DIR)

    # Configuration file
    configfile = configparser.ConfigParser()
    config_path = os.path.join(config.DATA_DIR, 'counterpartyd.conf')
    configfile.read(config_path)
    has_config = 'Default' in configfile
    #logging.debug("Config file: %s; Exists: %s" % (config_path, "Yes" if has_config else "No"))

    # testnet
    if testnet:
        config.TESTNET = testnet
    elif has_config and 'testnet' in configfile['Default']:
        config.TESTNET = configfile['Default'].getboolean('testnet')
    else:
        config.TESTNET = False

    # testcoin
    if testcoin:
        config.TESTCOIN = testcoin
    elif has_config and 'testcoin' in configfile['Default']:
        config.TESTCOIN = configfile['Default'].getboolean('testcoin')
    else:
        config.TESTCOIN = False

    # Bitcoind RPC host
    if bitcoind_rpc_connect:
        config.BITCOIND_RPC_CONNECT = bitcoind_rpc_connect
    elif has_config and 'bitcoind-rpc-connect' in configfile['Default'] and configfile['Default']['bitcoind-rpc-connect']:
        config.BITCOIND_RPC_CONNECT = configfile['Default']['bitcoind-rpc-connect']
    else:
        config.BITCOIND_RPC_CONNECT = 'localhost'

    # Bitcoind RPC port
    if bitcoind_rpc_port:
        config.BITCOIND_RPC_PORT = bitcoind_rpc_port
    elif has_config and 'bitcoind-rpc-port' in configfile['Default'] and configfile['Default']['bitcoind-rpc-port']:
        config.BITCOIND_RPC_PORT = configfile['Default']['bitcoind-rpc-port']
    else:
        if config.TESTNET:
            config.BITCOIND_RPC_PORT = '18332'
        else:
            config.BITCOIND_RPC_PORT = '8332'
    try:
        int(config.BITCOIND_RPC_PORT)
        assert int(config.BITCOIND_RPC_PORT) > 1 and int(config.BITCOIND_RPC_PORT) < 65535
    except:
        raise Exception("Please specific a valid port number bitcoind-rpc-port configuration parameter")

    # Bitcoind RPC user
    if bitcoind_rpc_user:
        config.BITCOIND_RPC_USER = bitcoind_rpc_user
    elif has_config and 'bitcoind-rpc-user' in configfile['Default'] and configfile['Default']['bitcoind-rpc-user']:
        config.BITCOIND_RPC_USER = configfile['Default']['bitcoind-rpc-user']
    else:
        config.BITCOIND_RPC_USER = 'bitcoinrpc'

    # Bitcoind RPC password
    if bitcoind_rpc_password:
        config.BITCOIND_RPC_PASSWORD = bitcoind_rpc_password
    elif has_config and 'bitcoind-rpc-password' in configfile['Default'] and configfile['Default']['bitcoind-rpc-password']:
        config.BITCOIND_RPC_PASSWORD = configfile['Default']['bitcoind-rpc-password']
    else:
        raise exceptions.ConfigurationError('bitcoind RPC password not set. (Use configuration file or --bitcoind-rpc-password=PASSWORD)')

    config.BITCOIND_RPC = 'http://' + config.BITCOIND_RPC_USER + ':' + config.BITCOIND_RPC_PASSWORD + '@' + config.BITCOIND_RPC_CONNECT + ':' + str(config.BITCOIND_RPC_PORT)

    # RPC host
    if rpc_host:
        config.RPC_HOST = rpc_host
    elif has_config and 'rpc-host' in configfile['Default'] and configfile['Default']['rpc-host']:
        config.RPC_HOST = configfile['Default']['rpc-host']
    else:
        config.RPC_HOST = 'localhost'

    # RPC port
    if rpc_port:
        config.RPC_PORT = rpc_port
    elif has_config and 'rpc-port' in configfile['Default'] and configfile['Default']['rpc-port']:
        config.RPC_PORT = configfile['Default']['rpc-port']
    else:
        if config.TESTNET:
            config.RPC_PORT = '14000'
        else:
            config.RPC_PORT = '4000'
    try:
        int(config.RPC_PORT)
        assert int(config.RPC_PORT) > 1 and int(config.RPC_PORT) < 65535
    except:
        raise Exception("Please specific a valid port number rpc-port configuration parameter")

    # RPC user
    if rpc_user:
        config.RPC_USER = rpc_user
    elif has_config and 'rpc-user' in configfile['Default'] and configfile['Default']['rpc-user']:
        config.RPC_USER = configfile['Default']['rpc-user']
    else:
        config.RPC_USER = 'rpc'

    # RPC password
    if rpc_password:
        config.RPC_PASSWORD = rpc_password
    elif has_config and 'rpc-password' in configfile['Default'] and configfile['Default']['rpc-password']:
        config.RPC_PASSWORD = configfile['Default']['rpc-password']
    else:
        raise exceptions.ConfigurationError('RPC password not set. (Use configuration file or --rpc-password=PASSWORD)')

    # Log
    if log_file:
        config.LOG = log_file
    elif has_config and 'logfile' in configfile['Default']:
        config.LOG = configfile['Default']['logfile']
    else:
        if config.TESTNET:
            config.LOG = os.path.join(config.DATA_DIR, 'counterpartyd.testnet.log')
        else:
            config.LOG = os.path.join(config.DATA_DIR, 'counterpartyd.log')

    if not unittest:
        if config.TESTCOIN:
            config.PREFIX = b'XX'                   # 2 bytes (possibly accidentally created)
        else:
            config.PREFIX = b'CNTRPRTY'             # 8 bytes
    else:
        config.PREFIX = config.UNITTEST_PREFIX

    # Database
    if config.TESTNET:
        config.DB_VERSION_MAJOR = str(config.DB_VERSION_MAJOR) + '.testnet'
    if database_file:
        config.DATABASE = database_file
    else:
        config.DB_VERSION_MAJOR
        config.DATABASE = os.path.join(config.DATA_DIR, 'counterpartyd.' + str(config.DB_VERSION_MAJOR) + '.db')

    # (more) Testnet
    if config.TESTNET:
        if config.TESTCOIN:
            config.ADDRESSVERSION = b'\x6f'
            config.BLOCK_FIRST = 154908
            config.BURN_START = 154908
            config.BURN_END = 4017708   # Fifty years, at ten minutes per block.
            config.UNSPENDABLE = 'mvCounterpartyXXXXXXXXXXXXXXW24Hef'
        else:
            config.ADDRESSVERSION = b'\x6f'
            config.BLOCK_FIRST = 154908
            config.BURN_START = 154908
            config.BURN_END = 4017708   # Fifty years, at ten minutes per block.
            config.UNSPENDABLE = 'mvCounterpartyXXXXXXXXXXXXXXW24Hef'
    else:
        if config.TESTCOIN:
            config.ADDRESSVERSION = b'\x00'
            config.BLOCK_FIRST = 278270
            config.BURN_START = 278310
            config.BURN_END = 2500000   # A long time.
            config.UNSPENDABLE = '1CounterpartyXXXXXXXXXXXXXXXUWLpVr'
        else:
            config.ADDRESSVERSION = b'\x00'
            config.BLOCK_FIRST = 278270
            config.BURN_START = 278310
            config.BURN_END = 283810
            config.UNSPENDABLE = '1CounterpartyXXXXXXXXXXXXXXXUWLpVr'

    # Headless operation
    config.HEADLESS = headless
    config.START_RPC_SERVER = start_server


def main(argv):
    # Parse command-line arguments.
    parser = argparse.ArgumentParser(prog='counterparty-gui', description='the GUI app for the counterparty protocol')
    parser.add_argument('-V', '--version', action='version', version="counterparty-gui v%s" % GUI_VERSION)
    parser.add_argument('--bitcoind-rpc-connect', help='the hostname of the Bitcoind JSON-RPC server')
    parser.add_argument('--bitcoind-rpc-port', type=int, help='the port used to communicate with Bitcoind over JSON-RPC')
    parser.add_argument('--bitcoind-rpc-user', help='the username used to communicate with Bitcoind over JSON-RPC')
    parser.add_argument('--bitcoind-rpc-password', help='the password used to communicate with Bitcoind over JSON-RPC')
    parser.add_argument('--rpc-host', help='the host to provide the counterpartyd JSON-RPC API')
    parser.add_argument('--rpc-port', type=int, help='port on which to provide the counterpartyd JSON-RPC API')
    parser.add_argument('--rpc-user', help='required username to use the counterpartyd JSON-RPC API (via HTTP basic auth)')
    parser.add_argument('--rpc-password', help='required password (for rpc-user) to use the counterpartyd JSON-RPC API (via HTTP basic auth)')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='sets log level to DEBUG instead of WARNING')
    parser.add_argument('--force', action='store_true', help='don\'t check whether Bitcoind is caught up')
    parser.add_argument('--testnet', action='store_true', help='use Bitcoin testnet addresses and block numbers')
    parser.add_argument('--testcoin', action='store_true', help='use the test Counterparty network on every blockchain')
    parser.add_argument('--unsigned', action='store_true', default=False, help='print out unsigned hex of transaction; do not sign or broadcast')
    parser.add_argument('--data-dir', help='the directory in which to keep the database, config file and log file, by default')
    parser.add_argument('--database-file', help='the location of the SQLite3 database')
    parser.add_argument('--config-file', help='the location of the configuration file')
    parser.add_argument('--log-file', help='the location of the log file')
    parser.add_argument('--no-counterpartyd', action='store_true', default=False, help='assume headless operation, e.g. don\'t ask for wallet passhrase')


    args = parser.parse_args()

    # Configuration
    set_options(data_dir=args.data_dir, bitcoind_rpc_connect=args.bitcoind_rpc_connect, bitcoind_rpc_port=args.bitcoind_rpc_port,
                bitcoind_rpc_user=args.bitcoind_rpc_user, bitcoind_rpc_password=args.bitcoind_rpc_password, rpc_host=args.rpc_host, rpc_port=args.rpc_port,
                rpc_user=args.rpc_user, rpc_password=args.rpc_password or ('PASSWORD' if not args.no_counterpartyd else None), log_file=args.log_file, database_file=args.database_file, testnet=args.testnet,
                testcoin=args.testcoin, headless=True, start_server=not args.no_counterpartyd)


    app = XCPApplication(argv)
    splashScreen = XCPSplashScreen()
    splashScreen.show()
    failure_message = verify_app_pre_reqs(splashScreen, app)

    if failure_message is not None:
        # create a dialog that, when dismissed, will kill the app.
        from utils import display_alert
        splashScreen.close()
        info, exc = failure_message
        display_alert(info, exc)
    else:
        mw = MainWindow()

        def callback(results):
            mw.fetch_initial_data_lambda()(results)
            mw.initialize_data_in_tabs()

        app.fetch_initial_data(callback)

        splashScreen.finish(mw)

        def auto_updating_thread():
            # variable that we check against the results of the last block check every time to see if
            # any new blocks have been added
            last_block = None
            while True:
                time.sleep(5)
                client = XCPClient()
                try:
                    block = client.get_running_info()['last_block']['block_index']
                    # any time we find a new block in the block chain, trigger a UI refresh
                    if last_block is None or block > last_block:
                        last_block = block
                        mw.setActiveBlockNumber(block)
                        app.fetch_initial_data(callback)
                except Exception as e:
                    print(e)
                    time.sleep(10)  # sleep a little extra before continuing

        t = threading.Thread(target=auto_updating_thread)
        t.daemon = True
        t.start()
        sys.exit(app.exec())


if __name__ == '__main__':
    main(sys.argv)