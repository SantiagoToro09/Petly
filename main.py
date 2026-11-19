from mascota import Mascota
from administrador import Administrador
from cuidador import Cuidador
from veterinario import Veterinario
from alerta_salud import AlertaSalud
from recordatorio import Recordatorio
from Gestor_Excel import GestorExcel
from Interfaz_Petly import InterfazPetly

# 1. Inicialización del Backend (Excel con openpyxl)
backend_excel = GestorExcel("petly_datos.xlsx")

# 2. Creación de objetos del dominio (Mascotas y Usuarios)
mascotas_iniciales = [
    Mascota("Max", "Perro", "Labrador", 28.5),
    Mascota("Luna", "Gato", "Siamés", 4.2)
]

usuarios_sistema = [
    Administrador(1, "Carlos (Papá)"),
    Cuidador(101, "Andrés (Hijo)"),
    Cuidador(102, "Laura (Hija)"),
    Veterinario(201, "Dra. Sofía", "TP-84920", "VetCare Pereira")
]

sistema_alertas = AlertaSalud()

recordatorios_iniciales = [
    Recordatorio(1, "Max", "08:00", "Servir desayuno balanceado", "Andrés (Hijo)"),
    Recordatorio(2, "Luna", "18:00", "Aplicar vitamina líquida", "Carlos (Papá)")
]

# 3. Instanciación del Frontend e inicio de la aplicación
app = InterfazPetly(
    backend=backend_excel,
    mascotas_base=mascotas_iniciales,
    usuarios=usuarios_sistema,
    sistema_alertas=sistema_alertas,
    recordatorios=recordatorios_iniciales
)
app.iniciar()