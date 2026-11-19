from usuario import Usuario


class Administrador(Usuario):
    def __init__(self, id_usuario, nombre):
        super().__init__(id_usuario, nombre, rol="Admin / Clínica")
        self.__tareas_clinicas = ["Medicamento", "Vacunación", "Cambio de Dieta"]

    def obtener_tareas_disponibles(self):
        return list(self.__tareas_clinicas)

    def realizar_tarea(self, mascota, evento, observaciones="", prioridad="Importante"):
        if evento not in self.__tareas_clinicas:
            raise ValueError("Operación médica no válida para el Administrador.")
        # El administrador tiene acceso a registrar_clinica
        return mascota.registrar_clinica(self.obtener_nombre(), evento, observaciones, prioridad)