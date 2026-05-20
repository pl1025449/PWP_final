'''
Purpose:
Run the Flask web server.

Pseudocode:
1. Start the camera.
2. Continuously read frames in a background thread.
3. Store the newest frames in a small buffer.
4. Serve the raw video stream.
5. Serve the processed video stream.
6. Start and stop automation when the GUI buttons are pressed.
'''
from datetime import datetime as dt
from datetime import timezone
utc_dt=dt.now(timezone.utc)
l_dt=utc_dt.astimezone()
import Motordriver as mot
import threading
from flask import render_template as r_t
#from tkinter import messagebox
import cv2
import numpy as np
from flask import Flask, Response,jsonify
from log_store import log_sto,gimmefull
from automation import start_automation, stop_automation, update_automation
if 'y' in input("start calibration?") and 'n' not in input("start calibration?"):
    from calibrate import calibrate
app = Flask(__name__)

# Camera setup
cap = cv2.VideoCapture(0)

# Frame buffer
frame_buffer = [None] * 5
buf_lock = threading.Lock()
buf_i = [0]

should_popup = False

def camera_reader():
    """
    Continuously read frames from the camera and store them in a circular buffer.
    """
    while True:
        ok, frame = cap.read()
        if not ok or frame is None:
            continue

        frame = np.asarray(frame)

        with buf_lock:
            frame_buffer[buf_i[0]] = frame
            buf_i[0] += 1
            if buf_i[0] == len(frame_buffer):
                buf_i[0] = 0


# Start camera thread immediately
threading.Thread(target=camera_reader, daemon=True).start()


def get_latest():
    """
    Return a copy of the newest frame in the buffer.
    """
    with buf_lock:
        idx = buf_i[0] - 1
        if idx < 0:
            idx = len(frame_buffer) - 1

        frame = frame_buffer[idx]
        if frame is None:
            return None

        return frame.copy()


def gen_raw():
    """
    raw camera video stream for Flask.
    """
    while True:
        frame = get_latest()
        if frame is None:
            continue

        ok, buf = cv2.imencode(".jpg", frame)
        if not ok:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"
        )


def gen_processed():
    """
    processed video stream for Flask.

    If auto mode is running, this also updates the robot control logic.
    If auto mode is not running, it still shows the processed overlay.
    """
    while True:
        frame = get_latest()
        if frame is None:
           continue
        global should_popup
        with buf_lock:
            out,det = update_automation(frame)
        should_popup=det
        print("detected face:",det)
        ok, buf = cv2.imencode(".jpg", out)
        if not ok:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"
        )

@app.route('/status')
def status():
    return jsonify({"popup": should_popup})

@app.route('/trigger')
def trigger():
    global should_popup
    should_popup = True
#    messagebox.showinfo("Title", "We are not alone!")
#    return jsonify({"ok": True})


@app.route('/reset')
def reset():
    global should_popup
    should_popup = False
    return jsonify({"ok": True})


@app.route("/stream")
def stream():
    """
    Raw camera stream route.
    """
    return Response(gen_raw(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/stream_processed")
def stream_processed():
    """
    Processed camera stream route.
    """
    return Response(
        gen_processed(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/play", methods=["POST"])
def play():
    """
    Start automation mode.
    """
#    calibrate()
    start_automation()
    return log_sto("Automation started")

@app.route("/do/<dir>", methods=["POST"])
def do(dir):
   mot._send_command(str(dir)) 
   return log_sto(f"command {dir} sent")
@app.route("/log", methods=["GET"])
def log():
   return log_sto("")
@app.route("/flog", methods=["GET"])
def flog():
   return gimmefull()
@app.route("/stop", methods=["POST"])
def stop():
    """
    Stop automation mode.
    """
    stop_automation(False)
    return log_sto("Automation stopped")
@app.route("/gui", methods=["GET"])
def gui():
    return    r_t('gui.html', name='main_gui')
    
