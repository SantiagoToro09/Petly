from registro import Registro


class Mascota:
    def __init__(self, nombre):
        self.__nombre = nombre
        self.__historial = []  # Lista exigida por la rúbrica

        # Atributos internos para validación de tiempo/duplicados
        self.__medicamento_dado_hoy = False
        self.__comida_dada_hoy = False

    def obtener_nombre(self):
        return self.__nombre

    def registrar_rutina(self, autor, evento):
        if evento == "Alimentar" and self.__comida_dada_hoy:
            # EXCEPCIÓN: Previene sobrealimentación
            raise ValueError(
                f"¡Peligro! {self.__nombre} ya fue alimentado recientemente. Riesgo de desorden digestivo.")

        if evento == "Alimentar":
            self.__comida_dada_hoy = True

        nuevo_registro = Registro(autor, evento, es_clinico=False)
        nuevo_registro.solicitar_observacion()
        self.__historial.append(nuevo_registro)
        return f"Rutina '{evento}' registrada con éxito."

    def registrar_clinica(self, autor, evento):
        if evento == "Medicamento" and self.__medicamento_dado_hoy:
            # EXCEPCIÓN CRÍTICA: Previene sobremedicación
            raise ValueError(f"¡ALERTA CRÍTICA! {self.__nombre} ya recibió su medicamento. Riesgo de sobredosis.")

        if evento == "Medicamento":
            self.__medicamento_dado_hoy = True

        nuevo_registro = Registro(autor, evento, es_clinico=True)
        nuevo_registro.solicitar_observacion()
        self.__historial.append(nuevo_registro)
        return f"Actividad médica '{evento}' registrada bajo estricta supervisión."

    def ejecutar_menu(self, admin, cuidadores):
        print(f"\n--- PANEL DE MASCOTA: {self.__nombre.upper()} ---")
        print("1. Registrar actividad diaria (Hijos/Cuidadores)")
        print("2. Registrar actividad clínica (Padres/Admin)")
        print("3. Ver bitácora de salud y cuidados")
        print("4. Salir del sistema")
        opcion = input("Elige una opción (1-4): ")

        if opcion == "1":
            id_cuidador = input("\nSeleccione cuidador (1. Hijo Menor | 2. Hija Mayor): ")
            if id_cuidador in cuidadores:
                # Llamada polimórfica interactiva
                print(cuidadores[id_cuidador].operar_interactivo(self))
            else:
                print("Cuidador no encontrado.")
        elif opcion == "2":
            # Llamada polimórfica interactiva exclusiva para el Admin
            print(admin.operar_interactivo(self))
        elif opcion == "3":
            self.mostrar_bitacora()
        elif opcion == "4":
            print("Cerrando Petly... ¡Cuida bien a tus mascotas!")
            return False
        else:
            print("Opción inválida.")
        return True

    def mostrar_bitacora(self):
        print(f"\n--- HISTORIAL DE {self.__nombre.upper()} ---")
        if not self.__historial:
            print("No hay registros el día de hoy.")
        else:
            for reg in self.__historial:
                print(reg.mostrar_detalle())