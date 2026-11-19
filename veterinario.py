from usuario import Usuario


class Veterinario(Usuario):
    def __init__(self, id_usuario, nombre, tarjeta_profesional, clinica="Clínica Veterinaria"):
        super().__init__(id_usuario, nombre, rol="Veterinario")
        self.__tarjeta_profesional = tarjeta_profesional
        self.__clinica = clinica
        self.__tareas_veterinarias = ["Chequeo General", "Desparasitación", "Control de Peso"]

    def obtener_tarjeta_profesional(self):
        return self.__tarjeta_profesional

    def obtener_clinica(self):
        return self.__clinica

    def obtener_tareas_disponibles(self):
        return list(self.__tareas_veterinarias)

    def realizar_tarea(self, mascota, evento, observaciones="", prioridad="Urgente"):
        if evento not in self.__tareas_veterinarias:
            raise ValueError("Procedimiento veterinario no autorizado.")
        firma_especialista = f"{self.obtener_nombre()} (TP: {self.__tarjeta_profesional})"
        return mascota.registrar_clinica(firma_especialista, evento, observaciones, prioridad)