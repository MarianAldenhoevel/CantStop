import logging
import random
import sys
import colorama

import environment

class Agent():
    
    def __init__(self, player_num):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug('__init__')

        self.player_num = player_num

    def pick_action(self, environment):
        self.logger.debug('pick_action()')

        return None

class RandomAgent(Agent):

    def __init__(self, player_num):
        super().__init__(player_num)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug('__init__')
        
    def pick_action(self, environment):
        self.logger.debug('pick_action()')

        if environment.actions:
            return random.choice(environment.actions)
        else:
            return None

class HumanAgent(Agent):

    def __init__(self, player_num):
        super().__init__(player_num)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug('__init__')

    def pick_action(self, environment):
        self.logger.debug('pick_action()')

        # Print the current board.
        colorize = True    
        environment.render(colorize)

        selected_action = None

        # Repeat until a valid selection is made.
        while not selected_action:
            
            # Print the list of available actions as a menu.
            
            # Menu title:
            print()
            print((environment.PLAYER_INFO[environment.current_player][1] if colorize else "") + "Select action for player #{n} ({name}):".format(
                n = environment.current_player,
                name = environment.PLAYER_INFO[environment.current_player][0]) + (colorama.Fore.WHITE if colorize else "") 
            )

            # List of actions:
            i = 0
            for action in environment.actions:
                i += 1
                print('    {i}: {action}'.format(i = i, action = action[0]))
            
            # Add the fixed action to quit the program. That is extraneous to the environment.
            print('    x: Quit game')

            # Read input.
            proposed_action_index = input()
            try: 
                # Is it an integer?
                proposed_action_index_int = int(proposed_action_index)-1
                # Yes. Is the integer valid? 
                if (proposed_action_index_int >= 0) and (proposed_action_index_int < len(environment.actions)):
                    selected_action = environment.actions[proposed_action_index_int]

            except ValueError:
                # Not an integer. Check for x to quit. If not 'x' this is not a valid action. 
                if proposed_action_index.lower() == 'x':
                    selected_action = 'x'

            # Report mis-selection
            if not selected_action:
                print((colorama.Fore.RED if colorize else "") + "Invalid action selected, please try again.")

        # Act on the user-selection. Either quit the program or return the selected action to the runner. 
        if selected_action == 'x':
            self.logger.info('User selected quit')
            sys.exit(1)
        else:
            return selected_action
