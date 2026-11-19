from datetime import datetime


class AlertaSalud:
    def __init__(self):
        self.__metas_diarias = ["Alimentar", "Pasear", "Cepillar"]

    def calcular_progreso_diario(self, mascota):
        hoy = datetime.now().strftime("%Y-%m-%d")
        eventos_hoy = {
            reg.obtener_evento()
            for reg in mascota.obtener_historial()
            if reg.obtener_fecha().startswith(hoy)
        }
        completadas = sum(1 for meta in self.__metas_diarias if meta in eventos_hoy)
        porcentaje = int((completadas / len(self.__metas_diarias)) * 100)
        return porcentaje

    def evaluar_estado(self, mascota):
        historial = mascota.obtener_historial()
        urgentes = [r for r in historial if r.obtener_prioridad() == "Urgente"]

        if urgentes:
            ultimo = urgentes[-1]
            return (
                f"ATENCIÓN URGENTE ({mascota.obtener_nombre()}): {ultimo.obtener_evento()} - {ultimo.obtener_observaciones()}",
                "#D9534F"
            )

        if mascota.medicamento_dado_hoy() and mascota.comida_dada_hoy():
            return (
                f"ÓPTIMO ({mascota.obtener_nombre()}): Alimentación y medicación del día cubiertas.",
                "#2E8B57"
            )

        if mascota.comida_dada_hoy():
            return (
                f"ESTABLE ({mascota.obtener_nombre()}): Ya recibió alimento hoy. Pendiente control/paseo.",
                "#E69500"
            )

        return (
            f"PENDIENTE ({mascota.obtener_nombre()}): Aún no registra alimentación ni cuidados hoy.",
            "#3B7A9E"
        )