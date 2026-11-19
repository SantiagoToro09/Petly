class Usuario:
    def __init__(self, id_usuario, nombre, rol="Usuario"):
        self.__id_usuario = id_usuario
        self.__nombre = nombre
        self.__rol = rol

    def obtener_nombre(self):
        return self.__nombre

    def obtener_id(self):
        return self.__id_usuario

    def obtener_rol(self):
        return self.__rol

    def obtener_etiqueta(self):
        return f"{self.__nombre} [{self.__rol}]"

    # Métodos base para el polimorfismo
    def obtener_tareas_disponibles(self):
        return []

    def realizar_tarea(self, mascota, evento, observaciones="", prioridad="Normal"):
        raise NotImplementedError("Este método debe ser implementado por las subclases.")