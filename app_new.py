from flask import Flask, jsonify, request
from flask_socketio import SocketIO, send, emit
import MetaTrader5 as mt5
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# REST API Endpoint
@app.route('/api/data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'POST':
        # Example POST request processing
        data = request.json
        return jsonify({"received": data}), 201
    else:
        # Example GET request
        return jsonify({"message": "This is a GET request to the REST API"})
@app.route('/test_trade', methods=['GET'])
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
# WebSocket Event Handler
@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))
    emit('my_response', json)


# @socketio.on('connect')
# def test_connect():
#     emit('my response', {'data': 'Connected'})


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


def background_task():
    while True:
        account_info = mt5_account_info()
        if "error" not in account_info:
            socketio.emit('mt5_account_info', {'data': account_info})
        else:
            print(account_info["error"])
        socketio.sleep(3)


@socketio.on('connect')
def connect():
    print('Client connected to MT5 account info channel')
    emit('my_response', {'data': 'Connected to MT5 account info channel'})
    # Starting the background task
    socketio.start_background_task(background_task)
#
# @socketio.on('disconnect')
# def test_disconnect():
#     print('Client disconnected')


if __name__ == '__main__':
    # When using Flask-SocketIO with Eventlet, the socketio.run method is used to start the server.
    socketio.run(app, host='0.0.0.0', debug=True)
