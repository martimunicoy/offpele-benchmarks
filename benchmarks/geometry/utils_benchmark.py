# Local imports
from getter import QCPortal
from minimize import Minimizer
from offpelebenchmarktools.utils.pele import PELEBaseJob, PELEMinimization
from offpele.topology import Molecule
import MoleculeMinimized as MM

# External imports
import argparse
import os 
import pandas as pd 

class MinimizationBenchmark(object): 
    def __init__(self, dataset, out_folder):

        """
        It initializes a MinimizationBenchmark object. 

        Parameters: 
        ----------
        dataset: name of the collection you want to extract from QCPortal

        out_folder: str
                    name for the output folder


        Examples: 
        ----------

        >>> benchmark = MinimizationBenchmark(
                dataset = 'Kinase Inhibitors: WBO Distributions', 
                out_folder = 'SET1')
        >>> benchmark.run()
        """
        self.dataset = dataset
        self.out_folder = out_folder

    def _get_molecule_minimized(self, index):
        """
            It minimized the molecule using PELE's minimization. 
        """
        
        #Load  and parameterize the molecule 
        mol = Molecule(os.path.join(os.getcwd(), self.out_folder,'QM/' '{}.pdb'.format(index + 1)))
        mol.parameterize('openff_unconstrained-1.2.1.offxml',
                 charges_method='gasteiger')
        
        # Runs a PELE Minimization
        pele_minimization = PELEMinimization(
            PELE_exec='/home/municoy/builds/PELE/PELE-repo_serial/PELE-1.6',
            PELE_src='/home/municoy/repos/PELE-repo/',
            PELE_license='/home/municoy/builds/PELE/license')
        pele_minimization.run(mol)

    def _filter_structures(self, smiles_tag):
        """
            It filter structures to keep only those that employ one of the OpenFF dihedrals with a non null phase constant.
            Output:
            ------------
                - It the structure employs one of the OpenFF dihedrals with a non null phase constant: return True.
                - Else: return False
        """
        # Filter out all non interesting molecules
        from offpele.topology import Molecule
        from simtk import unit

        var = False
        print('SMILES', smiles_tag)
        mol = Molecule(smiles=smiles_tag)
        mol.parameterize('openff_unconstrained-1.2.1.offxml',
                            charges_method='gasteiger')
        for p in mol.propers:
            if p.phase not in (unit.Quantity(0, unit.degree),
                               unit.Quantity(180, unit.degree)):
                var = True
        return var

    def _get_dataset_structures(self, filter_angles):
        """
            It gets the Dataset from the QCPortal and saves in a folder the optimized molecules as PDB.
        """
        import qcportal as ptl

        # Get the optimization dataset
        client = ptl.FractalClient()
        ds = client.get_collection('OptimizationDataset', self.dataset)
        nmols = len(list(ds.data.records.keys()))

        # Initializes the QCPortal class
        qc_portal = QCPortal(n_proc=4)
        
        #Handles output paths
        os.mkdir(os.path.join(os.getcwd(), self.out_folder))
        set_folder = os.path.join(os.getcwd(), self.out_folder, 'QM')
        os.mkdir(set_folder)
        
        # Build the optimized molecule and save it as a PDB
        for index in range(nmols):
            if (index % 50) == 0 : print('{}/{} optimized molecules built'.format(index + 1, nmols))
            entry =  ds.get_entry(ds.df.index[index])
            if filter_angles: 
                if self._filter_structures(smiles_tag = entry.attributes.get('canonical_smiles')): 
                    qc_portal._parallel_struct_getter(ds, set_folder, index)
            else: 
                qc_portal._parallel_struct_getter(ds, set_folder, index)



    def run(self, filter_structures = False): 
        """
            It generates the folders for the optimized with QM structures to PDB files and these PDBs minnimized with PELE.
        """

        # Obtain the dataset  
        self._get_dataset_structures(filter_angles = filter_structures)

        # Gets the number of files to minimize
        nfiles = len(os.listdir(out_QM_folder, 'QM'))

        # Creates the output folder
        os.mkdir(os.path.join(os.getcwd(), out_QM_folder, 'PELE'))

        # Loads the molecules from the Dataset and runs a PELEMinimization
        for index in range(nfiles):
            path = out_QM_folder
            self._get_molecule_minimized(index = index)

    def compute_RMSD(self):
        """
            For a collection of structures, 
            it saves a CSV file with a dictionary of the RMSD comparison between PELE and QM minimized structures.
        """

        from rdkit.Chem import rdMolAlign
        from rdkit.Chem import rdmolfiles

        # Computes the RMSD between ∫PELE and QM minimized structures
        nfiles = len(os.listdir(sos.path.join(self.out_folder, 'QM')))
        d = {}
        for index in range(nfiles): 
            molQM = rdmolfiles.MolFromPDBFile(os.path.join(out_folder, 'QM/{}.pdb'.format(index)))
            molPELE = rdmolfiles.MolFromPDBFile(os.path.join(out_folder, 'PELE/{}/minimized.pdb'.format(index)))
            rsmd = rdMolAlign.AlignMol(molQM, molPELE)
            d.update(index=rsmd)
        
        # Writes out a CSV file with the dictionary of the RMSD results.
        df = pd.DataFrame(d.items(), columns=['Ligand ID', 'RMSD'])
        df.to_csv(os.path.join(self.out_folder,'rmsd.csv'))


