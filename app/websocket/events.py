from flask_socketio import emit
from app import socketio
import MetaTrader5 as mt5

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