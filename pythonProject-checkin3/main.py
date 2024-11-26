from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time
import RPi.GPIO as GPIO
from switch import Switch
from led import LED
from pump import Pump
from timer import Timer
from sensor import PressureSensor
import threading
import os
from PiControler import*
import eventlet
from data_file_render import *

# Set GPIO pins for switch, LED, and pump relay
SWITCH_PIN = 17  # GPIO pin for the start switch
LED_PIN = 27     # GPIO pin for the LED
RELAY_PIN = 22   # GPIO pin for the pump relay

# Store the state for each bay
progress_state = {
    1: {'status': 'Idle', 'progress': 0, 'pressure': 0},
    2: {'status': 'Idle', 'progress': 0, 'pressure': 0},
    3: {'status': 'Idle', 'progress': 0, 'pressure': 0},
    4: {'status': 'Idle', 'progress': 0, 'pressure': 0},
}

eventlet.monkey_patch()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_default_secret_key')  # Use environment variable or default key
socketio = SocketIO(app, cors_allowed_origins="*")


GPIO.setmode(GPIO.BCM)  # Set GPIO mode

def monitor_switch():
    while True:
        if switch.is_pressed():
            socketio.emit('switch_status', {'status': 'active'})
        else:
            socketio.emit('switch_status', {'status': 'install_cartridge'})

        socketio.sleep(1)  # Poll the switch status every second

data_loger = DataLogger("data_log.csv", "csv" )

def handle_sensor_data(data1, data2):



    formatted_data1 = f"{data1:.2f}"
    print(f"Emitted sensor data: {formatted_data1}")
    socketio.emit('pressure_sensor_reading_1', {'message': formatted_data1})
    socketio.sleep(1)  # Sleep for 1 second bef

    formatted_data2 = f"{data2:.2f}"
    print(f"Emitted sensor data: {formatted_data2}")
    socketio.emit('pressure_sensor_reading_2', {'message': formatted_data2})
    socketio.sleep(1)  # Sleep for 1 second bef

    data_loger.log_data(sensor1 = formatted_data1, sensor2 = formatted_data2)



# Serve the HTML page
@app.route('/')
def index():
    return render_template('index_c.html')


switch = Switch(SWITCH_PIN)
led = LED(LED_PIN)
@socketio.on('connect')
def handle_connect():
    emit('initialize_state', progress_state)


@socketio.on('switch_status_replay')
def switch_status():
    print("switch_status")




@socketio.on('start_pump')
def handle_pump(data):

    print('proces_time', data.get('proces_time'))
    time_process = data.get('proces_time')
    print("Pump started:", data)  # Log incoming data for debugging
    button_id = data.get("blockId")
    print("Button press event received:", button_id)

    pump = Pump(RELAY_PIN)
    pressure_sensor = PressureSensor()
    timer = Timer(time_process, pressure_sensor, handle_sensor_data)

    pump_controller = PiPumpController(switch, led, pump, timer)
    pump_controller.check_and_run()

thread = threading.Thread(target=monitor_switch, daemon=True)
thread.start()


# Run the server using socketio.run for WebSocket support
if __name__ == '__main__':
    print("Starting Flask-SocketIO server...")
    socketio.run(app, host='127.0.0.1', port=5005, debug=True, allow_unsafe_werkzeug=True)




