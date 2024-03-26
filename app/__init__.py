from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Now you import the parts of your application that need to be registered with Flask
from app.api.routes import api_bp
app.register_blueprint(api_bp, url_prefix='/api')


from app.websocket import events
