import argparse
import logging
import os
import pathlib
import sys

from molecule import make_structure, Molecule


def command_line():
    parser = argparse.ArgumentParser(
        prog="GC-MS -> DFT",
        description="Program to convert an output of a GC-MS run into computational chemistry input files.")

    group = parser.add_mutually_exclusive_group()

    group.add_argument("-v",
                       "--verbosity",
                       action="store_true",
                       help="make verbose")

    group.add_argument("-q",
                       "--quiet",
                       action="store_true",
                       help="silence output")

    parser.add_argument('infile',
                        nargs='?',
                        type=argparse.FileType('r'),
                        default=sys.stdin,
                        help="Input file name.")

    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='%(prog)s v0.1')

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
                        help="Modify redundant internal coordinate definitions to be include at "
                             "the end of each input file.")

    return parser.parse_args()


def log_settings(arguments):
    logger_setting = logging.getLogger('GCMSpyDFT')
    # Logging setup
    logger_setup = logging.getLogger('GCMSpyDFT')
    logger_setup.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = logging.FileHandler('GCMSpyDFT.log', mode='w')
    fh.setLevel(level=logging.DEBUG)
    # create formatter and add it to the handlers
    fh_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(fh_formatter)
    # add the handlers to the logger
    logger_setup.addHandler(fh)

    # create console handler
    ch = logging.StreamHandler()
    # create formatter and add it to the handlers
    ch_formatter = logging.Formatter('%(levelname)s: %(message)s')
    ch.setFormatter(ch_formatter)
    if arguments.verbosity:
        # create console handler with a higher log level
        ch.setLevel(logging.INFO)
        logger_setting.addHandler(ch)
        logger_setting.debug("Cavitation")
    elif arguments.quiet:
        # create console handler with no logging
        ch.setLevel(logging.CRITICAL + 1)
        logger_setting.addHandler(ch)
        logger_setting.debug("Quite running")
    else:
        # create console handler with a default log level
        ch.setLevel(logging.WARNING)
        logger_setting.addHandler(ch)
        logger_setting.debug("Plain bagel")


def configuration(arguments):
    from config import cfg
    configuration_logger = logging.getLogger('GCMSpyDFT')
    # checks if configuration file exist
    if os.path.isfile(cfg.config_path):
        configuration_logger.info("Config file found, loading settings...")
        cfg.read_config()
    # if configuration file does not exist
    else:
        configuration_logger.info("Config file not found, writing settings...")
        cfg.make_config(cfg.config_path)
        cfg.read_config()


def settings(arguments):
    from config import cfg
    if args.output:
        cfg.output = args.output
    elif args.cores:
        cfg.cores = args.cores
    elif args.memory:
        cfg.memory = args.memory
    elif args.checkpoint:
        cfg.memory = args.checkpoint
    elif args.theory:
        cfg.theory = args.theory
    elif args.basis:
        cfg.basis = args.basis
    elif args.type:
        cfg.calc_type = args.type
    elif args.charge:
        cfg.charge = args.charge
    elif args.spin:
        cfg.spin = args.spin
    elif args.modred:
        cfg.modred = args.modred


def read_input_file(file: str) -> list[list[str]]:
    file_reader_logger = logging.getLogger('GCMSpyDFT')

    import gcms_interpreter as gi
    lines = gi.read_to_list(file)

    if header_line := gi.content_finder(lines) != -1:
        file_reader_logger.debug(f'Found header for file {file} at line {header_line}.')
        trimmed_lines = gi.trim_header(lines, header_line)

    else:
        file_reader_logger.warning(f'Assuming there is no header in file {file}')
        trimmed_lines = gi.trim_header(lines, 0)

    return gi.peak_agg(trimmed_lines)


def parse_peaks(peak_lines: list[list[str]]) -> list[object]:
    from peaks import Peak

    list_of_peaks: list[object] = []
    for lines in peak_lines:

        current_peak = Peak(lines)
        current_peak.peak_header()
        current_peak.left_align()
        current_peak.add_separator()
        current_peak.combine_lines()
        current_peak.parse_lines()

        list_of_peaks.append(current_peak)

    return list_of_peaks


def create_molecules(names: list[str], structures: list[str]) -> list[Molecule]:
    # TODO: added charge and spin maybe?
    from molecule import Molecule

    molecule_list: list[Molecule] = []

    for name, structure in zip(names, structures):
        current_mol = Molecule(name, structure)
        current_mol.addh()
        current_mol.make2D()
        current_mol.make3D()
        current_mol.OBMol.Center()

        molecule_list.append(current_mol)

    return molecule_list


def run():
    from config import cfg
    peak_blocks: list[list[str]] = read_input_file(args.infile)  # collection of lines organized by peak

    peak_list: list[object] = parse_peaks(peak_blocks)  # collection of peak objects

    for peak in peak_list:
        mol_names: list = getattr(peak, 'ID')
        mol_structures = make_structure(mol_names)  # expect CML structure
        peak_molecules: list[Molecule] = create_molecules(mol_names, mol_structures)
        for i, peak_molecule in enumerate(peak_molecules):

            # output/PK#-RT-area%/ref-cas-qual/name.gau
            file_path = (f'{cfg.output}/'
                         f'{getattr(peak_molecule, "peak_num")}'
                         f'-{getattr(peak_molecule, "retention_time")}'
                         f'-{getattr(peak_molecule, "percent_area")}/'
                         f'{getattr(peak_molecule, "reference_num")[i]}'
                         f'-{getattr(peak_molecule, "cas_num")[i]}'
                         f'-{getattr(peak_molecule, "quality")[i]}/'
                         f'{getattr(peak_molecule, "name_no_space")}')

            # %cores=1 \n %mem=50 \n %check=name_[calc_type]
            header = (f'%NProcShared={cfg.cores}\n'
                      f'%mem={cfg.memory}\n'
                      f'%chk={getattr(peak_molecule, "name")}_{cfg.calc_type}.chk\n')

            # #p theory/basis calc_type
            keywords = f'#p {cfg.theory}/{cfg.basis} {[calc for calc in cfg.calc_type]}'

            peak_molecule.title = peak_molecule.name + ' ' + cfg.calc_type + ' GCMSpyDFT'

            peak_molecule.write(format='gau', filename=file_path, opt=header+keywords)


if __name__ == '__main__':
    # run things
    args = command_line()
    log_settings(args)
    logger = logging.getLogger('GCMSpyDFT')
    logger.debug("Starting configuration")
    configuration(args)
    logger.debug("Starting settings")
    settings(args)
    logger.debug("Starting runself.reference_nums: list[int] = []  # list of all reference numbers in peak")
    run()
