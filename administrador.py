from usuario import Usuario


class Administrador(Usuario):
    def __init__(self, id_usuario, nombre):
        super().__init__(id_usuario, nombre)

    def realizar_tarea(self, mascota, evento):
        # El administrador tiene acceso a registrar_clinica
        return mascota.registrar_clinica(self.obtener_nombre(), evento)

    def operar_interactivo(self, mascota):
        print(f"\n--- Admin {self.obtener_nombre()} (Control Médico) ---")
        print("Tareas clínicas: 1. Medicamento | 2. Vacunación | 3. Cambio de Dieta")
        opc = input("¿Qué labor clínica realizaste?: ")

        eventos = {"1": "Medicamento", "2": "Vacunación", "3": "Cambio de Dieta"}
        if opc in eventos:
            return self.realizar_tarea(mascota, eventos[opc])
        else:
            raise ValueError("Operación médica no válida.")