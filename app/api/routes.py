from flask import Blueprint, jsonify, request
import MetaTrader5 as mt5
import logging
from datetime import datetime

api_bp = Blueprint('api', __name__)


@api_bp.route('/data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'POST':
        # Example POST request processing
        data = request.json
        return jsonify({"received": data}), 201
    else:
        # Example GET request
        return jsonify({"message": "This is a GET request to the REST API"})


@api_bp.route('/test_trade', methods=['GET'])
def test_trade():
    # Initialize MT5 connection
    # if not mt5.initialize():
    #     mt5.shutdown()
    #     return jsonify({"error": "Failed to initialize MT5"}), 500

    # account_info = mt5.account_info()
    # if account_info is not None:
    #     return jsonify({"message": " successful", "details": account_info.balance}), 200
    #     # print(f"Account Balance: {account_info.balance}")
    # else:
    #     print("Failed to get account information.")

    #order:
    ticket = 41878353
    # ticket = 33924235
    if ticket is None:
        print("Ticket not provided for closed position data request")
        return

    if not mt5.initialize():
        print("Failed to initialize MT5")
        # emit('closed_position_data', {'error': "Failed to initialize MT5"})
        return

    try:
        # Assuming 'ticket' refers to a deal's ticket
        deals = mt5.history_deals_get(position=ticket)
        # from_date = datetime(2020, 1, 1)
        # to_date = datetime.now()
        # deals=mt5.history_deals_get(from_date, to_date, group="*EUR*")
        if deals is None or len(deals) == 0:

            print(f"No data found for closed position with ticket: {ticket}")
            # emit('closed_position_data', {'error': f"No data found for ticket: {ticket}"})
        else:
            # Convert the deal information to a dictionary
            # This example just takes the first deal, adjust as needed
            # position_data = [deal._asdict() for deal in deals][0]  # Taking the first deal for simplicity
            print(deals)
            # emit('closed_position_data', {'data': position_data})
    except Exception as e:
        print(f"Failed to fetch data for closed position {ticket}: {e}")
        # emit('closed_position_data', {'error': str(e)})
    finally:
        mt5.shutdown()


@api_bp.route('/history_orders', methods=['GET'])
def get_history_orders():
    logger = logging.getLogger(__name__)

    # Initialize MT5 connection
    if not mt5.initialize():
        logger.error(f"initialize() failed, error code = {mt5.last_error()}")
        return jsonify({"error": "Failed to initialize MT5", "code": mt5.last_error()}), 500

    try:
        # Extract and process query parameters
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        group = request.args.get('group')
        ticket = request.args.get('ticket')
        position = request.args.get('position')

        # Convert date strings to datetime objects or set a wide range for "all" orders
        if from_date:
            from_date = datetime.strptime(from_date, "%Y-%m-%d %H:%M:%S")
        else:
            from_date = datetime(2023, 1, 1, 0, 0).replace(tzinfo=None)

        if to_date:
            to_date = datetime.strptime(to_date, "%Y-%m-%d %H:%M:%S")
        else:
            to_date = datetime.now().replace(microsecond=0, tzinfo=None)

        # Fetch history orders based on filters
        if ticket:
            history_orders = mt5.history_orders_get(ticket=int(ticket))
        elif position:
            history_orders = mt5.history_orders_get(position=int(position))
        else:
            # Default action for fetching a broad range of orders
            history_orders = mt5.history_orders_get(from_date, to_date)

        # Check if the query returned orders or an error occurred
        if history_orders is None:
            raise ValueError("No history orders found or error occurred")

    except ValueError as ve:
        logger.warning(f"Value error: {ve}")
        return jsonify({"error": str(ve), "code": mt5.last_error()}), 404
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return jsonify({"error": "Unexpected server error", "code": mt5.last_error()}), 500
    finally:
        mt5.shutdown()

    # Convert the history orders to a list of dictionaries for JSON response
    orders_list = [order._asdict() for order in history_orders]
    logger.info("Successfully fetched history orders")
    return jsonify(orders_list)