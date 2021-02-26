import logging
import argparse
import random
import sys
import os
import colorama

import environment

options = None

# Conversion function for argparse booleans
def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

# Set up argparse and get the command line options.
def parse_commandline():

    global options

    parser = argparse.ArgumentParser(
        description = 'This is an implementation of the board game "can''t stop".', 
        epilog = 'Remember to be nice!'
    )

    parser.add_argument('-ll', '--log-level',
        action = 'store',
        default = 'INFO',
        help ='Set the logging output level to CRITICAL, ERROR, WARNING, INFO or DEBUG (default: %(default)s)',
        dest ='log_level',
        metavar = 'level'
    )

    parser.add_argument('-co', '--colorize',
        action = 'store',
        default = True,
        type = str2bool,
        help ='Select colorized output (default: %(default)s)',
        dest ='colorize',
        metavar = 'colorize'
    )

    parser.add_argument('-cs', '--clear-screen',
        action = 'store',
        default = True,
        type = str2bool,
        help ='Clear screen before rendering each turn (default: %(default)s)',
        dest ='clearscreen',
        metavar = 'clearscreen'
    )

    parser.add_argument('-rs', '--random-seed',
        action = 'store',
        default = None,
        help = 'Set random seed to make dice rolls reproducible',
        dest ='randseed',
        metavar = 'randseed'
    )

    options = parser.parse_args()
    options.log_level_int = getattr(logging, options.log_level, logging.INFO)

    if options.randseed:
        random.seed(options.randseed)

# Set up a logger each for a file in the output folder and the console.      
def setup_logging():
  
    global options
  
    fh = logging.FileHandler(os.path.dirname(os.path.realpath(__file__)) + '\\manual.log')
    fh.setLevel(options.log_level_int)

    ch = logging.StreamHandler()
    ch.setLevel(options.log_level_int)

    ch.setFormatter(logging.Formatter('({thread}) [{levelname:7}] {name} - {message}', style='{'))
    fh.setFormatter(logging.Formatter('{asctime} ({thread}) [{levelname:7}] {name} - {message}', style='{'))

    root = logging.getLogger()
    root.addHandler(ch)
    root.addHandler(fh)
    root.setLevel(logging.DEBUG)

def main():
    global options

    # So we can redirect full Unicode even in Windows.
    sys.stdout.reconfigure(encoding='utf-8')

    parse_commandline()
    setup_logging()

    logger = logging.getLogger('Main')
    logger.info('Starting.')

    env = environment.Environment()
    
    env.reset()
    user_abort = False

    while (not user_abort):
        
        selected_action = None

        if options.clearscreen:
            colorama.ansi.clear_screen()
        
        env.render(options.colorize)

        while not selected_action:
            print()

            if env.winner != -1:
                print("Select action:")
            else:
                print((env.PLAYER_INFO[env.current_player][1] if options.colorize else "") + "Select action for player #{n} ({name}):".format(
                        n = env.current_player,
                        name = env.PLAYER_INFO[env.current_player][0]) + (colorama.Fore.WHITE if options.colorize else "") 
                )

            actions = env.actions
            i = 0
            for action in actions:
                i += 1
                print('    {i}: {action}'.format(i = i, action = action[0]))
            print('    x: Quit game')

            proposed_action_index = input()
            try: 
                proposed_action_index_int = int(proposed_action_index)-1
                if (proposed_action_index_int >= 0) and (proposed_action_index_int < len(actions)):
                    selected_action = actions[proposed_action_index_int]

            except ValueError:
                if proposed_action_index.lower() == 'x':
                    selected_action = 'x'

            if not selected_action:
                print((colorama.Fore.RED if options.colorize else "") + "Invalid action selected, please try again.")

        if selected_action == 'x':
            logger.info('User selected quit')
            user_abort = True
        else:
            env.take_action(selected_action)

    logger.info('Finished.')
    
if __name__ == '__main__':

    main()
