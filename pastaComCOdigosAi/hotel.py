class hotel:
    def __init__(self, nome, endereco, ava, telefone, email, validacao):
        self.nome = nome
        self.endereco = endereco
        self.avaliacao = ava
        self.telefone = telefone
        self.email = email
        self.validacao = validacao

    def exibir(self):
        print(f"Nome: {self.nome}")
        print(f"CPF: {self.CPF}")
        print(f"Telefone: {self.telefone}")
        print(f"Email: {self.email}")
        print(f"Senha: {self.senha}")
     