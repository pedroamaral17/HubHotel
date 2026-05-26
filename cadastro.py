#cpf
#ddn
#email
#telefone

from datetime import datetime
import re
from validadores import isCpfValid

usuarios = []


def cadastrar_usuario():
    while True:
        nome = input("Digite seu nome: ").strip
        if nome == "" or nome == int:
            print("Nome inválido, tente novamente.")
        else:
            break

    while True:
        cpf = input("Digite seu CPF(000.000.000-00): ")
        if isCpfValid(cpf):
            break
        else:
            print("CPF inválido, tente novamente.")

cadastrar_usuario()