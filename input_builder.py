from openbabel import openbabel as ob, pybel as pb


class InputBuilder:  # TODO wip name not 'builder' function

    def cast_to_gau(self):
        pymol = pb.readstring('cml', self)
        pymol.addh()
        pymol.make2D()
        pymol.make3D()
        return pymol.write()
