import periodictable

def Label_of_System(args):
    return f"""############################################################Label of System############################################################ 
             
SystemName {args.label}     
SystemLabel {args.label}"""

def Input_Parameters(args):
    if args.elements is not None:
        elements = args.elements
        num_species = len(elements)
        species = "" 
        for i,element in enumerate(elements):
            species += f" {i+1} {periodictable.elements.symbol(element).number} {element}\n"
    else:
        num_species = "num_species"
        species = "\n"
    return f"""############################################################Input Parameters############################################################        

NumberOfAtoms {args.num_atoms if args.num_atoms is not None else "num_atoms"}
NumberOfSpecies {num_species}

%block ChemicalSpeciesLabel     
# Atomic_Index Atomic_Number Atomic_Symbol
# Example: 1 6 C 
{species}%endblock ChemicalSpeciesLabel

#Use only for needed species, like Li, Na, K...
#%block PAO.Polarization.Scheme
# Atomic_Symbol Polarization_Scheme
# Example: Li non-perturbative

#%endblock PAO.Polarization.Scheme"""

def Structural_Info(args):
    return f"""############################################################Structural Informations############################################################

#Format of the atomic coordinates input: Ang (Angstroms), Fractional (Fractional coordinates)
AtomicCoordinatesFormat {"Fractional" if args.Fin == "F" else "Ang"}

#Format of the atomic coordinates output: Ang (Angstroms), Fractional (Fractional coordinates)
AtomCoorFormatOut {"Fractional" if args.Fout == "F" else "Ang"}

#Type of movement for the unitary cell: True (Cell can move), False (Cell is fixed)
MD.VariableCell {"False" if args.type == "bands" or args.type == "dynamic" or args.cell_fixed == False else "True"}

#Constrain atoms or/and cell-vectors:
%block Geometry.Constraints
# Examples:
# 1- Constrain all Carbon atoms: Z 6
# 2- Constrain the cell-vector c: cell-vector c
# 3- Constrain the movement of one atom in the xy-plane (Z-fixed): atom 1 0. 0. 1.

%endblock Geometry.Constraints

#Cell vectors of the system
LatticeConstant 1.00 Ang
%block LatticeVectors
0.00 0.00 0.00
0.00 0.00 0.00
0.00 0.00 0.00
%endblock LatticeVectors

#Atomic coordinates, depends on the input format choice (Ang or Fractional)
%block AtomicCoordinatesAndAtomicSpecies
#Position_x Position_y Position_z Atomic_Index Atomic_Number Atomic_Symbol
# Example: 0.000000 0.000000 0.000000 1 10 C
0.00 0.00 0.00 1
%endblock AtomicCoordinatesAndAtomicSpecies"""

def Bands_and_DOS_Info(args):
    return f"""############################################################Bands and DOS Informations############################################################

#Specifies the scale of the k vectors in the band lines
BandLinesScale ReciprocalLatticeVectors

#High Simmetry Points/Path (HSP) for the bands calculations:
#More informations about HSP can be found in the wikipedia
%block BandLines
#k_point HSP_x HSP_y HSP_Z HSP_Symbol
# Example: 1 0.000 0.000 0.000 G #(Gamma)

%endblock BandLines

#These block are related with the Density of States (DOS) and Projected Density of States (PDOS)
%block ProjectedDensityOfStates
#Min_Energy Max_Energy Broadening Num_Points Unit
#We can start the line using EF (Fermi Energy) 
# Example: EF -10.00 10.00 0.0500 10000 eV  

%endblock ProjectedDensityOfStates

#These block are related with the Local Density of States (LDOS)
%block LocalDensityOfStates
#Min_Energy Max_Energy Unit
# Example: EF -2.0 2.0 eV

%endblock LocalDensityOfStates"""

def Theoretical_Info(args):
    return f"""############################################################Theoretical Informations############################################################

#Exchange-Correlation functional
XC.Functional GGA 
#Author of the Exchange-Correlation functional
XC.Authors PBE

#Type of basis set
PAO.BasisSize {args.basis_size}

#MeshCutoff intensity for the real space grid
MeshCutoff {args.mesh_cutoff} Ry

#Type of dipole correction: True (Dipole correction on), False (Dipole correction off)
#Use this in case of adsorption
Slab.DipoleCorrection {"True" if args.dipole_correction is not None else "False"}  

#Type of spin polarization: non-polarized, polarized, non-collinear, spin-orbit. (Read Manual for more details)
Spin {"polarized" if args.spin_polarized == True else "non-polarized"}

#Monkhorst-Pack k-point sampling
%block kgrid_Monkhorst_Pack     
#Last value related to the k point value :0.5 (odd) or 0.0 (even)
# For 3D cells, also change the last line
{args.k_point} 0 0 {0.5 if args.k_point % 2 == 0 else 0.0}   
0 {args.k_point} 0 {0.5 if args.k_point % 2 == 0 else 0.0}   
0 0 1 0.0   
%endblock kgrid_Monkhorst_Pack"""

def SCF_Info(args):
    return f"""############################################################SCF Informations############################################################

#All Self Consistent Field (SCF) parameters can be found in the manual, but this configuration is a good estimate for most systems.

#
SolutionMethod diagon
SCF.Mixer.Method pulay
ElectronicTemperature 300 K

#Max value for the SCF cicle
MaxSCFIterations 1000

#Mixer informations. Switch this values for non-converged systems
SCF.Mixer.Weight 0.25
SCF.Mixer.History 10
SCF.Mixer.Restart 30
SCF.Mixer.Kick 100
SCF.Mixer.Kick.Weight 0.5
SCF.Mixer.Restart.Save 4

#Tolerance criteria of SCF cicle
SCF.DM.Tolerance {args.scf_crit}"""

def MD_Info(args):
    if args.type == "dynamic":
        args.run_type = "Nose"
        MD_Info_aux = f"""############################################################MD Informations############################################################

#MD - Molecular Dynamics

#Choice of the type of calculation, see the manual for more information
MD.TypeOfRun {args.run_type}

#
MD.Steps {10000 if args.steps is not None else args.steps}
MD.InitialTimeStep 1
MD.LengthTimeStep 1.0 fs
MD.InitialTemperature {args.temperature_initial} K
MD.TargetTemperature {args.temperature_target} K
MD.NoseMass 100 Ry*fs**2"""
    else:
        MD_Info_aux = f"""############################################################MD Informations############################################################

#MD - Molecular Dynamics

#Choice of the type of calculation, see the manual for more information
MD.TypeOfRun {args.run_type}

#Max atomic optimization step
MD.Steps {args.steps if not args.type == "bands" else 0}

#Max atomic displacements in an optimization step
MD.MaxDispl 0.1 Ang

#Force tolerance criteria in coordinate optimization
MD.MaxForceTol {args.md_crit} eV/Ang"""

    return MD_Info_aux

def Grimme_Info(args):
    return f"""############################################################Grimmes-D3 Informations############################################################

DFTD3 {"True" if args.Grimme_D3 is not None else "False"}
DFTD3.UseXCDefaults {"True" if args.Grimme_D3 is not None else "False"}
DFTD3.BJdamping {"True" if args.Grimme_D3 is not None else "False"}"""

def Re_Run_Info(args):
    return f"""############################################################Re-Run Output Informations############################################################

#Enable use the {args.label}.XV file for re-run calculations
MD.UseSaveXV {"True" if args.save_xv else "False"}

#Enable use the {args.label}.DM file for re-run calculations
DM.UseSaveDM {"False" if not args.no_save_dm else "True"}"""

def Write_Output(args):
    return f"""############################################################Write Output Informations############################################################

#All informations about the output can be obtained in the manual.

#Increase the output informations
LongOutput True

------------------------------------------------Structure and Coordinates------------------------------------------------

#Write the {args.label}.xyz file
WriteCoor.Xmol True

#Write the {args.label}.xtl file (Fractional Format)
WriteCoorCerius True

#Write the MD animation, {args.label}.ANI file
WriteMDXmol True

#Write the initial structure in the output file
WriteCoorInitial True

#Write the structure at each step in the output file
WriteCoorStep True

#Write all Molecular Dynamics (MD) informations:
# {args.label}.MD and {args.label}.MDE files
WriteMDHistory {"True" if args.type == "opt" or args.type == "dynamic" else "False"}

------------------------------------------------Forces and Orbitals------------------------------------------------

#Write the atomic forces, {args.label}.FA file
WriteForces True

#Write all the orbitals used in the calculation. {args.label}.ORB.INDX file
Write.OrbitalIndex False

#Write some orbital informations in the output file
WriteOrbMom False

------------------------------------------------Hamiltonian and Density Matrix (DM)------------------------------------------------

#Write the DM, {args.label}.DM file
Write.DM True

#Write the Hamiltonian and Overlap Matrices (HS), {args.label}.HSX file - Must be true for Bands and DOS calculations?
SaveHS {"True" if args.type == "bands" else "False"}

------------------------------------------------Eigenvalues, Bands and Wavefunctions------------------------------------------------

#Write the Hamiltonian bands eigenvalues, {args.label}.bands file - Must be true for Bands calculations
WriteBands {"True" if args.type == "bands" else "False"}

#Write the Hamiltonian eigenvalues, {args.label}.EIG file - Must be true for DOS accounts calculations
WriteEigenvalues {"True" if args.type == "bands" else "False"}

#Write the Wavefunctions, {args.label}.WFSX file
WriteWaveFunctions {"True" if args.type == "bands" else "False"}

#Write the Kpoints related to the calculation in the output file.
WriteKpoints false

#Write the Kpoints related to the bands calculation in the output file.
WriteKBands false

------------------------------------------------Electronic Populations------------------------------------------------

#Write Mulliken population, values can be 0, 1, 2 or 3 (see manual)
WriteMullikenPop 1

#Write Hirshfeld population
Write.HirshfeldPop True

#Write Voronoi population
Write.VoronoiPop True

#Write the Crystal Orbital Overlap Population (COOP)/ Crystal Orbital Hamiltonian Population (COHP) informations:
#{args.label}.fullBZ.WFSX and {args.label}.HSX files
COOP.Write False

------------------------------------------------Others Write Options------------------------------------------------

#Write.Graphviz
#Write.DM.end.of.cycle
#Write.H 
#Write.H.end.of.cycle
#Write.HS.History

#WFS.Write.For.Bands

#SaveRho
#SaveDeltaRho
#SaveRhoXC
#SaveElectrostaticPotential
#SaveNeutralAtomPotential
#SaveTotalPotential
#SaveIonicCharge
#SaveTotalCharge

#SaveBaderCharge
#AnalyzeChargeDensityOnly
#SaveInitialChargeDensity

#Write.Denchar"""