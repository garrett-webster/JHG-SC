# JHG-SC
A project to extend the Junior High Game with a social choice aspect.

The Junior High Game was built in the research lab of Dr. Jacob Crandall to study social dynamics. To see the current version, see beta.juniorhighgame.com. This project, also developed in Dr. Crandall's lab, extends the Junior High Game by adding a social choice voting system.
The primary goals are to study how the social dynamics in the Junior High Game affect a different system, where interests may or may not be aligned in the same way as in the Junior High Game running in parallel. 

The implementation of the Junior High Game that this is built on was developed for a paper accepted at the 2024 IJCAI conference. That code can be found here github.com/jakecrandall/IJCAI2024_SM
The development of this project was started as a fork of the above repository and can be found here https://github.com/seanvsmith1901/IJCAI2024_SM

# Setting Up A Game
To set up the options for the game, open Server/server.py. In the OPTIONS dictionary, set "NUM_HUMANS" to the desired number of human players and "TOTAL_PLAYERS" to the desired number of total players, such that "TOTAL_PLAYERS" minus "NUM_HUMANS" is equal to the number of bots you want to play with (set these equal to each other if you want to bots). Set "JHG_ROUNDS_PER_SC_ROUND" equal to the number of Junior High Game rounds you want to elapse between each Social Choice round (normally 1 or 3). Set the "MAX_ROUNDS" to the number of Junior High Game rounds you want to play. Set "SC_GROUP_OPTION" to play with the group configuration you want to play with. See Server/options_creation.py for more information. set "SC_VOTE_CYCLES" equal to the number of cycles you want to play in each Social Choice round. Usually this is set at 3. 

If you will be playing with multiple people across several computers, find the variable called host in Client/jhg_client.py and set it equal to the IP address of the machine that the server is being run on. Confirm that the port number matches in Server/server.py. Note that if you will only be running clients on the same machine as the server, you can set the IP address as localhost (127.0.0.1). The port numbers in both files must still match.

# Running A Game
Running the server: In a terminal, navigate to the Server directory and run "python3 server.py". You will see a message that says "Server started", and may see several messages regarding failure to delete files. Those messages can be safely ignored. Note that the server must be running before any clients can be run.

Running the clients: For each human client, open a terminal, navigate to the Client directory, and run jhg_client.py. A GUI should appear. Do not attempt to play the game until all human clients have connected. Multiple clients can be run on the same machine, they just each need their own terminal instance. 
