class hospedes:
    def __init__(self, nome, CPF, telefone, email, senha, DDN):
        self.nome = nome
        self.CPF = CPF
        self.telefone = telefone
        self.email = email
        self.senha = senha
        self.DDN = DDN

    def exibir(self):
        print(f"Nome: {self.nome}")
        print(f"Data de Nascimento: {self.DDN}")
        print(f"CPF: {self.CPF}")
        print(f"Telefone: {self.telefone}")
        print(f"Email: {self.email}")
        print(f"Senha: {self.senha}")

nome = input("Digite seu nome: ")
DDN = input("Digite sua data de nascimento: ")
CPF = input("Digite seu CPF: ")
telefone = input("Digite seu telefone: ")
email = input("Digite seu e-mail: ")
legal = input("Digite sua senha: ")
senha = input("Confirme sua senha: ")

while legal != senha:
    print("As senhas não são a mesma!")

legal = input("Digite sua senha novamente: ")
senha = input("Confirme sua senha: ")
       

    






