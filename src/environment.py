import random
import logging
import colorama
import itertools
import copy

class Environment():
    
    def __init__(self):

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug('__init__')

        self.ACTION_THROW_AGAIN = -1
        self.ACTION_STICK_DOWN = -2

        self.PLAYER_INFO = [
            ("Red",   colorama.Fore.RED),
            ("Blue",  colorama.Fore.BLUE),
            ("Green", colorama.Fore.GREEN) 
        ]

        self.board = [
            [                     [], [], []                     ], #  2
            [                 [], [], [], [], []                 ], #  3
            [             [], [], [], [], [], [], []             ], #  4
            [         [], [], [], [], [], [], [], [], []         ], #  5
            [     [], [], [], [], [], [], [], [], [], [], []     ], #  6
            [ [], [], [], [], [], [], [], [], [], [], [], [], [] ], #  7
            [     [], [], [], [], [], [], [], [], [], [], []     ], #  8
            [         [], [], [], [], [], [], [], [], []         ], #  9
            [             [], [], [], [], [], [], []             ], # 10
            [                 [], [], [], [], []                 ], # 11
            [                     [], [], []                     ], # 12
        ]

    def reset(self):
        self.logger.debug('reset()')

        self.last_action = ''
        self.current_turn = 1
        self.current_player = 0
        self.phase = 0
        self.winner = -1
        self.in_flight = []
        
        for ladder in self.board:
            for i in range(0, len(ladder)):
                ladder[i] = []

        '''
        # Set up situation for debugging
        self.board[5][0]=[0]
        self.board[6][0]=[0]
        self.in_flight = [
            [5,0],
            [6,0]
        ]
        '''

        # Throw first set of dice and initialize first observation
        self.throw_dice()
        self.build_observation()

    def sorted_pair(self, a, b):
        # Returns a tuple of a and b in sorted order
        return (min(a,b), max(a,b))

    def position_in_ladder(self, player, ladderindex):
        # Return the position of players marker in the ladder. -1 if he has not
        # placed one. Does not look at markers in flight.
        
        for pos in range(0, len(self.board[ladderindex])):
            if player in self.board[ladderindex][pos]:
                return pos

        return -1

    def position_in_ladder_in_flight(self, ladderindex):
        # Return the position of players marker in the ladder within the current turn. 
        # -1 if he has not placed one.
        
        for inflight in self.in_flight:
            if inflight[0] == ladderindex:
                return inflight[1]

        return -1

    def build_observation(self):
        # (Re-)build the dictionary for the observation
        self.logger.debug("build_observation()")
        
        self.observation = {
            "board":     copy.deepcopy(self.board),
            "in_flight": copy.deepcopy(self.in_flight),
            "phase":     self.phase,
            "winner":    self.winner
        }

        self.logger.debug("Observation: " + str(self.observation))

    def throw_dice(self):
        self.logger.debug("throw_dice()")

        # Throw 4 dice
        self.dice = [random.randint(1,6), random.randint(1,6), random.randint(1,6), random.randint(1,6)]
        #self.dice = [1,1,2,3] # For debugging - can just always play action #1 and will quickly win.
        #self.dice = [6,5,6,5]
        self.logger.debug("Thrown: " + ", ".join(str(x) for x in self.dice))

        # Create all three possible pairs of sums of two dice
        self.combinations = [
            self.sorted_pair( self.dice[0] + self.dice[1], self.dice[2] + self.dice[3] ),
            self.sorted_pair( self.dice[0] + self.dice[2], self.dice[1] + self.dice[3] ),
            self.sorted_pair( self.dice[0] + self.dice[3], self.dice[1] + self.dice[2] )             
        ]

        # Remove duplicate combinations
        self.combinations = list(set(self.combinations))

        # Sort by the tuples in lexicographic order for clarity and repeatability
        self.combinations.sort()
        
        self.logger.debug("Available combinations: " + ", ".join(str(x) for x in self.combinations))

        # Create the actions from each viable combination
        self.actions = []

        # For each combination
        for comb in self.combinations:
            self.logger.debug("Create actions for combination " + str(comb))
                
            # What actions are applicable for this combination? We can progress on
            # ladders or place new inflight-markers. 
            can_progress = []
            can_place =    []
                    
            for c in comb:
                self.logger.debug("Create actions for throw " + str(c))
                
                ladderindex = c-2
                ladder = self.board[ladderindex]

                # The ladder can only progress if no player has fully claimed it yet. For real or in-flight.
                if (len(ladder[-1]) == 0) and (self.position_in_ladder_in_flight(ladderindex) < len(ladder)-1):
                    
                    # If we already have a marker in flight on that ladder we could progress that marker.
                    if self.position_in_ladder(self.current_player, ladderindex) > -1 or self.position_in_ladder_in_flight(ladderindex) > -1:
                        can_progress.append(ladderindex)
                    else:
                        # We do not yet have a marker in flight on the ladder. Can we
                        # place another one? There may only be three.
                        if len(self.in_flight) < 3:
                            # Yes. If already a place-candidate, promote this second move to progress
                            if ladderindex in can_place:
                                can_progress.append(ladderindex)
                            else:
                                can_place.append(ladderindex)

            # What can happen?
            # 0) No action possible.
            # 1) We can have progress on one or two ladders. Max two, because there are only two
            #    sums of dice in the combination.
            # 2) We can have the option of placing one or two new markers. A maximum of two, because
            #    there are only two sums of dice in the combination
            # 3) We can have two separate options of placing just one marker. This happens if in case #2
            #    there are two options but we only have one free in-flight-slot.
            action = ""
            ladders = []
            
            self.logger.debug("can_place = " + str(can_place))
            self.logger.debug("can_progress = " + str(can_progress))
            
            if can_place:
                p = list(set(can_place))
                p.sort()
                for prog in p:
                    if prog in ladders:
                        new = ""
                        New = ""
                    else:
                        new = "new "
                        New = "New "

                    # If we already have two ladders in flight we cannot place a combined action
                    # for two more ladders. Instead we need to create them as separate actions. Push
                    # current action and create a new one.
                    if (self.position_in_ladder_in_flight(prog) == -1) and (len(self.in_flight) == 2): 
                        if ladders and action:
                            self.actions.append((str(comb) + ":" + action, ladders))
                        action = ""
                        ladders = []
                
                    if ladders:
                        action += " and " + new + "progress"
                    else:  
                        action += " " + New + "progress"    
                    action += " on " + str(prog+2)
                    ladders.append(prog)

            if can_progress:
                for prog in can_progress:
                    # if we already have prog in ladders we check for the penultimate current
                    # position. So we do not double-advance past the top.
                    pos = max(self.position_in_ladder(self.current_player, prog), self.position_in_ladder_in_flight(prog))
                    
                    if (not(prog in ladders)) or (pos < len(self.board[prog])-2):
                        
                        # If we already have two ladders in flight we cannot place a combined action
                        # for two more ladders. Instead we need to create them as separate actions. Push
                        # current action and create a new one.
                        if (prog not in ladders) and (self.position_in_ladder_in_flight(prog) == -1) and (len(self.in_flight) == 2): 
                            if ladders and action:
                                self.actions.append((str(comb) + ":" + action, ladders))
                            action = ""
                            ladders = []
                    
                        if ladders:
                            action += " and progress"
                        else:
                            action += " Progress"    
                        action += " on " + str(prog+2)
                        ladders.append(prog)

            if ladders and action:
                self.actions.append((str(comb) + ":" + action, ladders))

    def next_turn(self):
        self.logger.debug("next_turn()")

        while True:
            self.current_turn += 1
            self.phase = 0
            self.current_player = (self.current_player+1) % 3
            self.in_flight = []
            self.throw_dice()

            if self.actions:
                break
                
    def take_action(self, action):
        self.logger.debug('take_action("{action}")'.format(action = action))
        
        self.actions = []

        if self.phase == 0:
            for ladderindex in action[1]:
                is_in_flight = False
                for inflight in self.in_flight:
                    if inflight[0] == ladderindex:
                        is_in_flight = True
                        inflight[1] += 1

                if not is_in_flight:
                    pos = max(self.position_in_ladder(self.current_player, ladderindex), self.position_in_ladder_in_flight(ladderindex))                
                    self.in_flight.append([ladderindex, pos + 1])

            # Save last movement action for rendering
            self.last_action = action[0]
            self.last_player = self.current_player
             
            # Switch to next phase
            self.phase += 1
            self.dice = []

            # Create fixed actions for next phase
            self.actions = [
                ("Throw dice again", self.ACTION_THROW_AGAIN),
                ("Stick markers down and finish turn", self.ACTION_STICK_DOWN)
            ]

        elif self.phase == 1:
            if action[1] == self.ACTION_THROW_AGAIN:
                # Throw dice again
                self.throw_dice()
                
                if self.actions:
                    # There are valid actions to play
                    self.phase = 0
                else:
                    # No more valid actions to play. Reset everything in flight and start
                    # phase 0 for the next player
                    self.last_action = "No valid action, markers reset"
                    
                    # Next player
                    self.next_turn()
                    
            elif action[1]  == self.ACTION_STICK_DOWN:   
                # Finish turn
                for in_flight in self.in_flight:
                    ladderindex = in_flight[0]
                    new_pos = in_flight[1]
                    if new_pos == len(self.board[ladderindex]) - 1:
                        # Reached the top. Fill ladder with just my markers.
                        for pos in range(0, len(self.board[ladderindex])):
                            self.board[ladderindex][pos] = [self.current_player]
                    else:
                        # Not yet at the top. Remove from current position in the ladder if present.       
                        pos = self.position_in_ladder(self.current_player, ladderindex)
                        if pos > -1:
                            self.board[ladderindex][pos].remove(self.current_player)
                        # And put into in-flight position
                        self.board[ladderindex][new_pos].append(self.current_player)

                self.in_flight = []

                # Check for a win. The player wins when he has a marker at the top in three ladders.
                topcount = 0
                for ladder in self.board:
                    if self.current_player in ladder[-1]:
                        topcount += 1

                if topcount >= 3:
                    # We have a winner!
                    self.winner = self.current_player
                    self.last_action += ". Player #{n} ({name}) wins".format(n= self.current_player, name = self.PLAYER_INFO[self.current_player][0])                        
                else: 
                    # Next player
                    self.next_turn()
            else:
                raise ValueError("Unsupported action")

        self.build_observation()    

    def render(self, colorize):
        INDENT = 5
        COLWIDTH = 5 # Width of the column reserved for each ladder
        COLSPACE = 4

        # Separator and Number of turns
        pagewidth = (INDENT + len(self.board) * (COLWIDTH + COLSPACE) + INDENT)
        print("< Turn #{current_turn} >".format(current_turn = self.current_turn).center(pagewidth, "-"))
        print()

        # Print last action that happened leading up to the board currently being displayed
        if (self.last_action):
            print((self.PLAYER_INFO[self.last_player][1] if colorize else "") + "Player #{last_player} ({name}) played: {last_action}.".format(
                last_player = self.last_player,
                name = self.PLAYER_INFO[self.last_player][0],
                last_action = self.last_action).center(pagewidth) + (colorama.Fore.WHITE if colorize else ""))
        else:
            print()

        print() 
        
        # Go down the board row by row. The maximum number of rows is in ladder at index 5. We start at -1 and add one
        # for the ladder-numbers above and below.
        for row in range(-1, len(self.board[5]) + 1):
            
            # Build one line of output
            line = ""

            # For each ladder add the representation of the current logical row and pad to COLUMNWIDTH
            for ladder in range(0, len(self.board)):
                cell = ""

                # All ladders are simple lists starting at index 0. Calculate which logical row we are
                # currently printing for the current ladder. This may lie outside of the range of the
                # ladder! 
                logicalrow = len(self.board[ladder]) - row + abs(ladder - len(self.board) // 2) - 1
                
                if (logicalrow == len(self.board[ladder])) or (logicalrow == -1):
                    # Top or bottom, just one out from valid indices. Print the number of the ladder.
                    cell = str(ladder+2).center(COLWIDTH)

                elif (logicalrow >= 0) and (logicalrow < len(self.board[ladder])):
                    # Valid index. Print the pieces that are placed here. 
                    pieces = ""

                    # First all the pieces that are already stuck down.
                    for piece in self.board[ladder][logicalrow]:
                        pieces += (self.PLAYER_INFO[piece][1] if colorize else "") + ("●" if colorize else str(piece)) + (colorama.Fore.WHITE if colorize else "")

                    # Is there an in-flight piece here?
                    add_in_flight = 0
                    if self.position_in_ladder_in_flight(ladder) == logicalrow:
                        pieces += (colorama.Fore.WHITE if colorize else "") + "●" # "◌"
                        add_in_flight = 1

                    # Pad the piece-string to center it. We cannot use string.center() because there are
                    # ANSI-Sequences for the coloring. But we know how many actual pieces there are.
                    for i in range(add_in_flight + len(self.board[ladder][logicalrow]), 3):
                        if (i%2) != 0:
                            pieces = " " + pieces
                        else:
                            pieces = pieces + " "

                    # Wrap the cell
                    cell = "(" + pieces + ")"
                else:
                    # Invalid index, output blank cell
                    cell = " " * COLWIDTH   

                # Add current cell to line and space from the next column.
                line += cell + " " * COLSPACE

            # Print the finished line.
            print((" " * INDENT) + line)

            # Build another line of output for the separators
            line = ""

            for ladder in range(0, len(self.board)):
                # Same as for cells, only simpler as there can only be the line or a blank.
                logicalrow = len(self.board[ladder]) - row + abs(ladder - len(self.board) // 2) - 1
                
                if (logicalrow > 0) and (logicalrow < len(self.board[ladder])):
                    cell = "|"
                else:
                    cell = " "
                                        
                cell = cell.center(COLWIDTH, " ")
                line += cell + " " * COLSPACE
                
            print((" " * INDENT) + line)

        # If we have thrown dice print the list
        if (self.dice):
            print("Thrown: " + str(self.dice))
        else:
            print()

colorama.init(autoreset = True)