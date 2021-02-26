# This is a scaffolding using an instance of Environment allowing it to be played
# by humans in a console window. 

import logging
import argparse
import random
import sys
import os
import colorama

import environment
import agent as ag

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

    # Create and reset the environment
    env = environment.Environment()
    env.reset()

    # Set up agents:
    agents = [
        ag.RandomAgent(0),
        ag.RandomAgent(1),
        ag.RandomAgent(2)
    ]

    #human_index = random.randint(0,2)
    #agents[human_index] = ag.HumanAgent(human_index)

    while (env.winner == -1):
        
        # Print the current board.    
        env.render(options.colorize)

        # Find the agent whose turn it is.
        agent = agents[env.current_player]

        # Ask the agent for an action
        action = agent.pick_action(env)

        if action:
            # Take the action
            env.take_action(action)
        else:
            raise ValueError("Agent did not pick an action")

    # Render the final board.    
    env.render(options.colorize)

    logger.info('Finished.')
    
if __name__ == '__main__':

    main()
