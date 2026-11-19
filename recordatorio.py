class Recordatorio:
    def __init__(self, id_recordatorio, mascota_nombre, hora, descripcion, responsable, completado=False):
        self.__id_recordatorio = id_recordatorio
        self.__mascota_nombre = mascota_nombre
        self.__hora = hora
        self.__descripcion = descripcion
        self.__responsable = responsable
        self.__completado = completado

    def obtener_id(self):
        return self.__id_recordatorio

    def obtener_mascota(self):
        return self.__mascota_nombre

    def obtener_hora(self):
        return self.__hora

    def obtener_descripcion(self):
        return self.__descripcion

    def obtener_responsable(self):
        return self.__responsable

    def esta_completado(self):
        return self.__completado

    def marcar_completado(self):
        self.__completado = True

    def obtener_resumen(self):
        estado = "✔ Completado" if self.__completado else "⏳ Pendiente"
        return f"[{self.__hora}] {self.__mascota_nombre}: {self.__descripcion} ({self.__responsable}) - {estado}"