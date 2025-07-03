import argparse
import os
import data

def parse_args():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command") # add subcommands and store them in `args.commands`
    commands.required = True

    init_parser = commands.add_parser("init")
    init_parser.set_defaults(func=init)

    hash_object_parser = commands.add_parser("hash-object")
    hash_object_parser.set_defaults(func=hash_object)
    hash_object_parser.add_argument("file")

    return parser.parse_args()

def init(args):
    data.init()
    print(f'Initialized empty __git__ repository in {os.getcwd()}')

def hash_object(args):
    with open(args.file, "rb") as file:
        print(data.hash_object(file.read()))

if __name__ == "__main__":
    args = parse_args()
    args.func(args)

