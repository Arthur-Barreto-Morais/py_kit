from . import writer as wt

def Create(args):
    fdf_file = args.label + ".fdf"

    with open(fdf_file, 'w') as f:
        f.write(wt.Label_of_System(args)+"\n"+"\n")

        f.write(wt.Input_Parameters(args)+"\n"+"\n")

        f.write(wt.Structural_Info(args)+"\n"+"\n")

        if args.type == "bands":
            f.write(wt.Bands_and_DOS_Info(args)+"\n"+"\n")

        f.write(wt.Theoretical_Info(args)+"\n"+"\n")

        f.write(wt.SCF_Info(args)+"\n"+"\n")
        
        f.write(wt.MD_Info(args)+"\n"+"\n")

        f.write(wt.Grimme_Info(args)+"\n"+"\n")

        f.write(wt.Re_Run_Info(args)+"\n"+"\n")

        f.write(wt.Write_Output(args)+"\n"+"\n")
    return