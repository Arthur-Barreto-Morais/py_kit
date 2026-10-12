import shlex
import os
from siesta.file_creator import create
from siesta.file_creator import options as opt
from siesta.tools import chemical

print("Choose the program:")
print("1 - SIESTA")
print("2 - Quantum Expresso (QE)")

programa = input("\nOpção: ").strip()

if programa == "1":
    print("\nChoose the operation:")
    print("1 - Criar arquivo fdf")
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
                print("\nNão deu certo, tente de novo.")

        with open("Arguments.txt", 'w') as f:
            for key, value in vars(args).items():
                f.write(f"{key}={value}\n")
        
        create.Create(args)

        if args.elements is not None:
            chemical.psml_find(fdf_file = args.label + ".fdf", dir = os.getcwd(), path_psml = "~/Siesta_Standart_psml/Scalar_Relativistic/")
        
        if args.type == "bands":
            pass

    elif escolha == "2":
        print("K_point ainda não implementado.")

    elif escolha == "3":
        print("path_finder ainda não implementado.")

    elif escolha == "4":
        print("neb_code ainda não implementado.")

    else:
        print("Opção inválida.")

elif programa == "2":
    print("QE ainda não implementado.")

else:
    print("Opção inválida.")