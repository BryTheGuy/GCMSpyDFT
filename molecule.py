from openbabel import openbabel
from cas_converter import name_to_format


class Molecule:
    name: str
    name_no_space: str
    smiles: str
    cml: str
    mol: openbabel.OBMol
    charge: int
    spin: int

    def generate_smi(self):
        if self.smiles:
            self.smiles = name_to_format(self.name, 'SMILES')

    def generate_cml(self):
        if self.cml:
            self.cml = name_to_format(self.name, 'CML')
