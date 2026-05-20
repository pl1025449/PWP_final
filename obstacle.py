import time
from motor_steering import set_motor_speeds
from Motordriver import _send_command

def avoid_obstacle():
    _send_command('backward')
    time.sleep(2)
    set_motor_speeds(30.0)
    time.sleep(1.2)
    _send_command('forward')
    time.sleep(3.0)
    set_motor_speeds(-30.0)
    time.sleep(1.2)
    _send_command('forward')
    time.sleep(8.0)
    set_motor_speeds(-30.0)
    time.sleep(1.2)
    _send_command('forward')
    time.sleep(3.0)
    set_motor_speeds(30.0)
    time.sleep(1.2)
