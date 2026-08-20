usuarios = []

usuario_logado = None


class Hospede:
    def __init__(self, nome, cpf, email, senha):
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.senha = senha


def login():
    global usuario_logado

    print("\n=== LOGIN ===")

    email = input("Email: ")
    senha = input("Senha: ")

    for usuario in usuarios:
        if usuario.email == email and usuario.senha == senha:
            usuario_logado = usuario
            print(f"\nBem-vindo(a), {usuario.nome}!")
            return usuario

    print("\nEmail ou senha incorretos.")
    return None