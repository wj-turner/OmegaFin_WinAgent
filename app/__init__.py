from flask import Flask
from flask_socketio import SocketIO

import logging
from logging.handlers import SysLogHandler
from concurrent_log_handler import ConcurrentRotatingFileHandler
import os

app = Flask(__name__)


def configure_logging(app, enable_file_logging=True, enable_syslog=True):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    if enable_file_logging:
        try:
            log_directory = r"C:\Users\Administrator\Documents\Projects\OmegaFin_WinAgent\runtimes\logs"
            if not os.path.exists(log_directory):
                os.makedirs(log_directory)
            # file_handler = RotatingFileHandler(os.path.join(log_directory, 'app.log'), maxBytes=10240, backupCount=10)
            file_handler = ConcurrentRotatingFileHandler(os.path.join(log_directory, 'app.log'), maxBytes=10240,
                                                         backupCount=10)

            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(logging.INFO)
            logger.addHandler(file_handler)
            app.logger.addHandler(file_handler)
        except Exception as e:
            logger.error(f"Failed to set up file logging: {e}")

    if enable_syslog:
        try:
            syslog_handler = SysLogHandler(address=('remote.syslog.server', 514))
            syslog_formatter = logging.Formatter('%(name)s: %(levelname)s - %(message)s')
            syslog_handler.setFormatter(syslog_formatter)
            syslog_handler.setLevel(logging.INFO)
            logger.addHandler(syslog_handler)
            app.logger.addHandler(syslog_handler)
        except Exception as e:
            logger.error(f"Failed to set up syslog logging: {e}")


configure_logging(app, enable_file_logging=True, enable_syslog=False)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Now you import the parts of your application that need to be registered with Flask
from app.api.routes import api_bp
app.register_blueprint(api_bp, url_prefix='/api')
from app.websocket import events


