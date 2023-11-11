import argparse

parser = argparse.ArgumentParser(
    description="Program to convert an output of a GCMS run into \n"
                "computational chemistry input files.")

parser.add_argument('filename',
                    type=str,
                    help="Input file name.")

parser.add_argument('-o',
                    '--output',
                    type=str,
                    help="Output directory.")

parser.add_argument()

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
                    default='Opt',
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
                    help="Modify redundant internal coordinate definitions to include at the end of each input file")
