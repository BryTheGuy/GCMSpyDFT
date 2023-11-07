import configparser
import os.path


class Config:
    config_path = "./config.ini"

    def make_config(self):
        if os.path.isfile(self.config_path):
            print("Config file found, loading settings...")

        elif not os.path.isfile(self.config_path):
            config = configparser.ConfigParser()
            config['Environment'] = {
                "InputFile": './input.txt',
                "OutputDir": './output/',
            }
            config['File'] = {
                "Cores": '28',
                "Memory": '50GB',
                "Checkpoint": 'Yes',
                "OldCheckpoint": 'No',
            }
            config['Route'] = {
                "Theory": 'B3LYP',
                "Basis_Set": '6-31G',
                "Calc_Type": 'opt'
            }
            config['MoleculeSpec'] = {
                "Charge": '0',
                "Spin": '1'
            }
