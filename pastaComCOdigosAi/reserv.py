class reserva:
    def __init__(self, Rn, status, hosp, quarto, data, vtotal):
        self.numero = Rn
        self.status = status
        self.hospede = hosp
        self.quarto = quarto
        self.data = data
        self.valor_total = vtotal