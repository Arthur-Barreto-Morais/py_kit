import argparse as arg

def Build_Parser():
    parser = arg.ArgumentParser(prog = "FDF_Creator", formatter_class = arg.RawDescriptionHelpFormatter, description = "Program used to create FDF files for SIESTA code at several configurations", epilog= """Some Examples: 
    1: Run optimization with GrimmeD3 and Dipole Correction activated:
        -l Label -k K_Point -t opt -d3 -dc
        
    2: Run bands with spin polarized optmization:
        -l Label -k K_Point -t bands -s 
        """)

    #######################################################################################################################################################################


    required = parser.add_argument_group("Required Configurations")

    required.add_argument("-l", dest = "label", type = str, required = True, help = "Label of file")
    required.add_argument("-k", dest = "k_point", type = int, required = True, help = "Quantity of K points in Monkhorst-Pack grid")

    input = parser.add_argument_group("Important Configurations")

    input.add_argument("-t", dest = "type", type = str, required = False, metavar = "TYPE", choices = ["opt","bands","phonons","dm"], help = "Some Pattern Configurations [opt, bands, dm (dynamic)]")
    input.add_argument("-n", dest = "num_atoms", type = int, required = False, help = "Number of Atoms")
    input.add_argument("-run", dest = "run_type", type = str, required = False, metavar = "RUN_TYPE", default = "CG", choices = ["CG", "Broyden", "FIRE", "Nose", "FC"], help = "Types of Run - Default (CG) - [CG, Broyden, FIRE, Nose, FC]")
    input.add_argument("-el", dest = "elements", nargs ="+", required = False, metavar = "ELEMENT", help = "Elements (In order)")

    theoretical = parser.add_argument_group("Theoretical Configurations")

    theoretical.add_argument("-bs", dest = "basis_size", type = str, required = False, default = "DZP", help = "Basis Size - Default (DZP)")
    theoretical.add_argument("-mesh", dest = "mesh_cutoff", type = float, required = False, default = 400.0, help = "Mesh Cutoff Value (Ry) - Default (400.0)")

    stored = parser.add_argument_group("Stored Configurations - Add this informations switch the Default (True -> False or False -> True)")

    stored.add_argument("-cm", dest = "cell_fixed", required = False, action = "store_false", help = "Enable Cell Fixed - Default (True) (MD.VariableCell True)")
    stored.add_argument("-s", dest = "spin_polarized", required = False, action = "store_true", help = "Enable spin polarized - Default (non-polarized)")
    stored.add_argument("-d3", dest = "Grimme_D3", required = False, action = "store_true", help = "Enable Grimme D3(BJ) dispersion corrections - Default (False)")
    stored.add_argument("-sv", dest = "no_save_dm", required = False, action = "store_false", help = "Do not use saved density matrix - Default (True) (DM.UseSaveDM True)")
    stored.add_argument("-xv", dest = "save_xv", required = False, action = "store_true", help = "Enable use saved XV file - Default (False) (MD.UseSaveXV False)")
    stored.add_argument("-dc", dest = "dipole_correction", required = False, action = "store_true", help = "Enable slab dipole correction - Default (False) (Slab.DipoleCorrection False)")

    criteria = parser.add_argument_group("Criteria Configurations")

    criteria.add_argument("-scf", dest = "scf_crit", type = float, required = False, default = 0.000001, help = "Criteria of SCF - Default (0.000001)")
    criteria.add_argument("-md", dest = "md_crit", type = float, required = False, default = 0.01, help = "Criteria of MD - Default (0.01)")

    simple = parser.add_argument_group("Simple Configurations")

    simple.add_argument("-Fin", dest = "Fin", type = str, required = False, metavar = "FORMAT IN", default = "A", choices = ["A", "F"], help = "Input Coordinate Format - A = Ang, F = Fractional - Default (Ang)")
    simple.add_argument("-Fout", dest = "Fout", type = str, required = False, metavar = "FORMAT OUT", default = "A", choices = ["A", "F"], help = "Output Coordinate Format - A = Ang, F = Fractional - Default (Ang)")
    simple.add_argument("-steps", dest = "steps", type = int, required = False, default = 500, help = "Number of Steps in MD - Default (500)")

    dynamic = parser.add_argument_group("Dynamic Configurations")

    dynamic.add_argument("-Tin", dest = "temperature_initial", type = int, required = False, default = 300, help = "Initial Temperature of Dynamic Simulation - Default (300)")
    dynamic.add_argument("-Tgt", dest = "temperature_target", type = int, required = False, default = 300, help = "Target Temperature of Dynamic Simulation - Default (300)")

    return parser


def Options(argv = None):
    return Build_Parser().parse_args(argv)