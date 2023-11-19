import configparser
import os.path
import pathlib
from main import verbose_print


class Config:
    config_path: str
    filename: str
    output: pathlib.Path

    opsin_format: str
    acid: bool
    radicals: bool
    bad_stereo: bool
    wildcard_radicals: bool

    cores: int
    memory: int
    checkpoint: bool
    theory: str
    basis: str
    calc_type: list
    charge: int
    spin: int
    modred: list

    def __init__(self, config_path: str = "./config.ini"):
        """
        Initialize config class with path of existing file, or if one does not exist
        create a new file and read it.

        :param config_path:
        """
        self.config_path = config_path

        if os.path.isfile(config_path):
            verbose_print("Config file found, loading settings...")
            self.read_config()
        else:
            verbose_print("Config file not found, writing settings...")
            self.make_config(config_path)
            self.read_config()

    def __str__(self):
        return str(self.__class__) + '\n' + '\n'.join(
            ('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__))

    def read_config(self):
        config = configparser.ConfigParser()
        config.read(self.config_path)
        # all variables to read from file into config class
        self.filename = config['Environment']['input file']
        self.output = pathlib.Path(config['Environment']['output dir'])

        # OPSIN Settings
        self.opsin_format = config['OPSIN']['output format']
        self.acid = config.getboolean('OPSIN', 'allow acid')
        self.radicals = config.getboolean('OPSIN', 'allow radicals')
        self.bad_stereo = config.getboolean('OPSIN', 'allow bad stereo')
        self.wildcard_radicals = config.getboolean('OPSIN', 'wildcard radicals')

        # Gaussian file header
        self.cores = int(config['File']['cores'])
        self.memory = int(config['File']['memory'])
        self.checkpoint = config.getboolean('File', 'checkpoint')
        # old checkpoint ?

        # Gaussian route commands
        self.theory = config['Route']['theory']
        self.basis = config['Route']['basis set']
        self.calc_type = config['Route']['calc type'].split(',')

        self.charge = int(config['Molecule Specs']['charge'])
        self.spin = int(config['Molecule Specs']['spin'])

    def make_config(self, config_path="./config.ini"):
        self.config_path = config_path
        config = configparser.ConfigParser()
        # Added categorises and variables to be added to config file here.
        config['Environment'] = {
            "Input File": './input.txt',
            "Output Dir": './output/',
        }
        config['OPSIN'] = {
            "Output Format": 'SMILES',
            "Allow Acid": 'Yes',
            "Allow Radicals": 'Yes',
            "Allow Bad Stereo": 'No',
            "Wildcard Radicals": 'No'
        }
        config['File'] = {
            "Cores": '28',
            "Memory": '50',
            "Checkpoint": 'Yes',
            "Old Checkpoint": 'No',
        }
        config['Route'] = {
            "Theory": 'B3LYP',
            "Basis Set": '6-31G',
            "Calc Type": 'Opt'
        }
        config['Molecule Specs'] = {
            "Charge": '0',
            "Spin": '1'
        }

        with open(config_path, 'w') as config_file:
            config.write(config_file)


        self.charge = config['Molecule Specs']['charge']
        self.spin = config['Molecule Specs']['spin']


if __name__ == '__main__':
    f = Config()
    print(f)
