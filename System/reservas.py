# IMPORTS
from System.integracao import integracao
from datetime import date, datetime
import questionary

# ============================================================
#                       1. BUSCAR HOTEL
# ============================================================

def buscar_hotel(termo_busca: str):
    # Busco o termo tanto no nome quanto no endereço, com "OU"
    # (o usuário não precisa saber os dois de antemão)
    resposta = (
        integracao.table("hotel")
        .select("*")
        .or_(f"nome.ilike.%{termo_busca}%,endereco.ilike.%{termo_busca}%")
        .execute()
    )

    if resposta.data:
        return resposta.data

    # Nada encontrado do jeito exato — tenta busca aproximada,
    # que tolera erro de digitação (ex: "Roanldo" ainda acha "Ronaldo")
    resposta_aproximada = integracao.rpc(
        "buscar_hotel_aproximado", {"termo": termo_busca}
    ).execute()
    return resposta_aproximada.data


# ============================================================
# 2. TIPOS DE QUARTO DE UM HOTEL (+ amenidades de cada um)
# ============================================================

def buscar_tipos_quarto(id_hotel: int):
    resposta = (
        integracao.table("tipo_quarto")
        .select("*")
        .eq("id_hotel", id_hotel)
        .execute()
    )
    return resposta.data


def buscar_amenidades_do_tipo(id_tipo_quarto: int):
    # A ligação só guarda os IDs, então busco os nomes depois
    resposta = (
        integracao.table("tipo_quarto_amenidade")
        .select("id_amenidade")
        .eq("id_tipo_quarto", id_tipo_quarto)
        .execute()
    )
    ids_amenidades = [linha["id_amenidade"] for linha in resposta.data]

    if not ids_amenidades:
        return []

    resposta_amenidades = (
        integracao.table("amenidade_do_quarto")
        .select("nome_amenidade")
        .in_("id_amenidade", ids_amenidades)
        .execute()
    )
    return [linha["nome_amenidade"] for linha in resposta_amenidades.data]


# ============================================================
#               3. QUARTOS DISPONÍVEIS DE UM TIPO
# ============================================================

def buscar_id_status(palavra_chave: str):
    # Busco o status por trecho do nome (ex: "dispon" acha "Disponível")
    resposta = (
        integracao.table("status_quarto")
        .select("id_status")
        .ilike("nome_status", f"%{palavra_chave}%")
        .execute()
    )
    if not resposta.data:
        return None
    return resposta.data[0]["id_status"]


def buscar_quartos_do_tipo(id_tipo_quarto: int):
    # Traz todos os quartos do tipo, exceto os fisicamente indisponíveis
    # (manutenção, limpeza, inspeção) — esses continuam bloqueados
    # independente de data.
    ids_bloqueados = [
        buscar_id_status("manuten"),
        buscar_id_status("limpeza"),
        buscar_id_status("inspec"),
    ]
    ids_bloqueados = [i for i in ids_bloqueados if i is not None]

    query = integracao.table("quarto").select("*").eq("id_tipo_quarto", id_tipo_quarto)

    if ids_bloqueados:
        query = query.not_.in_("id_status", ids_bloqueados)

    resposta = query.execute()
    return resposta.data


def buscar_quartos_disponiveis_periodo(id_tipo_quarto: int, checkin: str, checkout: str):
    # Só entram na lista os quartos sem nenhuma reserva ativa
    # que se cruze com o período pedido.
    quartos = buscar_quartos_do_tipo(id_tipo_quarto)
    return [q for q in quartos if verificar_disponibilidade(q["id_quarto"], checkin, checkout)]


def atualizar_status_quarto(id_quarto: int, id_status: int):
    (
        integracao.table("quarto")
        .update({"id_status": id_status})
        .eq("id_quarto", id_quarto)
        .execute()
    )


# ============================================================
#                    4. RESERVA E PAGAMENTO
# ============================================================

def verificar_disponibilidade(id_quarto: int, checkin: str, checkout: str) -> bool:
    # Existe alguma reserva ativa desse quarto cujo período cruza com o novo?
    # Regra clássica de sobreposição: existente.checkin < novo.checkout
    #                             e   existente.checkout > novo.checkin
    resposta = (
        integracao.table("reserva")
        .select("numero")
        .eq("quarto", id_quarto)
        .eq("status", True)
        .lt("checkin", checkout)
        .gt("checkout", checkin)
        .execute()
    )
    return len(resposta.data) == 0


def criar_reserva(id_hospede: int, id_quarto: int, checkin: str, checkout: str, valor_total: float):
    resposta = (
        integracao.table("reserva")
        .insert({
            "hospede": id_hospede,
            "quarto": id_quarto,
            "checkin": checkin,
            "checkout": checkout,
            "valor_total": valor_total,
            "status": True,  # True = reserva ativa/confirmada
        })
        .execute()
    )
    return resposta.data[0]


def criar_pagamento(numero_reserva: int, valor_total: float, formato: str, parcelas: int = 1):
    resposta = (
        integracao.table("pagamento")
        .insert({
            "reserva": numero_reserva,
            "valor_total": valor_total,
            "formato": formato,
            "parcelas": parcelas,
            "status": "pendente",
        })
        .execute()
    )
    return resposta.data[0]


def buscar_reservas_do_hospede(id_hospede: int):
    # Uso a sintaxe de "embed" do Supabase: como as foreign keys existem,
    # ele já traz o quarto, o tipo de quarto e o hotel juntos, numa só chamada
    resposta = (
        integracao.table("reserva")
        .select("numero, checkin, checkout, valor_total, status, quarto(numero, tipo_quarto(nome_tipo, hotel(nome)))")
        .eq("hospede", id_hospede)
        .order("checkin", desc=True)
        .execute()
    )
    return resposta.data


def cancelar_reserva(numero_reserva: int):
    # Marca como inativa — automaticamente libera o quarto pro período,
    # já que verificar_disponibilidade() só olha reservas com status = True
    (
        integracao.table("reserva")
        .update({"status": False})
        .eq("numero", numero_reserva)
        .execute()
    )


def buscar_pagamentos_do_hospede(id_hospede: int):
    reservas = (
        integracao.table("reserva")
        .select("numero")
        .eq("hospede", id_hospede)
        .execute()
    )
    numeros = [r["numero"] for r in reservas.data]

    if not numeros:
        return []

    resposta = (
        integracao.table("pagamento")
        .select("*")
        .in_("reserva", numeros)
        .execute()
    )
    return resposta.data


# ============================================================
#                      FLUXO PRINCIPAL
# ============================================================

def formatar_valor(valor: float) -> str:
    # Formato brasileiro: ponto separando milhar, vírgula separando centavos.
    # f"{valor:,.2f}" gera o padrão americano (1,234.56) — aqui a gente
    # troca "," por "." e "." por "," pra inverter pro padrão BR.
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def _pedir_data(mensagem: str):
    formatos_aceitos = ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d")

    while True:
        entrada = questionary.text(mensagem).ask()

        if entrada is None or entrada.strip() == "0":
            return None

        entrada = entrada.strip()

        for formato in formatos_aceitos:
            try:
                return datetime.strptime(entrada, formato).date()
            except ValueError:
                continue

        print("Data inválida. Use AAAA-MM-DD ou DD-MM-AAAA (com - ou /), ou 0 para cancelar.")


def _pedir_forma_pagamento(valor_total: float):
    formato = questionary.select(
        "Forma de pagamento:",
        choices=[
            questionary.Choice(title="Pix", value="pix"),
            questionary.Choice(title="Cartão de Débito", value="debito"),
            questionary.Choice(title="Cartão de Crédito", value="credito"),
            questionary.Choice(title="Dinheiro", value="dinheiro"),
            questionary.Choice(title="Cancelar", value=False),
        ],
        instruction="(use as setas do teclado e Enter para confirmar)",
    ).ask()

    if not formato:
        return None, None

    parcelas = 1
    if formato == "credito":
        opcoes_parcelas = [
            questionary.Choice(title=f"{n}x de {formatar_valor(valor_total / n)}", value=n)
            for n in range(1, 13)
        ]
        parcelas = questionary.select(
            "Em quantas parcelas?",
            choices=opcoes_parcelas,
            instruction="(use as setas do teclado e Enter para confirmar)",
        ).ask()

        if parcelas is None:
            return None, None

    return formato, parcelas


def iniciar_reserva(hospede):
    # -- 1. Buscar hotel (nome ou endereço, num campo só)
    termo = questionary.text("Buscar hotel (nome ou endereço):").ask()

    if termo is None:
        print("Reserva cancelada.")
        return

    hoteis = buscar_hotel(termo)

    if not hoteis:
        print("Nenhum hotel encontrado.")
        return

    opcoes = [
        questionary.Choice(title=f"{h['nome']} - {h['endereco']}", value=h)
        for h in hoteis
    ]
    # value=False (não None!) — questionary trata None como "usar o título
    # como valor", então None faria hotel_escolhido virar a string "Cancelar"
    opcoes.append(questionary.Choice(title="Cancelar", value=False))

    hotel_escolhido = questionary.select(
        "Escolha o hotel:",
        choices=opcoes,
        instruction="(use as setas do teclado e Enter para confirmar)",
    ).ask()

    if not hotel_escolhido:
        print("Reserva cancelada.")
        return

    # -- 3. Listar tipos de quarto + amenidades
    tipos = buscar_tipos_quarto(hotel_escolhido["id_hotel"])

    if not tipos:
        print("Este hotel não possui tipos de quarto cadastrados.")
        return

    opcoes_tipo = []
    for tipo in tipos:
        amenidades = buscar_amenidades_do_tipo(tipo["id_tipo_quarto"])
        lista_amenidades = ", ".join(amenidades) if amenidades else "nenhuma"
        titulo = f"{tipo['nome_tipo']} - {formatar_valor(tipo['preco_diaria'])}/diária - Amenidades: {lista_amenidades}"
        opcoes_tipo.append(questionary.Choice(title=titulo, value=tipo))
    opcoes_tipo.append(questionary.Choice(title="Cancelar", value=False))

    tipo_escolhido = questionary.select(
        "Escolha o tipo de quarto:",
        choices=opcoes_tipo,
        instruction="(use as setas do teclado e Enter para confirmar)",
    ).ask()

    if not tipo_escolhido:
        print("Reserva cancelada.")
        return

    # -- 4. Datas primeiro, pra já filtrar quartos livres nesse período
    checkin = _pedir_data("Data de check-in (AAAA-MM-DD ou DD-MM-AAAA, ou 0 p/ cancelar):")
    if checkin is None:
        print("Reserva cancelada.")
        return

    checkout = _pedir_data("Data de check-out (AAAA-MM-DD ou DD-MM-AAAA, ou 0 p/ cancelar):")
    if checkout is None:
        print("Reserva cancelada.")
        return

    if checkout <= checkin:
        print("A data de check-out precisa ser depois do check-in.")
        return

    checkin_str = checkin.isoformat()
    checkout_str = checkout.isoformat()

    # -- 5. Quartos realmente disponíveis nesse período
    quartos = buscar_quartos_disponiveis_periodo(tipo_escolhido["id_tipo_quarto"], checkin_str, checkout_str)

    if not quartos:
        print("Não há quartos disponíveis para este tipo, nesse período.")
        return

    opcoes_quarto = [
        questionary.Choice(title=f"Quarto {quarto['numero']}", value=quarto)
        for quarto in quartos
    ]
    opcoes_quarto.append(questionary.Choice(title="Cancelar", value=False))

    quarto_escolhido = questionary.select(
        "Escolha o quarto:",
        choices=opcoes_quarto,
        instruction="(use as setas do teclado e Enter para confirmar)",
    ).ask()

    if not quarto_escolhido:
        print("Reserva cancelada.")
        return

    diarias = (checkout - checkin).days
    valor_total = diarias * float(tipo_escolhido["preco_diaria"])

    confirmar = questionary.select(
        f"Confirmar reserva? Valor total: {formatar_valor(valor_total)}",
        choices=[
            questionary.Choice(title="Sim", value=True),
            questionary.Choice(title="Não", value=False),
        ],
        instruction="(use as setas do teclado e Enter para confirmar)",
    ).ask()
    if not confirmar:
        print("Reserva cancelada.")
        return

    reserva = criar_reserva(
        hospede["id_hospede"],
        quarto_escolhido["id_quarto"],
        checkin_str,
        checkout_str,
        valor_total,
    )

    # -- 6. Pagamento
    formato, parcelas = _pedir_forma_pagamento(valor_total)
    if formato is None:
        print("Reserva criada, mas o pagamento foi cancelado. Finalize o pagamento depois pelo menu.")
        return

    pagamento = criar_pagamento(reserva["numero"], valor_total, formato, parcelas)

    print("-" * 30)
    print("Reserva realizada com sucesso!")
    print(f"Número da reserva: {reserva['numero']}")
    print(f"Valor total: {formatar_valor(valor_total)}")
    if formato == "credito" and parcelas > 1:
        print(f"Pagamento registrado: {pagamento['id_pagamento']} ({formato}, {parcelas}x de {formatar_valor(valor_total / parcelas)})")
    else:
        print(f"Pagamento registrado: {pagamento['id_pagamento']} ({formato})")


def consultar_reservas(hospede):
    reservas = buscar_reservas_do_hospede(hospede["id_hospede"])
    reservas_ativas = [r for r in reservas if r["status"]]

    if not reservas_ativas:
        print("Você não tem nenhuma reserva ativa no momento.")
        return

    opcoes = []
    for r in reservas_ativas:
        hotel_nome = r["quarto"]["tipo_quarto"]["hotel"]["nome"]
        tipo_nome = r["quarto"]["tipo_quarto"]["nome_tipo"]
        numero_quarto = r["quarto"]["numero"]
        texto = (
            f"#{r['numero']} - {hotel_nome} - Quarto {numero_quarto} ({tipo_nome}) - "
            f"{r['checkin']} a {r['checkout']} - {formatar_valor(r['valor_total'])}"
        )
        opcoes.append(questionary.Choice(title=texto, value=r["numero"]))

    # value=False pelo mesmo motivo do hotel: evitar o fallback do questionary
    opcoes.append(questionary.Choice(title="Voltar", value=False))

    escolha = questionary.select(
        "Suas reservas (selecione uma pra cancelar, ou volte):",
        choices=opcoes,
        instruction="(use as setas do teclado e Enter para confirmar)",
    ).ask()

    if not escolha:
        return

    confirmar = questionary.select(
        "Tem certeza que deseja cancelar essa reserva?",
        choices=[
            questionary.Choice(title="Sim", value=True),
            questionary.Choice(title="Não", value=False),
        ],
        instruction="(use as setas do teclado e Enter para confirmar)",
    ).ask()
    if confirmar:
        cancelar_reserva(escolha)
        print("Reserva cancelada com sucesso.")
    else:
        print("Nenhuma alteração feita.")


def consultar_pagamentos(hospede):
    pagamentos = buscar_pagamentos_do_hospede(hospede["id_hospede"])

    if not pagamentos:
        print("Nenhum pagamento encontrado.")
        return

    print("-" * 40)
    print("Extrato de pagamentos")
    print("-" * 40)
    for p in pagamentos:
        parcelas = p.get("parcelas", 1)
        detalhe_parcelas = f" ({parcelas}x)" if p["formato"] == "credito" and parcelas > 1 else ""
        print(f"Reserva #{p['reserva']} - {formatar_valor(p['valor_total'])} - {p['formato']}{detalhe_parcelas} - status: {p['status']}")
    print("-" * 40)


def menu_reservas(hospede):
    while True:
        opcao = questionary.select(
            f"Olá, {hospede['nome']}! O que deseja fazer?",
            choices=[
                questionary.Choice(title="Nova reserva", value="nova"),
                questionary.Choice(title="Minhas reservas", value="minhas"),
                questionary.Choice(title="Extrato de pagamento", value="extrato"),
                questionary.Choice(title="Sair", value="sair"),
            ],
            instruction="(use as setas do teclado e Enter para confirmar)",
        ).ask()

        if opcao is None or opcao == "sair":
            print("Até a próxima!")
            return

        if opcao == "nova":
            iniciar_reserva(hospede)
        elif opcao == "minhas":
            consultar_reservas(hospede)
        elif opcao == "extrato":
            consultar_pagamentos(hospede)