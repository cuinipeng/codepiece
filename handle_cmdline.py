#!/usr/bin/env python
import os.path
import argparse
import collections
import multiprocessing

Result = collections.namedtuple('Result', ['copied', 'scaled', 'name'])
Summary = collections.namedtuple('Summary', ['todo', 'copied', 'scaled', 'canceld'])

def handle_cmdline():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--concurrency', type=int,
        default=multiprocessing.cpu_count(),
        help='specify the concurrency (for debug and timing) [default: %(default)d]')
    parser.add_argument('-s', '--size', type=int, default=400,
        help='make a scaled image that fits the given dimension [default: %(default)d]')
    parser.add_argument('-S', '--smooth', action='store_true',
        help='use smooth scaling (slow but good for text)')
    parser.add_argument('source', help='the directory containing the original .xpm images')
    parser.add_argument('target', help='the directory for scaled .xpm images')
    args = parser.parse_args()

    source = os.path.abspath(args.source)
    target = os.path.abspath(args.target)
    if source == target:
        parser.error('source and target must be different')
    if not os.path.exists(target):
        os.makedirs(target)

    return args

def main():
    # handle_cmdline()
    pass

if __name__ == '__main__':
    main()