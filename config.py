import configparser
import os.path


class Config:

    def __init__(self):
        self.config_path = "./config.ini"

    def make_config(self):
        if os.path.isfile(self.config_path):
            print("Config file found, loading settings...")

        elif not os.path.isfile(self.config_path):
            config = configparser.ConfigParser()
            config['Environment'] = {
                "Input File": './input.txt',
                "Output Dir": './output/',
            }
            config['File'] = {
                "Cores": '28',
                "Memory": '50GB',
                "Checkpoint": 'Yes',
                "Old Checkpoint": 'No',
            }
            config['Route'] = {
                "Theory": 'B3LYP',
                "Basis Set": '6-31G',
                "Calc Type": 'opt'
            }
            config['Molecule Specs'] = {
                "Charge": '0',
                "Spin": '1'
            }

            with open(self.config_path, 'w') as config_file:
                config.write(config_file)


if __name__ == '__main__':
    f = Config()
    f.make_config()
