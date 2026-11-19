class Usuario:
    def __init__(self, id_usuario, nombre):
        self.__id_usuario = id_usuario
        self.__nombre = nombre

    def obtener_nombre(self):
        return self.__nombre

    def obtener_id(self):
        return self.__id_usuario

    # Métodos base para el polimorfismo
    def realizar_tarea(self, mascota, evento):
        pass

    def operar_interactivo(self, mascota):
        pass