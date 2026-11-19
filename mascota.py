from datetime import datetime
from registro import Registro


class Mascota:
    def __init__(self, nombre, especie="Perro", raza="Mestizo", peso_kg=10.0):
        self.__nombre = nombre
        self.__especie = especie
        self.__raza = raza
        self.__peso_kg = float(peso_kg)
        self.__historial = []

        # Atributos internos para validación de tiempo/duplicados
        self.__medicamento_dado_hoy = False
        self.__comida_dada_hoy = False

    def obtener_nombre(self):
        return self.__nombre

    def obtener_especie(self):
        return self.__especie

    def obtener_raza(self):
        return self.__raza

    def obtener_peso(self):
        return self.__peso_kg

    def actualizar_peso(self, nuevo_peso):
        valor = float(nuevo_peso)
        if valor <= 0:
            raise ValueError("El peso de la mascota debe ser mayor a 0 kg.")
        self.__peso_kg = valor

    def obtener_historial(self):
        return list(self.__historial)

    def comida_dada_hoy(self):
        return self.__comida_dada_hoy

    def medicamento_dado_hoy(self):
        return self.__medicamento_dado_hoy

    def reiniciar_estado_diario(self):
        self.__comida_dada_hoy = False
        self.__medicamento_dado_hoy = False

    def cargar_registro_existente(self, registro):
        self.__historial.append(registro)
        hoy = datetime.now().strftime("%Y-%m-%d")
        if registro.obtener_fecha().startswith(hoy):
            if registro.obtener_evento() == "Alimentar":
                self.__comida_dada_hoy = True
            elif registro.obtener_evento() == "Medicamento":
                self.__medicamento_dado_hoy = True

    def registrar_rutina(self, autor, evento, observaciones="", prioridad="Normal"):
        if evento == "Alimentar" and self.__comida_dada_hoy:
            raise ValueError(
                f"¡Peligro! {self.__nombre} ya fue alimentado hoy. Riesgo de desorden digestivo."
            )

        if evento == "Alimentar":
            self.__comida_dada_hoy = True

        nuevo_registro = Registro(
            autor=autor,
            evento=evento,
            es_clinico=False,
            observaciones=observaciones,
            prioridad=prioridad,
            mascota_nombre=self.__nombre
        )
        self.__historial.append(nuevo_registro)
        return nuevo_registro

    def registrar_clinica(self, autor, evento, observaciones="", prioridad="Importante"):
        if evento == "Medicamento" and self.__medicamento_dado_hoy:
            raise ValueError(
                f"¡ALERTA CRÍTICA! {self.__nombre} ya recibió su medicamento hoy. Riesgo de sobredosis."
            )

        if evento == "Medicamento":
            self.__medicamento_dado_hoy = True

        nuevo_registro = Registro(
            autor=autor,
            evento=evento,
            es_clinico=True,
            observaciones=observaciones,
            prioridad=prioridad,
            mascota_nombre=self.__nombre
        )
        self.__historial.append(nuevo_registro)
        return nuevo_registro

    def a_fila_excel(self):
        return [self.__nombre, self.__especie, self.__raza, self.__peso_kg]