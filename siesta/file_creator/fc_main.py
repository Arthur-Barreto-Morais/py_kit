import shlex
import os
import create
import options as opt

def main():
    path_psml = "~/Siesta_Standart_psml/Scalar_Relativistic/"

    programa = input("\nOpção: ").strip()

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

    return

if __name__ == "__main__":
    main()