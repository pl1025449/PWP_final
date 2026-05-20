import pickle as pck
try:
    settings=pck.load(open('setting.txt','rb'))
except:
    settings=[None,[3.8,-40,1.5],[3,40,1]]

"""
Purpose:
Control the robot's automatic movement.

Pseudocode:
1. Check whether auto mode is running.
2. Check whether a stop line has already been detected.
3. Receive the newest camera frame from the server layer.
4. Process the frame using OpenCV.
5. Use the steering value to control motor speeds.
6. If the horizontal stop line is detected, wait a few seconds so the robot
   can pass over the line, then stop the robot.
7. Allow the GUI Play/Stop buttons to start and stop automation.
"""

import time
import processing_parallel
from processing_parallel import process_frame
from motor_steering import set_motor_speeds
from Motordriver import stop_all,_send_command,turn_right
from obstacle import avoid_obstacle
from log_store import log_sto

# Auto-mode state variables
auto_running = False
stop_line_seen = False
stop_time = None

# How long the robot should keep moving after it detects the horizontal tape
# before stopping. You can tune this later if needed.
STOP_DELAY_SECONDS = 2.0


def start_automation():
    """
    Turn on automatic line-following mode.
    """
    global auto_running, stop_line_seen, stop_time,stopped, explored
    stopped=True
    auto_running = True
    stop_line_seen = False
    stop_time = None
    explored = False

def stop_automation(pause=False):
    """
    Turn off automatic line-following mode and stop the robot.
    """
    global auto_running, stop_line_seen, stop_time, stopped, explored

    auto_running = pause
    stopped =False
    stop_line_seen = False
    stop_time = None
    explored=False
    stop_all()


def is_running():
    """
    Return whether automatic mode is currently active.
    """
    return auto_running
last_c=""
def explorer(l,right,horizontal):
    #print("explorer:",explored)
    global last_c
    if not auto_running:
        print('ended due to stop')
        log_sto('ended due to stop')
        return False
    print("last_c=",last_c)
    if l and right:
        return True
    if horizontal:
        print('turn left initialized-following horizontal')
        log_sto('turn left initialized-following horizontal')
        _send_command('forward')
        time.sleep(settings[1][0])
#        print('turn right initialized')
        set_motor_speeds(settings[1][1])
        time.sleep(settings[1][2])
        _send_command('backward')
        time.sleep(1)
        stop_automation(True)
        #return False
    elif horizontal and right:
        print('turn right initialized')
        log_sto('turn right initialized')
        _send_command('forward')
        time.sleep(settings[2][0])
        #print("turn right initialized")
        set_motor_speeds(settings[2][1])
        time.sleep(settings[2][2])
        _send_command('forward')
        time.sleep(1)
        stop_automation(True)
        #return False
    elif horizontal and l:
        print('turn left initialized')
        log_sto('turn left initialized')
        _send_command('forward')
        time.sleep(settings[1][0])
#        print('turn right initialized')
        set_motor_speeds(settings[1][1])
        time.sleep(settings[1][2])
        _send_command('forward')
        time.sleep(5)
        stop_automation(True)
        #return False
    elif l:
        last_c="l"
        print('heyo')
        _send_command('forward')
    elif right:
        last_c='r'
        print('howdy')
        _send_command('forward')
    else:
        print('here')
        if last_c == 'l':
            set_motor_speeds(15)
        elif last_c == 'r':
            set_motor_speeds(-15)
        elif last_c=="":
            #print("here")
            _send_command("forward")
    return False
explored=False
def update_automation(frame):
    """
    Process one frame of video and update robot behavior.

    Parameters:
        frame: The newest camera frame.

    Returns:
        out: The processed overlay image.
    """
    global auto_running, stop_line_seen, stop_time, explored,stopped


    # Always process the frame so the processed stream can still display overlays
    out, steering_value, stop_line_detected, center_line,left,right,det,obst = process_frame(frame)
    print("explorer:",explored)
    log_sto("explorer mode:"+str(explored)+" ")
    if not auto_running or not stopped:
        return out,det
    if not explored:
        explored = explorer(left,right,stop_line_detected)
        return out,det
    # If the stop line is detected for the first time, start the stop timer
    if stop_line_detected and not stop_line_seen:
        stop_line_seen = True
        stop_time = time.time()

    # If the robot has already seen the stop line, keep going for a short delay,
    # then stop completely
    if stop_line_seen and left and not center_line:
        print('turn right initialized')
        #_send_command('forward')
        time.sleep(3.0)
        #print("turn right initialized")
        set_motor_speeds(40)
        time.sleep(1)
        _send_command('forward')
        time.sleep(1)
        stop_automation()
        return out,det
    if stop_line_seen and right and not center_line:
        print('turn left initialized')
        #_send_command('forward')
        time.sleep(3.8)
#        print('turn right initialized')
        set_motor_speeds(-40)
        time.sleep(1.0)
        _send_command('forward')
        time.sleep(5)
        stop_automation()
        return out,det
    elif stop_line_seen and not center_line:
        elapsed = time.time() - stop_time
        time.sleep(6.0)
        if elapsed >= STOP_DELAY_SECONDS:
            stop_automation()
            return out,det
    if center_line:
    # Normal line-following behavior
        print('hi')
        _send_command('forward')
    elif left:
        set_motor_speeds(10.0)
    elif right:
        set_motor_speeds(-10.0)
    else:
        stop_automation(True)
    if obst:
        log_sto('found obstacle... avoiding')
        avoid_obstacle()
        stop_automation(True)
    return out,det
