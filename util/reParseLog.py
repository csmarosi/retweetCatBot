#!/usr/bin/env python3

import argparse
import json


def writeData(partial, args):
    first = partial[0]
    last = partial[-1]
    fileName = args.outPrefix + '_' + str(first['created_at']) + '-' + str(
        last['created_at'])
    with open(fileName, 'w') as fp:
        json.dump(partial, fp, indent=2, separators=(',', ': '))


def parseData(data, partial, args):
    jsonCandidate = ''
    for line in data:
        if '}' == line[0]:
            jsonCandidate += '}'
            partial.append(json.loads(jsonCandidate))
            if len(partial) >= args.numberPerFile:
                writeData(partial, args)
                partial = []
            jsonCandidate = '{'
        else:
            jsonCandidate += line
    return partial


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i',
                        '--inputFiles',
                        nargs='+',
                        required=True,
                        help='Input files to parse, must be ordered')
    parser.add_argument('-n',
                        '--numberPerFile',
                        type=int,
                        default=56000,
                        help='Number of tweets per output file')
    parser.add_argument('-o',
                        '--outPrefix',
                        type=str,
                        default='ReplayFile',
                        help='The prefix for the output')
    args = parser.parse_args()

    partial = []
    for inputFile in args.inputFiles:
        with open(inputFile, 'r') as data:
            partial = parseData(data, partial, args)
    writeData(partial, args)


if __name__ == "__main__":
    main()
