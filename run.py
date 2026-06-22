# HUBHOTEL - PROTÓTIPO

usuarios = []
hoteis = []
reservas = []

usuario_logado = None


class Hospede:
    def __init__(self, nome, cpf, email, senha):
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.senha = senha

    def __str__(self):
        return f"{self.nome} | {self.email}"


class Hotel:
    def __init__(self, nome, cidade, preco, estrelas):
        self.nome = nome
        self.cidade = cidade
        self.preco = preco
        self.estrelas = estrelas

    def exibir(self):
        print("=" * 40)
        print(f"Hotel: {self.nome}")
        print(f"Cidade: {self.cidade}")
        print(f"Avaliação: {self.estrelas}")
        print(f"Diária: R$ {self.preco:.2f}")
        print("=" * 40)


class Reserva:
    def __init__(self, hospede, hotel, dias):
        self.hospede = hospede
        self.hotel = hotel
        self.dias = dias
        self.valor_total = hotel.preco * dias
        self.status = "Confirmada"

    def mostrar(self):
        print("\n========= RESERVA =========")
        print(f"Hóspede: {self.hospede.nome}")
        print(f"Hotel: {self.hotel.nome}")
        print(f"Cidade: {self.hotel.cidade}")
        print(f"Dias: {self.dias}")
        print(f"Valor Total: R$ {self.valor_total:.2f}")
        print(f"Status: {self.status}")
        print("===========================\n")

hoteis.append(Hotel("Copacabana Palace", "Rio de Janeiro", 950, "9.5/10"))
hoteis.append(Hotel("Hotel Bahia Premium", "Salvador", 450, "8.8/10"))
hoteis.append(Hotel("Hub Luxury Resort", "São Paulo", 1200, "9.9/10"))
hoteis.append(Hotel("Pousada do Sol", "Fortaleza", 300, "8.0/10"))


def cadastrar():
    print("\n=== CADASTRO ===")

    nome = input("Nome: ")
    cpf = input("CPF: ")
    email = input("Email: ")
    senha = input("Senha: ")

    for usuario in usuarios:
        if usuario.email == email:
            print("\nEmail já cadastrado.")
            return

    novo = Hospede(nome, cpf, email, senha)
    usuarios.append(novo)

    print("\nCadastro realizado com sucesso!")


def login():
    global usuario_logado

    print("\n=== LOGIN ===")

    email = input("Email: ")
    senha = input("Senha: ")

    for usuario in usuarios:
        if usuario.email == email and usuario.senha == senha:
            usuario_logado = usuario
            print(f"\nBem-vindo(a), {usuario.nome}!")
            return

    print("\nEmail ou senha incorretos.")


def listar_hoteis():
    print("\n===== HOTÉIS DISPONÍVEIS =====")

    for i, hotel in enumerate(hoteis, start=1):
        print(f"\n[{i}]")
        hotel.exibir()


def reservar():
    if usuario_logado is None:
        print("\nFaça login primeiro.")
        return

    listar_hoteis()

    try:
        escolha = int(input("\nEscolha um hotel: ")) - 1

        if escolha < 0 or escolha >= len(hoteis):
            print("Hotel inválido.")
            return

        dias = int(input("Quantos dias deseja ficar? "))

        nova = Reserva(usuario_logado, hoteis[escolha], dias)

        reservas.append(nova)

        print("\n=== PAGAMENTO ===")
        print("1 - PIX")
        print("2 - Cartão")
        print("3 - Dinheiro")

        forma = input("Forma de pagamento: ")

        print("\nProcessando pagamento...")
        print("Pagamento aprovado!")

        nova.mostrar()

    except ValueError:
        print("Entrada inválida.")


def minhas_reservas():
    if usuario_logado is None:
        print("\nFaça login primeiro.")
        return

    encontrou = False

    for reserva in reservas:
        if reserva.hospede == usuario_logado:
            reserva.mostrar()
            encontrou = True

    if not encontrou:
        print("\nNenhuma reserva encontrada.")


def menu_usuario():
    while usuario_logado is not None:

        print(f"\n=== HUBHOTEL | {usuario_logado.nome} ===")
        print("1 - Ver hotéis")
        print("2 - Reservar hotel")
        print("3 - Minhas reservas")
        print("4 - Logout")

        op = input("Escolha: ")

        if op == "1":
            listar_hoteis()

        elif op == "2":
            reservar()

        elif op == "3":
            minhas_reservas()

        elif op == "4":
            logout()

        else:
            print("Opção inválida.")


def logout():
    global usuario_logado

    print(f"\nAté logo, {usuario_logado.nome}!")
    usuario_logado = None


while True:

    print("""
=================================
           HUBHOTEL
=================================
1 - Cadastrar
2 - Login
3 - Sair
=================================
""")

    opcao = input("Escolha: ")

    if opcao == "1":
        cadastrar()

    elif opcao == "2":
        login()

        if usuario_logado:
            menu_usuario()

    elif opcao == "3":
        print("\nObrigado por utilizar o HubHotel!")
        break

    else:
        print("Opção inválida.")