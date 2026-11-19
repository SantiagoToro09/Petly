from mascota import Mascota
from cuidador import Cuidador
from administrador import Administrador


def main():
    # 1. Creación de objetos (Mascotas y Usuarios)
    perrito = Mascota("Max")
    papa_admin = Administrador(1, "Carlos (Papá)")

    # Uso de Diccionarios
    cuidadores = {
        "1": Cuidador(101, "Andrés (Hijo)"),
        "2": Cuidador(102, "Laura (Hija)")
    }

    print("=== SISTEMA PETLY INICIADO ===")

    # 2. Ejecución general del sistema (Ciclo)
    while True:
        try:
            # La mascota orquesta su propio panel visual
            continuar = perrito.ejecutar_menu(papa_admin, cuidadores)
            if not continuar:
                break

        # 3. Manejo de excepciones centralizado
        except ValueError as error_clinico:
            print(f"\n[SISTEMA BLOQUEADO]: {error_clinico}")
        except Exception as e:
            print(f"\n[ERROR DEL SISTEMA]: Ocurrió un fallo ({e}).")


if __name__ == "__main__":
