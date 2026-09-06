# IMPORTS
from System.integracao import integracao
from datetime import date

# ============================================================
#                       1. BUSCAR HOTEL
# ============================================================

def buscar_hotel(nome_busca: str, endereco_busca: str):
    resposta = (
        integracao.table("hotel")
        .select("*")
        .ilike("nome", f"%{nome_busca}%")
        .ilike("endereco", f"%{endereco_busca}%")
        .execute()
    )
    return resposta.data


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


def buscar_quartos_disponiveis(id_tipo_quarto: int):
    id_status_disponivel = buscar_id_status("dispon")

    resposta = (
        integracao.table("quarto")
        .select("*")
        .eq("id_tipo_quarto", id_tipo_quarto)
        .eq("id_status", id_status_disponivel)
        .execute()
    )
    return resposta.data


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


def criar_pagamento(numero_reserva: int, valor_total: float, formato: str):
    resposta = (
        integracao.table("pagamento")
        .insert({
            "reserva": numero_reserva,
            "valor_total": valor_total,
            "formato": formato,
            "status": "pendente",
        })
        .execute()
    )
    return resposta.data[0]


# ============================================================
#                      FLUXO PRINCIPAL
# ============================================================

def _escolher_da_lista(lista, mensagem):
    while True:
        entrada = input(mensagem).strip()

        if not entrada.isdigit():
            print("Digite um número válido.")
            continue

        indice = int(entrada) - 1

        if indice < 0 or indice >= len(lista):
            print("Esse número não existe! Escolha um da lista acima.")
            continue

        return lista[indice]


def iniciar_reserva(hospede):
    # -- 1. Buscar hotel
    nome = input("Nome do hotel: ")
    endereco = input("Endereço: ")

    hoteis = buscar_hotel(nome, endereco)

    if not hoteis:
        print("Nenhum hotel encontrado.")
        return

    for i, hotel in enumerate(hoteis):
        print(f"[{i + 1}] {hotel['nome']} - {hotel['endereco']}")

    hotel_escolhido = _escolher_da_lista(hoteis, "Escolha o hotel (número da lista): ")

    # -- 3. Listar tipos de quarto + amenidades
    tipos = buscar_tipos_quarto(hotel_escolhido["id_hotel"])

    if not tipos:
        print("Este hotel não possui tipos de quarto cadastrados.")
        return

    for i, tipo in enumerate(tipos):
        amenidades = buscar_amenidades_do_tipo(tipo["id_tipo_quarto"])
        print(f"[{i + 1}] {tipo['nome_tipo']} - R$ {tipo['preco_diaria']}/diária")
        print(f"    Amenidades: {', '.join(amenidades) if amenidades else 'nenhuma'}")

    tipo_escolhido = _escolher_da_lista(tipos, "Escolha o tipo de quarto (número da lista): ")

    # -- 4. Quartos disponíveis
    quartos = buscar_quartos_disponiveis(tipo_escolhido["id_tipo_quarto"])

    if not quartos:
        print("Não há quartos disponíveis para este tipo.")
        return

    for i, quarto in enumerate(quartos):
        print(f"[{i + 1}] Quarto {quarto['numero']}")

    quarto_escolhido = _escolher_da_lista(quartos, "Escolha o quarto (número da lista): ")

    # -- 5. Checkin, checkout e valor total
    checkin_str = input("Data de check-in (AAAA-MM-DD): ")
    checkout_str = input("Data de check-out (AAAA-MM-DD): ")

    checkin = date.fromisoformat(checkin_str)
    checkout = date.fromisoformat(checkout_str)

    if checkout <= checkin:
        print("A data de check-out precisa ser depois do check-in.")
        return

    diarias = (checkout - checkin).days
    valor_total = diarias * float(tipo_escolhido["preco_diaria"])

    reserva = criar_reserva(
        hospede["id_hospede"],
        quarto_escolhido["id_quarto"],
        checkin_str,
        checkout_str,
        valor_total,
    )

    # -- 6. Atualiza o status do quarto para "reservado"
    id_status_reservado = buscar_id_status("reserv")
    if id_status_reservado:
        atualizar_status_quarto(quarto_escolhido["id_quarto"], id_status_reservado)

    # -- 7. Pagamento
    formato = input("Forma de pagamento (pix, cartao, dinheiro): ")
    pagamento = criar_pagamento(reserva["numero"], valor_total, formato)

    print("-" * 30)
    print("Reserva realizada com sucesso!")
    print(f"Número da reserva: {reserva['numero']}")
    print(f"Valor total: R$ {valor_total}")
    print(f"Pagamento registrado: {pagamento['id_pagamento']} ({formato})")