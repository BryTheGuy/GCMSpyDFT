import argparse
import logging
import os
import pathlib
import sys
import warnings
from io import TextIOWrapper

from datamolecule import make_structure, DataMolecule


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
                        # nargs='?',
                        type=argparse.FileType('r'),
                        # default=sys.stdin,
                        help="Input file name.")

    parser.add_argument('-V',
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

    parser.add_argument('--modred',
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


def read_input_file(file: TextIOWrapper) -> list[list[str]]:
    file_reader_logger = logging.getLogger('GCMSpyDFT')

    import interpreter as gi
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


def create_molecules(names: list[str], structures: list[str]) -> list[DataMolecule]:
    # TODO: added charge and spin maybe?
    from datamolecule import DataMolecule

    molecule_list: list[DataMolecule] = []

    for name, structure in zip(names, structures):
        current_mol = DataMolecule(name, structure)
        current_mol.mol.addh()
        current_mol.mol.make2D()
        current_mol.mol.make3D()
        current_mol.mol.OBMol.Center()

        molecule_list.append(current_mol)

    return molecule_list


def run() -> list[str]:
    from config import cfg
    warnings.simplefilter('error')

    peak_blocks: list[list[str]] = read_input_file(args.infile)  # collection of lines organized by peak

    peak_list: list[object] = parse_peaks(peak_blocks)  # collection of peak objects
    failed_names: list[str] = []

    for peak in peak_list:
        mol_names: list = getattr(peak, 'ID')

        mol_structures: list[str] = []
        success_names: list[str] = []
        data_molecule: list = []  # FIXME: rename

        for i, mol_name in enumerate(mol_names):
            try:
                structure = make_structure(mol_name)
                mol_structures.append(structure)
                success_names.append(mol_name)
                logger.info(f'{cfg.OKCYAN} Success! {mol_name} is now a structure! {cfg.ENDC}')
                # print(structure)
                data_molecule.append((mol_name, structure, i))
            except Warning as w:
                failed_names.append(mol_name)
                logger.warning(f'{cfg.FAIL} FAIL! {cfg.UNDERLINE}{mol_name}{cfg.SUNDERLINE} threw an error!\n'
                               f'{cfg.WARNING} {str(w).strip()} {cfg.ENDC}')

        # mol_structures = make_structure(mol_names)
        peak_molecules: list[DataMolecule] = create_molecules(success_names, mol_structures)
        # peak_molecules: list[DataMolecule] = create_molecules(*data_molecule)
        for i, peak_molecule in enumerate(peak_molecules):
            folder_path = (f'{cfg.output}/'
                           f'{getattr(peak, "peak_num")}'
                           f'-{getattr(peak, "retention_time")}'
                           f'-{getattr(peak, "percent_area")}/'
                           f'{getattr(peak, "reference_nums")[i]}'
                           f'-{getattr(peak, "cas_nums")[i]}'
                           f'-{getattr(peak, "qualities")[i]}/')

            if not os.path.isdir(folder_path):
                os.makedirs(folder_path)

            # output/PK#-RT-area%/ref-cas-qual/name.gau
            file_path = (f'{cfg.output}/'
                         f'{getattr(peak, "peak_num")}'
                         f'-{getattr(peak, "retention_time")}'
                         f'-{getattr(peak, "percent_area")}/'
                         f'{getattr(peak, "reference_nums")[i]}'
                         f'-{getattr(peak, "cas_nums")[i]}'
                         f'-{getattr(peak, "qualities")[i]}/'
                         f'{getattr(peak_molecule, "name_no_space")}'
                         f'.inp')

            # %cores=1 \n %mem=50 \n %check=name_[calc_type]
            header = (f'%NProcShared={cfg.cores}\n'
                      f'%mem={cfg.memory}\n'
                      f'%chk={getattr(peak_molecule, "name")}_{",".join(cfg.calc_type).lower()}.chk\n')

            # #p theory/basis calc_type
            keywords = f'\n#p {cfg.theory}/{cfg.basis} ({",".join(cfg.calc_type)})'

            peak_molecule.mol.title = peak_molecule.name + ' ' + '/'.join(cfg.calc_type).strip() + ' GCMSpyDFT'

            peak_molecule.mol.write(format='gau', filename=file_path, opt={'k': header + keywords}, overwrite=True)

    warnings.resetwarnings()
    return failed_names


if __name__ == '__main__':
    # run things
    args = command_line()
    log_settings(args)
    logger = logging.getLogger('GCMSpyDFT')
    logger.info("Starting configuration")
    configuration(args)
    logger.info("Starting settings")
    settings(args)
    logger.info("Starting run")
    if failed := run():
        logger.error(f'List of molecules that failed to form structures. {failed}')

