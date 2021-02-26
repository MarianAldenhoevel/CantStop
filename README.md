# Cant' Stop
This is a machine-learing experiment on the board game "Can't Stop"

The long-term goal is to train an agent to play the game competently against other agents or humans.

# The Game
Can't stop is a simple dice-rolling board game for three players. The objective is to be the first to top out on three ladders or climbing-routes. This is made tricky by the option to roll again as often as you want, risking the danger of losing all progress.

![Screenshot](https://raw.githubusercontent.com/MarianAldenhoevel/CantStop/master/doc/Screenshot%202021-02-25%20161046.png)

# Progress
I have built a representation of the board and the game mechanics. This can be played in the console by people using a simple menu-system. 

That representation can be used as the environment agents will interact with. It offers observation of the current state, gives options for actions and updates state according to the rules.
