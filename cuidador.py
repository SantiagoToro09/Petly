from usuario import Usuario


class Cuidador(Usuario):
    def __init__(self, id_usuario, nombre):
        super().__init__(id_usuario, nombre)

    def realizar_tarea(self, mascota, evento):
        # El cuidador solo puede tocar registrar_rutina
        return mascota.registrar_rutina(self.obtener_nombre(), evento)

    def operar_interactivo(self, mascota):
        print(f"\n--- Cuidador {self.obtener_nombre()} ---")
        print("Tareas permitidas: 1. Alimentar | 2. Pasear | 3. Cepillar")
        opc = input("¿Qué labor realizaste?: ")

        eventos = {"1": "Alimentar", "2": "Pasear", "3": "Cepillar"}
        if opc in eventos:
            return self.realizar_tarea(mascota, eventos[opc])
        else:
            # Excepción si intenta hacer algo no permitido
            raise ValueError("Operación de rutina no válida.")