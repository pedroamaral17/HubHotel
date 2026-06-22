titulo = "Bem-vindo ao HubHotel"

cidades = {
    "1": "Mauá",
    "2": "Guapituba",
    "3": "Ribeirão Pires",
    "4": "Rio Grande da Serra"
}

while True:
    print("\n" + "=" * len(titulo))
    print(titulo)
    print("=" * len(titulo))

    print("\n1 - Cadastro")
    print("2 - Login")
    print("3 - Pesquisar cidade")
    print("4 - Escolher cidade")
    print("0 - Sair")

    opcao = input("\nEscolha uma opção: ")

    if opcao == "1":
        print("Carregando cadastro...")

    elif opcao == "2":
        print("Carregando login...")

    elif opcao == "3":
        pesquisa = input("Digite o nome da cidade: ")

        encontrado = False

        for cidade in cidades.values():
            if pesquisa.lower() in cidade.lower():
                print(f"Cidade encontrada: {cidade}")
                encontrado = True

        if not encontrado:
            print("Nenhuma cidade encontrada.")

    elif opcao == "4":
        print("\nCidades disponíveis:")

        for codigo, cidade in cidades.items():
            print(f"{codigo} - {cidade}")

        escolha = input("\nEscolha uma cidade: ")

        if escolha in cidades:
            print(f"Você escolheu: {cidades[escolha]}")
        else:
            print("Cidade inválida.")

    elif opcao == "0":
        print("Obrigado por usar o HubHotel!")
        break

    else:
        print("Opção inválida. Tente novamente.")
