import shlex
import os
from siesta import create, options as opt, k_point, neb, path_finder as pf, input_info as ii

path_psml = "~/Siesta_Standart_psml/Scalar_Relativistic/"

print("Choose the program:")
print("1 - SIESTA")
print("2 - Quantum Expresso (QE)")

programa = input("\nOpção: ").strip()

if programa == "1":
    print("\nChoose the operation:")
    print("1 - Create fdf file")
    print("2 - K_point")
    print("3 - path_finder")
    print("4 - neb_code")

    escolha = input("\nOption: ").strip()

    if escolha == "1":
        parser = opt.Build_Parser()
        parser.print_help()

        while True:
            linha = input("\nChoose the arguments: ")
            try:
                args = parser.parse_args(shlex.split(linha))
                break
            except SystemExit:
                print("\nERROR.")

        with open("Arguments.txt", 'w') as f:
            for key, value in vars(args).items():
                f.write(f"{key}={value}\n")
        
        create.Create(args,os.getcwd(),path_psml)

        if os.path.exists("vec.dat") and os.path.exists("pos.dat"):
            ii.(args)
    elif escolha == "2":
        parser = k_point.get_parser()
        parser.print_help()

        while True:
            linha = input("\nChoose the arguments: ")
            try:
                args = parser.parse_args(shlex.split(linha))
                break
            except SystemExit:
                print("\nERROR.")

        with open("Arguments_kp.txt", 'w') as f:
            for key, value in vars(args).items():
                f.write(f"{key}={value}\n")

        k_point.k_point(args, path_psml)
        
    elif escolha == "3":
        parser = pf.get_parser()      
        parser.print_help()

        while True:
            linha = input("\nChoose the arguments: ")
            try:
                args = parser.parse_args(shlex.split(linha))
                break
            except SystemExit:
                print("\nERROR.")
        
        pf.run(args)

    elif escolha == "4":
        parser = neb.get_parser()        
        parser.print_help()

        while True:
            linha = input("\nChoose the arguments: ")
            try:
                args = parser.parse_args(shlex.split(linha))
                break
            except SystemExit:
                print("\nERROR.")

        with open("Arguments_neb.txt", 'w') as f:
            for key, value in vars(args).items():
                f.write(f"{key}={value}\n")   
        
        neb.neb_code(args, path_psml)    

    else:
        print("Opção inválida.")

elif programa == "2":
    print("QE ainda não implementado.")

else:
    print("Opção inválida.")