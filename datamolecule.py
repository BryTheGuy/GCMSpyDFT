import logging
from typing import Literal

from openbabel import openbabel, pybel
from py2opsin import py2opsin as opsin

from config import cfg

data_logger = logging.getLogger('GCMSpyDFT.datamolecule')


def make_structure(names: str | list,
                   out_format: Literal[
                       "SMILES",
                       "ExtendedSMILES",
                       "CML",
                       "InChI",
                       "StdInChI",
                       "StdInChIKey"] = cfg.opsin_format or 'CML'
                   ) -> str | list:
    """
    Input simplifier for py2opsin.

    Use list of names for batch processing as
    there is a performance boost.
    :param names: string or list of strings to be converted
    :param out_format: style in which molecules are returned e.g. CML, SMILES...
    :return: string or list of molecules in format
    """
    return opsin(
        chemical_name=names,
        output_format=out_format,
        allow_acid=cfg.acid,
        allow_radicals=cfg.radicals,
        allow_bad_stereo=cfg.bad_stereo,
        wildcard_radicals=cfg.wildcard_radicals)


class DataMolecule(pybel.Molecule):
    def __init__(self, name: str, OBMol: openbabel.OBMol = None, structure: str = None, reference_num: int = None,
                 cas_num: int = None, quality: int = None):
        self.logger = logging.getLogger('GCMSpyDFT.molecule.Molecule')
        self.logger.info(f'Creating new {name} molecule instance.')

        self.name = name
        self.name_no_space = self.name.strip().replace(' ', '_')
        self.structure: str = structure
        self.mol = pybel.readstring('cml', make_structure(self.name, 'CML'))
        self.reference_num: int = reference_num  # reference number of molecule
        self.cas_num: int = cas_num  # CAS numbers of molecule
        self.quality: int = quality  # quality of molecule

        # For the love of all that is good I cannot understand this, but it seems to work
        # FIXME: This needs a cleaning
        if OBMol is not None:
            self.logger.debug(f'Openbabel object provided for {name}')
            super().__init__(OBMol)
        else:
            self.logger.debug(f'Generating molecule object for {name}')
            try:
                structure = make_structure(self.name, 'CML')
            except Warning:
                self.logger.error(f'Molecule {self.reference_num} failed to from a structure')
            super().__init__(self.mol)

    def name_strip(self):
        self.name_no_space = self.name.strip().replace(' ', '_')

    # def name_to_smi(self):
    #     if not self.smiles:
    #         self.smiles = name_to_format('SMILES')

    # def name_to_cml(self):
    #     if not self.cml:
    #         self.cml = name_to_format('CML')

    def create(self, in_format: str = None):
        valid_opsin = ["SMILES", "ExtendedSMILES", "CML", "InChI", "StdInChI", "StdInChIKey"]

        if in_format is None and self.structure is None:
            in_format = 'cml'
            self.structure = make_structure(self.name)

        elif in_format in valid_opsin and self.structure is None:
            self.structure = make_structure(self.name, in_format)

        self.mol = pybel.readstring(in_format.lower(), self.structure)

    # def three_d(self):
    #     self.mol.addh()
    #     self.mol.make3D()
    #     self.mol.OBMol.Center()

    def change_charge(self, change_by):
        self.mol.OBMol.SetTotalCharge(self.mol.charge + change_by)

    def change_spin(self, change_by):
        self.mol.OBMol.SetTotalSpinMultiplicity(self.mol.spin + change_by)

    # def write(self, path, out_format):
    #     self.mol.write(out_format, path)
