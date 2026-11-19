from datetime import datetime


class Registro:
    def __init__(self, autor, evento, es_clinico, observaciones="", prioridad="Normal",
                 mascota_nombre="Max", id_registro=None, fecha=None):
        self.__id_registro = id_registro
        self.__mascota_nombre = mascota_nombre
        self.__autor = autor
        self.__evento = evento
        self.__es_clinico = bool(es_clinico)
        self.__fecha = fecha if fecha else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.__observaciones = observaciones.strip() if observaciones and observaciones.strip() else "Sin observaciones"
        self.__prioridad = prioridad

    def obtener_id(self):
        return self.__id_registro

    def asignar_id(self, nuevo_id):
        self.__id_registro = nuevo_id

    def obtener_mascota(self):
        return self.__mascota_nombre

    def obtener_autor(self):
        return self.__autor

    def obtener_evento(self):
        return self.__evento

    def es_clinico(self):
        return self.__es_clinico

    def obtener_fecha(self):
        return self.__fecha

    def obtener_observaciones(self):
        return self.__observaciones

    def obtener_prioridad(self):
        return self.__prioridad

    def mostrar_detalle(self):
        tipo = "[CLÍNICO]" if self.__es_clinico else "[RUTINA]"
        return f"[{self.__fecha}] {tipo} ({self.__prioridad}) {self.__evento} | Por: {self.__autor} | Obs: {self.__observaciones}"

    def a_fila_excel(self):
        tipo_texto = "Clínico" if self.__es_clinico else "Rutina"
        return [
            self.__id_registro,
            self.__fecha,
            self.__mascota_nombre,
            tipo_texto,
            self.__evento,
            self.__autor,
            self.__prioridad,
            self.__observaciones
        ]