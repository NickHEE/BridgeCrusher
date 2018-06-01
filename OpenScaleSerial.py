import serial
import io
import time
import logging
from logging.handlers import RotatingFileHandler

# GLOBALS

# FUNCTIONS


def zero_scale():
    ser = serial.Serial('COM4', 115200, timeout=1)
    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser), newline='\r\n')

    while time.time() < time.time() + 2:
        trunk = ser.readline()

    ser.write(b'x\r\n')
    for line in sio.readlines():
        trunk = line
    sio.flush()
    ser.write(b'1\r\n')
    time.sleep(0.5)
    sio.flush()
    for line in sio.readlines():
        if line == '>\r\n':
            break
    sio.flush()
    ser.write(b'x\r\n')
"""
def start():


def get_val():
    ser = serial.Serial('COM4', 115200, timeout=1)
    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser), newline='\r\n')

    return val
"""


# CLASSES


class TeamScores:
    class Top10:
        def __init__(self, name, score):
            self.name = name
            self.score = score
            return

        def reset_top10(self):
            self.name = None
            self.score = None
            return

    def __init__(self, team_name, max_val):
        self.team_name = team_name
        self.max_val = max_val
        self.val = []
        self.top10 = []
        return

    def add_top10(self, team_name, max_val):
        self.top10.append(TeamScores.Top10(team_name, max_val))
        return

    def clear_top10(self):
        for var in self.top10:
            var.top10 = None
        return


def main():
    ser = serial.Serial('COM4', 115200, timeout=1)
    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser), newline='\r\n')
    start = time.time()
    while time.time() < start+2:
        trunk = ser.readline()

    ser.write(b'x\r\n')
    sio.flush()
    for line in sio.readlines():
        trunk = line

    ser.write(b'1\r\n')
    sio.flush()
    for line in sio.readlines():
        if line == '>\r\n':
            break

    ser.write(b'x\r\nx\r\n')
    sio.flush()

    while time.time() < time.time()+5:
        # output = str(ser.readline(), 'utf-8')
        # print(output)
        output = sio.readline()
        if 'Exiting' not in output:
            # start = output.rfind('-')
            end = output.rfind(',kg')
            value = output[0:end]
            print(value)
    ser.close()
    return

if __name__ == '__main__':
    main()
