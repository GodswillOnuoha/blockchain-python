from argparse import ArgumentParser

from blockchain import create_node

parser = ArgumentParser()
parser.add_argument('-p', '--port', default=3000)

args = parser.parse_args()


node = create_node()
node.start(port=args.port)
