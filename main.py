import argparse
import pathlib
import sys

import config
import os


config_file = config.Config()

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
                    default=config_file.output,
                    help="Output directory.")

parser.add_argument('-c',
                    '--cores',
                    type=int,
                    default=config_file.cores,
                    help="Number of cpu cores.")

parser.add_argument('-m',
                    '--memory',
                    type=int,
                    default=config_file.memory,
                    help="Maximum allowed memory.")

parser.add_argument('-C',
                    '--checkpoint',
                    action='store_true',
                    default=config_file.checkpoint,
                    help="Create checkpoint.")

parser.add_argument('-t',
                    '--theory',
                    type=str,
                    default=config_file.theory,
                    help="Functional method to use for all input files.")

parser.add_argument('-b',
                    '--basis',
                    type=str,
                    default=config_file.basis,
                    help="Basis set to use for all input files.")

parser.add_argument('-T',
                    '--type',
                    choices=["SP", "Opt", "Freq"],
                    default=config_file.calc_type,
                    nargs='*',
                    help="Calculation type to preform. eg. 'SP' = 'Single point'")

parser.add_argument('--charge',
                    type=int,
                    default=config_file.charge,
                    help="Total Charge to assign each molecules. Overrides predicted charge.")

parser.add_argument('--spin',
                    type=int,
                    default=config_file.spin,
                    help="Multiplicity spin to assign each molecule. Overrides predicted spin.")

parser.add_argument('-M',
                    '--modred',
                    type=str,
                    default=config_file.modred,
                    nargs='*',
                    help="Modify redundant internal coordinate definitions to include at the end of each input file")

args = parser.parse_args()

verbose_print = print if args.verbose else lambda *a, **k: None

if args.output:
    config_file.output = args.output
elif args.cores:
    config_file.cores = args.cores
elif args.memory:
    config_file.memory = args.memory
elif args.checkpoint:
    config_file.memory = args.checkpoint
elif args.theory:
    config_file.theory = args.theory
elif args.basis:
    config_file.basis = args.basis
elif args.type:
    config_file.calc_type = args.type
elif args.charge:
    config_file.charge = args.charge
elif args.spin:
    config_file.spin = args.spin
elif args.modred:
    config_file.modred = args.modred
