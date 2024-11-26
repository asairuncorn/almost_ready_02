# timer.py
import time
from sensor import*

class Timer:
    def __init__(self, duration, pressure_sensor, callback_sensor_data):
        """
        Initializes the timer with a specified duration in seconds.
        """

        self.duration = duration
        self.remaining_time = duration
        self.pressure_sensor = pressure_sensor
        self.callback_sensor_data = callback_sensor_data





    def start(self):
        """
        Starts the countdown timer and displays the remaining time.
        """
        start_time = time.time()
        while time.time() - start_time < self.duration:
            self.remaining_time = self.duration - int(time.time() - start_time)
            print(f"Time remaining: {self.remaining_time} seconds", end='\r')

            sensor1, sensor2 = self.pressure_sensor.read_data()
            self.callback_sensor_data(sensor1, sensor2)

            time.sleep(1)



        print("\nTimer completed.")



