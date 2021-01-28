from natex import NatEx
import argparse

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Configure NatEx local installation using the `setup` sub-command')
	parser.add_argument('command', help='setup')
	parser.add_argument('param', metavar='N', nargs='+')
	args = parser.parse_args()

	if args.command == 'setup':
		NatEx.setup(args.param)