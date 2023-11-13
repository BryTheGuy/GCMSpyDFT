from openbabel import openbabel, pybel
from py2opsin import py2opsin as opsin

import config

config_file = config.Config()


class Molecule:
    name: str
    name_no_space: str
    smiles: str
    cml: str
    mol: pybel.Molecule
    charge: int
    spin: int

    def name_strip(self):
        self.name_no_space = self.name.strip().replace(' ', '_')

    def name_to_smi(self):
        if not self.smiles:
            self.smiles = self.name_to_format('SMILES')

    def name_to_cml(self):
        if not self.cml:
            self.cml = self.name_to_format('CML')

    def name_to_format(self, out_format: str = config_file.opsin_format()) -> str | list:
        """
        Input simplifier for py2opsin.

        Use list of names for batch processing as
        there is a performance boost.
        :param out_format:
        :return:
        """
        return opsin(
            chemical_name=self.name,
            output_format=out_format,
            allow_acid=config_file.acid(),
            allow_radicals=config_file.radicals(),
            allow_bad_stereo=config_file.bad_stereo(),
            wildcard_radicals=config_file.wildcard_radicals())

