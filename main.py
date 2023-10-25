import argparse

parser = argparse.ArgumentParser(
    description="Program to convert an output of a GCMS run into \n"
                "computational chemistry input files.")
parser.add_argument('filename',
                    type=str)

parser.add_argument('-o',
                    '--output',
                    type=str)

parser.add_argument()

parser.add_argument('-c',
                    '--cores',
                    type=int)

parser.add_argument('-m',
                    '--memory',
                    type=int)

parser.add_argument('-C',
                    '--checkpoint',
                    action='store_true')

parser.add_argument('-t',
                    '--theory')

parser.add_argument('-b',
                    '--basis_set',
                    type=str)

parser.add_argument('-T',
                    '--calc_type',
                    default='opt',
                    nargs='*',
                    type=str)

parser.add_argument('--charge',
                    type=int)

parser.add_argument('--spin',
                    type=int)

parser.add_argument('-M',
                    '--modred',
                    type=str)
