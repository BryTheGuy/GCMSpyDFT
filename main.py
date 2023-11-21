import argparse
import logging
import os
import pathlib
import sys


def command_line():
    parser = argparse.ArgumentParser(
        prog="DFT_GC-MS",
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
    logger_setting = logging.getLogger('pyDFT')
    # Logging setup
    logger_setup = logging.getLogger('pyDFT')
    logger_setup.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = logging.FileHandler('pyDFT.log', mode='w')
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
    from config import cgf
    configuration_logger = logging.getLogger('pyDFT')
    # checks if configuration file exist
    if os.path.isfile(cgf.config_path):
        configuration_logger.info("Config file found, loading settings...")
        cgf.read_config()
    # if configuration file does not exist
    else:
        configuration_logger.info("Config file not found, writing settings...")
        cgf.make_config(cgf.config_path)
        cgf.read_config()


if __name__ == '__main__':
    # run things
    args = command_line()
    log_settings(args)
    logger = logging.getLogger('pyDFT')
    logger.debug("Starting configuration")
    configuration(args)
