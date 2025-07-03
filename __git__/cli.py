import argparse
import os
import data

def parse_args():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command") # add subcommands and store them in `args.commands`
    commands.required = True

    init_parser = commands.add_parser("init")
    init_parser.set_defaults(func=init)

    return parser.parse_args()

def init(args):
    data.init()
    print(f'Initialized empty __git__ repository in {os.getcwd()}')

if __name__ == "__main__":
    args = parse_args()
    args.func(args)

