from typing import Literal

from openbabel import openbabel, pybel
from py2opsin import py2opsin as opsin

from config import cgf


class Molecule:
    name: str
    name_no_space: str
    smiles: str
    cml: str
    mol: pybel.Molecule

    def name_strip(self):
        self.name_no_space = self.name.strip().replace(' ', '_')

    def name_to_smi(self):
        if not self.smiles:
            self.smiles = self.name_to_format('SMILES')

    def name_to_cml(self):
        if not self.cml:
            self.cml = self.name_to_format('CML')

    def name_to_format(
            self,
            out_format: Literal[
               "SMILES",
               "ExtendedSMILES",
               "CML",
               "InChI",
               "StdInChI",
               "StdInChIKey",] = cgf.opsin_format
            ) -> str | list:
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
            allow_acid=cgf.acid,
            allow_radicals=cgf.radicals,
            allow_bad_stereo=cgf.bad_stereo,
            wildcard_radicals=cgf.wildcard_radicals)

    def create(self):
        if not self.cml:
            self.name_to_cml()
        self.mol = pybel.readstring('cml', self.cml)

    def three_d(self):
        self.mol.addh()
        self.mol.make3D()
        self.mol.OBMol.Center()

    def change_charge(self, change_by):
        self.mol.OBMol.SetTotalCharge(self.mol.charge + change_by)

    def change_spin(self, change_by):
        self.mol.OBMol.SetTotalSpinMultiplicity(self.mol.spin + change_by)

    def write(self, path, out_format):
        self.mol.write(out_format, path)
