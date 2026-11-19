import os
import shutil
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from registro import Registro
from mascota import Mascota


class GestorExcel:
    def __init__(self, ruta_archivo="petly_datos.xlsx"):
        self.__ruta_archivo = ruta_archivo
        self.__encabezados_bitacora = [
            "ID", "Fecha y Hora", "Mascota", "Tipo", "Actividad",
            "Responsable", "Prioridad", "Observaciones"
        ]
        self.__encabezados_mascotas = ["Nombre", "Especie", "Raza", "Peso_kg"]
        self.inicializar_archivo()

    def obtener_ruta(self):
        return self.__ruta_archivo

    def cambiar_ruta(self, nueva_ruta):
        self.__ruta_archivo = nueva_ruta
        self.inicializar_archivo()

    def inicializar_archivo(self):
        if not os.path.exists(self.__ruta_archivo):
            libro = openpyxl.Workbook()

            # Hoja 1: Bitácora
            hoja_bitacora = libro.active
            hoja_bitacora.title = "Bitacora"
            hoja_bitacora.append(self.__encabezados_bitacora)
            self.__estilizar_encabezados(hoja_bitacora, len(self.__encabezados_bitacora))

            # Hoja 2: Mascotas
            hoja_mascotas = libro.create_sheet(title="Mascotas")
            hoja_mascotas.append(self.__encabezados_mascotas)
            self.__estilizar_encabezados(hoja_mascotas, len(self.__encabezados_mascotas))

            libro.save(self.__ruta_archivo)

    def __estilizar_encabezados(self, hoja, num_columnas):
        relleno = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        fuente = Font(color="FFFFFF", bold=True)
        for col in range(1, num_columnas + 1):
            celda = hoja.cell(row=1, column=col)
            celda.fill = relleno
            celda.font = fuente
            celda.alignment = Alignment(horizontal="center")
            hoja.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 20

    # --- CRUD DE MASCOTAS ---
    def leer_mascotas(self):
        self.inicializar_archivo()
        libro = openpyxl.load_workbook(self.__ruta_archivo)
        if "Mascotas" not in libro.sheetnames:
            return []

        hoja = libro["Mascotas"]
        mascotas = []
        for fila in hoja.iter_rows(min_row=2, values_only=True):
            if fila[0]:
                mascotas.append(Mascota(fila[0], fila[1] or "Perro", fila[2] or "Mestizo", fila[3] or 10.0))
        return mascotas

    def guardar_mascota(self, mascota):
        self.inicializar_archivo()
        libro = openpyxl.load_workbook(self.__ruta_archivo)
        hoja = libro["Mascotas"]

        for fila in hoja.iter_rows(min_row=2, values_only=True):
            if fila[0] and str(fila[0]).lower() == mascota.obtener_nombre().lower():
                return False

        hoja.append(mascota.a_fila_excel())
        libro.save(self.__ruta_archivo)
        return True

    # --- CRUD DE REGISTROS (BITÁCORA) ---
    def leer_registros(self):
        self.inicializar_archivo()
        libro = openpyxl.load_workbook(self.__ruta_archivo)
        hoja = libro["Bitacora"]
        registros = []

        for fila in hoja.iter_rows(min_row=2, values_only=True):
            if fila[0] is not None:
                es_clinico = (str(fila[3]).strip().lower() == "clínico")
                reg = Registro(
                    id_registro=int(fila[0]),
                    fecha=str(fila[1]),
                    mascota_nombre=str(fila[2]),
                    es_clinico=es_clinico,
                    evento=str(fila[4]),
                    autor=str(fila[5]),
                    prioridad=str(fila[6]),
                    observaciones=str(fila[7])
                )
                registros.append(reg)
        return registros

    def guardar_registro(self, registro):
        self.inicializar_archivo()
        libro = openpyxl.load_workbook(self.__ruta_archivo)
        hoja = libro["Bitacora"]

        ids_existentes = [
            int(fila[0]) for fila in hoja.iter_rows(min_row=2, values_only=True) if fila[0] is not None
        ]
        nuevo_id = max(ids_existentes, default=0) + 1
        registro.asignar_id(nuevo_id)

        hoja.append(registro.a_fila_excel())
        libro.save(self.__ruta_archivo)
        return nuevo_id

    def actualizar_registro(self, id_registro, nueva_actividad, nuevo_autor, nueva_prioridad, nuevas_obs):
        libro = openpyxl.load_workbook(self.__ruta_archivo)
        hoja = libro["Bitacora"]
        actualizado = False

        for fila_idx in range(2, hoja.max_row + 1):
            valor_id = hoja.cell(row=fila_idx, column=1).value
            if valor_id is not None and int(valor_id) == int(id_registro):
                es_clinico = nueva_actividad in [
                    "Medicamento", "Vacunación", "Cambio de Dieta",
                    "Chequeo General", "Desparasitación", "Control de Peso"
                ]
                hoja.cell(row=fila_idx, column=4).value = "Clínico" if es_clinico else "Rutina"
                hoja.cell(row=fila_idx, column=5).value = nueva_actividad
                hoja.cell(row=fila_idx, column=6).value = nuevo_autor
                hoja.cell(row=fila_idx, column=7).value = nueva_prioridad
                hoja.cell(row=fila_idx, column=8).value = nuevas_obs.strip() or "Sin observaciones"
                actualizado = True
                break

        if actualizado:
            libro.save(self.__ruta_archivo)
        return actualizado

    def eliminar_registro(self, id_registro):
        libro = openpyxl.load_workbook(self.__ruta_archivo)
        hoja = libro["Bitacora"]
        eliminado = False

        for fila_idx in range(2, hoja.max_row + 1):
            valor_id = hoja.cell(row=fila_idx, column=1).value
            if valor_id is not None and int(valor_id) == int(id_registro):
                hoja.delete_rows(fila_idx, 1)
                eliminado = True
                break

        if eliminado:
            libro.save(self.__ruta_archivo)
        return eliminado

    def exportar_copia(self, ruta_destino):
        self.inicializar_archivo()
        shutil.copyfile(self.__ruta_archivo, ruta_destino)