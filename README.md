# BridgeCrusher
Simple GUI that displays the maximum force that a bridge can handle before collapsing.
Authors: Nick Huttemann, Julie Lee

![alt text](https://raw.githubusercontent.com/NickHEE/BridgeCrusher/master/Screenshot.png)

# Quick Start Guide

1. Plug in your openscale device into a USB port. Run Bridge Crusher and it will attempt to auto detect the serial COM port used.
    1. If the COM port cannot be detected, edit bridgecrusher.py and manually enter the COM port in the main() function
  
2. If everything is working, you will see the force display changing when you press on your load cell.
3. Enter your team name into the team list on the right and **double click** the team to select it as the active team.
4. When a team is active, force data will be recorded into a .csv file. When your bridge has been crushed or you wish to view the recorded data, press the **Start/Stop** button to stop recording data and view a force vs time graph.
5. When its time for the next team to have a go: 
    5. Enter another team name
    5. **Double click** the team to select it as the active team
    5. Press **Reset** to reset the current maximum force
    5. Press **Start/Stop** and crush your bridge


