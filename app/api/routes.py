from flask import Blueprint, jsonify, request
import MetaTrader5 as mt5

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/data', methods=['GET', 'POST'])
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
    if not mt5.initialize():
        mt5.shutdown()
        return jsonify({"error": "Failed to initialize MT5"}), 500

    account_info = mt5.account_info()
    if account_info is not None:
        return jsonify({"message": " successful", "details": account_info.balance}), 200
        # print(f"Account Balance: {account_info.balance}")
    else:
        print("Failed to get account information.")