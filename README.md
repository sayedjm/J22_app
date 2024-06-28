# J22 system
Repair & order system for j22 

This repair system is used for repairs at the jewels shop J22 located in Rijswijk. 
The software that will be used is Python with the framework Flask. For the first time, you have to set up the database. 
Use the following script in the terminal to create the database locally:

	python3 creat_database.py

Setup that the .Bat file automatically starts up if you turn on the computer. this ensures that de servers are locally online.
If the user inserts, update or move the repair, automatically makes a backup from the database in the form of a TXT file. If are any unexpected errors coms over make a screenshot and connect the maker of the application. The errors are logged in a logfile.


# Install

Clone repository

    git clone https://github.com/sayedjm/repair_system.git

Requirements

In the project root folder and with the activated virtual environment:

     pip install -r requirements.txt

In the project root folder and with the activated virtual environment:

    flask --app app run
