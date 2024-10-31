# DDoS_Attack_On_Server_Simulation

DDoS Attack Simulation on Server Performance
This repository contains a Python-based simulation that models the impact of Distributed Denial of Service (DDoS) attacks on server performance, focusing specifically on CPU load and dropped packets. The simulation is created using the simpy, pygame, and matplotlib libraries to simulate and visualize the server's response under normal and attack conditions.

Description
The code simulates a server that processes requests from both normal clients and DDoS attackers. The simulation runs for a specified duration, with a DDoS attack starting midway through the simulation period. Key performance metrics, including CPU load and dropped packets, are tracked and plotted to provide insights into the server's performance under stress.

CPU Load: The percentage of processing capacity utilized by the server.
Dropped Packets: The number of requests that exceed the server’s processing capacity.
Features
Simulates normal client traffic and DDoS attack traffic.
Provides real-time visualization of server load and request handling using pygame.
Tracks and plots CPU load and dropped packets over time using matplotlib.
Requirements
Python 3.x
Libraries: simpy, pygame, matplotlib
Install the required libraries using:

bash

pip install simpy pygame matplotlib
Running the Simulation
To run the simulation, execute the following command in a terminal or IDE like Visual Studio Code:

bash

python ddos_simulation.py
The simulation will generate two graphs (cpu_load_over_time.png and dropped_packets_over_time.png) at the end, displaying the server's CPU load and dropped packets over the duration of the simulation.

Visualization
The server is represented by a rectangle in the center of the screen, changing color based on CPU load (green for low load, red for high load).
Normal clients are shown as blue circles, while attackers are displayed as yellow squares. Dropped requests appear in grey.
The simulation provides real-time movement and interaction of clients and attackers with the server.
References
GitHub Repository with the simulation code. [https://github.com/AnasNour/DDoS_Attack_On_Server_Simulation]
