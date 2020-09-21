"""
This module contains classes and functions to handle dihedral benchmarks.
"""


class DihedralBenchmark(object):
    """
    It defines a certain dihedral and allows to run several benchmarks
    on it.
    """

    def __init__(self, dihedral_atom_indexes, molecule):
        """
        It initializes a DihedralBenchmark object.

        Parameters
        ----------
        dihedral_atom_indexes : tuple[int]
            The indexes of atoms involved in the dihedral
        molecule : an offpele.topology.Molecule
            The offpele's Molecule object
        """

        self._atom_indexes = dihedral_atom_indexes
        self._molecule = molecule

    def generate_dihedral_conformers(self, resolution):
        """
        Given a resolution, it generates all the possible conformers
        that come out when rotating the dihedral's rotatable bond.

        Parameters
        ----------
        resolution : float
            The resolution, in degrees, that is applied when rotating
            the dihedral rotatable bond. Default is 30 degrees

        Returns
        -------
        rdkit_mol : an rdkit.Chem.rdchem.Mol object
            The RDKit's Molecule object with the conformers that were
            generated
        """
        from copy import deepcopy
        from rdkit.Chem import rdMolTransforms

        rdkit_mol = deepcopy(self.molecule.rdkit_molecule)

        conformer = rdkit_mol.GetConformer()

        theta = rdMolTransforms.GetDihedralDeg(conformer, *self.atom_indexes)

        for angle in range(0, 360, resolution):
            rdMolTransforms.SetDihedralDeg(conformer, *self.atom_indexes,
                                           theta + angle)
            rdkit_mol.AddConformer(conformer, assignId=True)

        # Remove initial conformer (which is repeated)
        rdkit_mol.RemoveConformer(conformer.GetId())

        return rdkit_mol

    def save_dihedral_conformers(self, resolution=30):
        """
        It saves the dihedral conformers that are obtained when
        rotating the dihedral's rotatable bond with a certain resolution.

        Parameters
        ----------
        resolution : float
            The resolution, in degrees, that is applied when rotating
            the dihedral rotatable bond. Default is 30 degrees
        """
        mol_with_conformers = self.generate_dihedral_conformers(resolution)

        from rdkit import Chem

        # Write structures
        w = Chem.SDWriter('conformers.sdf')
        for i, conf in enumerate(mol_with_conformers.GetConformers()):
            tm = Chem.Mol(mol_with_conformers, False, conf.GetId())
            w.write(tm)
        w.close()

    def plot(self, resolution=30):
        """
        It plots the dihedral
        """

    @property
    def atom_indexes(self):
        """
        The indexes of atoms involved in the dihedral.

        Returns
        -------
        atom_indexes : tuple[int]
            The tuple of atom indexes
        """
        return self._atom_indexes

    @property
    def molecule(self):
        """
        The molecule the dihedral belongs to.

        Returns
        -------
        molecule : an offpele.topology.Molecule
            The offpele's Molecule object
        """
        return self._molecule

    @property
    def rotatable_bond(self):
        """
        It returns the atom indexes in the dihedral that belong to the
        rotatable bond.

        Returns
        -------
        rot_bond : tuple[int]
        The tuple of atom indexes
        """
        return tuple(list(self.atom_indexes)[1:3])