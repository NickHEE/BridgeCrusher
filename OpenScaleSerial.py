import serial
import io
import logging
from logging.handlers import RotatingFileHandler

# GLOBALS

# FUNCTIONS
def get_val():
    ser = serial.Serial('COM4', 115200, timeout=1)
    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser), newline='\r\n')
    s
    return val

# CLASSES
class TeamScores:
    class Top10:
        def __init__(self, name, score):
            self.name = name
            self.score = score
            return

        def reset(self):
            for var in self.score:
                var.score = None
            self.team_name = None
            self.max_val = None
            return

    def __init__(self, team_name, max_val):
        self.team_name = team_name
        self.max_val = max_val
        self.score = []
        self.top10 = []
        return

    def add_highteam(self, team_name, max_val):
        self.top_team.append(TeamScores.CurrentTeam(team_name))
        self.top_score.append(TeamScores.CurrentTeam(max_val))
        return





def main():
    teams = TeamScores()
    for var in team_name:

    return



if __name__ == '__main__':
    main()
