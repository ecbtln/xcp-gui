from constants import BTC_CONNECTION_TIMEOUT
from counterpartyd.lib import util
import counterpartyd.lib.config as config
from bitcoinrpc.authproxy import AuthServiceProxy
from rpcclient.btc_async_app_client import url_for_client
import time
import urllib.request
import traceback
from counterpartyd.lib import api
from counterpartyd.lib import blocks
import threading
from rpcclient.xcp_client import XCPClient


def verify_app_pre_reqs(splashScreen, app):

    def progress_ui(status_update):
        splashScreen.showMessage(status_update)
        app.processEvents()

    progress_ui("Performing required startup tasks")
    client = AuthServiceProxy(url_for_client(), timeout=BTC_CONNECTION_TIMEOUT)

    try:
        current_count = client.getblockcount()
    except Exception as e:
        return ("Could not connect to bitcoind", traceback.format_exc())

    progress_ui("bitcoind connection established")

#        splashScreen.bar.setValue(25) # step 1 of 5 complete

    if config.TESTNET:
        url = 'http://blockexplorer.com/testnet/q/getblockcount'
    else:
        url = 'https://blockchain.info/q/getblockcount'

    def get_last_block():
        return urllib.request.urlopen(url).read().decode('utf-8')

    last_block = get_last_block()
    if current_count != last_block:
        progress_ui("Bitcoind blockchain %d blocks behind" % (int(last_block) - int(current_count)))
    else:
        progress_ui("Bitcoind blockchain up to date")
    while current_count != last_block:
        try:
            current_count = client.getblockcount()
            last_block = int(get_last_block())

            if current_count == last_block:
                progress_ui("Bitcoind blockchain up to date")
                break
            progress_ui("Current blockchain progress: %s/%s" % (current_count, last_block))
            time.sleep(3)
        except Exception as e:
            return 'Lost bitcoind connection', traceback.format_exc()

    if config.START_RPC_SERVER:
        progress_ui("Launching counterpartyd")
        db = util.connect_to_db()
        api_server = api.APIServer()
        api_server.daemon = True
        api_server.start()
        api_server.join(4) # wait 3 seconds, if the thread is dead that means an exception was thrown
        if api_server.isAlive():
        # fork off in another thread
            t = threading.Thread(target=lambda: blocks.follow(db))
            t.daemon = True
            t.start()
        else:
            return "Cannot start the API subsystem. Is counterpartyd already running, or is " \
                   "something else listening on port %s?" % config.RPC_PORT, ''
#           splashScreen.bar.setValue(75)

    # we've now started up the webserver, finally just wait until the db is in a good state
    client = XCPClient()
    while True:
        try:
            response = client.get_running_info()
            if response['db_caught_up']:
                progress_ui("Counterpartyd finished parsing blockchain")
                break
            else:
                current_block = response['last_block']['block_index'] or 0
                current_block = int(current_block)
                progress_ui("Current counterpartyd progress: %d/%s" % (current_block, current_count))
            time.sleep(3)
        except Exception as e:
            return 'Lost counterpartyd RPC connection', traceback.format_exc()

    return None