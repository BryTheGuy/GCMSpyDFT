import argparse
import pathlib
import sys

from config import cgf

parser = argparse.ArgumentParser(
    prog="DFT_GC-MS",
    description="Program to convert an output of a GC-MS run into \n"
                "computational chemistry input files.")

parser.add_argument('infile',
                    nargs='?',
                    type=argparse.FileType('r'),
                    default=sys.stdin,
                    help="Input file name.")

parser.add_argument('-v',
                    '--version',
                    action='version',
                    version='%(prog)s v0.1')

parser.add_argument('-V',
                    '--Verbose',
                    action='store_true')

parser.add_argument('-o',
                    '--output',
                    type=pathlib.Path,
                    help="Output directory.")

parser.add_argument('-c',
                    '--cores',
                    type=int,
                    help="Number of cpu cores.")

parser.add_argument('-m',
                    '--memory',
                    type=int,
                    help="Maximum allowed memory.")

parser.add_argument('-C',
                    '--checkpoint',
                    action='store_true',
                    help="Create checkpoint.")

parser.add_argument('-t',
                    '--theory',
                    type=str,
                    help="Functional method to use for all input files.")

parser.add_argument('-b',
                    '--basis',
                    type=str,
                    help="Basis set to use for all input files.")

parser.add_argument('-T',
                    '--type',
                    choices=["SP", "Opt", "Freq"],
                    nargs='*',
                    help="Calculation type to preform. eg. 'SP' = 'Single point'")

parser.add_argument('--charge',
                    type=int,
                    help="Total Charge to assign each molecules. Overrides predicted charge.")

parser.add_argument('--spin',
                    type=int,
                    help="Multiplicity spin to assign each molecule. Overrides predicted spin.")

parser.add_argument('-M',
                    '--modred',
                    type=str,
                    nargs='*',
                    help="Modify redundant internal coordinate definitions to include at the end of each input file")

args = parser.parse_args()

verbose_print = print if args.Verbose else lambda *a, **k: None

if args.output:
    cgf.output = args.output
elif args.cores:
    cgf.cores = args.cores
elif args.memory:
    cgf.memory = args.memory
elif args.checkpoint:
    cgf.memory = args.checkpoint
elif args.theory:
    cgf.theory = args.theory
elif args.basis:
    cgf.basis = args.basis
elif args.type:
    cgf.calc_type = args.type
elif args.charge:
    cgf.charge = args.charge
elif args.spin:
    cgf.spin = args.spin
elif args.modred:
    cgf.modred = args.modred
