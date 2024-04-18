from flask_socketio import emit
from app import socketio
import MetaTrader5 as mt5
import logging
import datetime

logger = logging.getLogger(__name__)
symbols_file_path = r"C:/Users/Administrator/Documents/Projects/OmegaFin_WinAgent/runtimes/symbols.txt"
deal_time_file_path = r"C:/Users/Administrator/Documents/Projects/OmegaFin_WinAgent/runtimes/LastDeal.txt"


@socketio.on('setLastDeal')
def handle_my_custom_event(json):
    print('received json: ' + str(json))
    with open(deal_time_file_path, 'w') as file:
        file.write(str(json))
    # emit('my_response', json)


@socketio.on('connect')
def connect():
    print('Client connected to MT5 account info channel')
    emit('my_response', {'data': 'Connected to MT5 account info channel'})
    # Starting the background task
    socketio.start_background_task(background_task)


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


def mt5_account_info():
    try:
        if not mt5.initialize():
            print("Failed to initialize MT5")
            return {"error": "Failed to initialize MT5"}
        account_info = mt5.account_info()._asdict()
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": str(e)}
    finally:
        mt5.shutdown()
    return account_info


@socketio.on('request_closed_position_data')
def handle_closed_position_request(data):
    ticket = data.get('ticket')
    if ticket is None:
        logger.error("Ticket not provided for closed position data request")
        return

    if not mt5.initialize():
        logger.error("Failed to initialize MT5")
        emit('closed_position_data', {'error': "Failed to initialize MT5"})
        return

    try:
        # Assuming 'ticket' refers to a deal's ticket
        deals = mt5.history_deals_get(ticket=ticket)
        if deals is None or len(deals) == 0:
            logger.error(f"No data found for closed position with ticket: {ticket}")
            emit('closed_position_data', {'error': f"No data found for ticket: {ticket}"})
        else:
            # Convert the deal information to a dictionary
            # This example just takes the first deal, adjust as needed
            position_data = [deal._asdict() for deal in deals][0]  # Taking the first deal for simplicity

            emit('closed_position_data', {'data': position_data})
    except Exception as e:
        logger.exception(f"Failed to fetch data for closed position {ticket}: {e}")
        emit('closed_position_data', {'error': str(e)})
    finally:
        mt5.shutdown()


def background_task():
    while True:
        if not mt5.initialize():
            print("Failed to initialize MT5")
            return {"error": "Failed to initialize MT5"}
        data = fetch_data(symbols_file_path, deal_time_file_path)
        if data:
            socketio.emit('mt5_account_info', {'data': data})
        else:
            logger.error("No data to send")
        mt5.shutdown()
        socketio.sleep(3)


def fetch_data(symbols_file_path, deal_time_file_path):
    try:
        # Read symbols from file
        with open(symbols_file_path, 'r') as file:
            symbols = file.read().splitlines()

        # Fetch current prices for symbols
        prices = {}
        for symbol in symbols:
            price = mt5.symbol_info_tick(symbol)._asdict()
            if price:
                prices[symbol] = price
            else:
                logger.warning(f"Could not fetch price for symbol: {symbol}")

        # Fetch open positions
        positions = mt5.positions_get()
        if positions is None:
            logger.warning("No open positions")
            positions_data = []
        else:
            # Directly convert each position object to a dictionary
            positions_data = [position._asdict() for position in positions]

        # Fetch account info
        account_info = mt5.account_info()._asdict()
        if account_info is None:
            logger.error("Failed to fetch MT5 account info")
            return {"error": "Failed to fetch MT5 account info"}

        # Fetch active orders
        orders = mt5.orders_get()
        if orders is None:
            logger.warning("No active orders")
            orders_data = []
        else:
            # Directly convert each order object to a dictionary
            orders_data = [order._asdict() for order in orders]

        with open(deal_time_file_path, 'r') as f:
            last_deal_time = f.read().strip()
            last_deal_timestamp = datetime.datetime.strptime(last_deal_time, '%Y-%m-%d %H:%M:%S')
        now = datetime.datetime.now()

        # Add one day to get tomorrow's date at the same time
        tomorrow = now + datetime.timedelta(days=1)

        # Fetch deals from last timestamp to now
        deals = mt5.history_deals_get(last_deal_timestamp, tomorrow)
        # print(deals)
        if deals is None or len(deals) == 0:
            logger.warning("No new deals since last check")
            deals_data = []
        else:
            deals_data = [deal._asdict() for deal in deals]

        # Update the last deal timestamp in the file
        with open(deal_time_file_path, 'w') as f:
            f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        # Compile data
        data = {
            "positions": positions_data,
            "orders": orders_data,
            "deals": deals_data,
            "prices": prices,
            "profile": account_info
        }

        return data

    except Exception as e:
        logger.exception("Failed to fetch data: {}".format(str(e)))
        return None


