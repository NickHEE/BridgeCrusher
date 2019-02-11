# BridgeCrusher
Simple GUI that displays the maximum force that a bridge can handle before collapsing.
Authors: Nick Huttemann, Julie Lee

![Main View](https://raw.githubusercontent.com/NickHEE/BridgeCrusher/experimental/Screenshot.png)

![Graph View](https://raw.githubusercontent.com/NickHEE/BridgeCrusher/experimental/Screenshot2.PNG)

# Installation

1. Install Python 3.6+ and clone BridgeCrusher to your desired directory
2. Open a command prompt and "cd" to the BridgeCrusher folder (eg: cd C:\Users\Nick\Desktop\BridgeCrusher)
3. pip install -r "requirements.txt" (This will install all the required modules)

# Quick Start Guide

1. Plug in your openscale device into a USB port. Run Bridge Crusher (Crush.bat) and it will attempt to auto detect the serial COM port used.
    1. If the COM port cannot be detected, edit bridgecrusher.py and manually enter the COM port in the main() function
  
2. If everything is working, you will see the force display changing when you press on your load cell.
    1. If the scale is not reading zero when no force is applied, press the "zero scale" button.
3. Enter your team name into the team list on the right and **double click** the team to select it as the active team.
4. When a team is active, force data will be recorded into a .csv file. When your bridge has been crushed or you wish to view the recorded data, press the **Start/Stop** button to stop recording data and view a force vs time graph.
5. When its time for the next team to have a go: 
    1. Enter another team name
    2. **Double click** the team to select it as the active team
    3. Press **Reset** to reset the current maximum force
    4. Press **Start/Stop** and crush your bridge

