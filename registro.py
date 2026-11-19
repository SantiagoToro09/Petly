from datetime import datetime

class Registro:
    def __init__(self, autor, evento, es_clinico):
        self.__autor = autor
        self.__evento = evento
        self.__es_clinico = es_clinico # Booleano para saber si es médico o rutina
        self.__fecha = datetime.now().strftime("%H:%M:%S")
        self.__observaciones = ""

    # El registro pide interactivamente sus observaciones
    def solicitar_observacion(self):
        print(f"   -> Detallando la actividad: {self.__evento}")
        self.__observaciones = input("   Escribe alguna observación (ej. Comió todo, dosis de 5ml): ")
        if not self.__observaciones.strip():
            self.__observaciones = "Sin observaciones"

    def mostrar_detalle(self):
        tipo = "[CLÍNICO]" if self.__es_clinico else "[RUTINA]"
        return f"[{self.__fecha}] {tipo} {self.__evento} | Por: {self.__autor} | Observacion: {self.__observaciones}"

    def obtener_evento(self):
        return self.__evento