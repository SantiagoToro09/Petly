from usuario import Usuario


class Cuidador(Usuario):
    def __init__(self, id_usuario, nombre):
        super().__init__(id_usuario, nombre, rol="Cuidador / Rutina")
        self.__tareas_rutina = ["Alimentar", "Pasear", "Cepillar"]

    def obtener_tareas_disponibles(self):
        return list(self.__tareas_rutina)

    def realizar_tarea(self, mascota, evento, observaciones="", prioridad="Normal"):
        if evento not in self.__tareas_rutina:
            raise ValueError("Operación de rutina no válida para el Cuidador.")
        # El cuidador solo puede tocar registrar_rutina
        return mascota.registrar_rutina(self.obtener_nombre(), evento, observaciones, prioridad)