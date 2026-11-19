import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from mascota import Mascota
from recordatorio import Recordatorio


class InterfazPetly:
    def __init__(self, backend, mascotas_base, usuarios, sistema_alertas, recordatorios):
        self.__backend = backend
        self.__usuarios = {u.obtener_etiqueta(): u for u in usuarios}
        self.__sistema_alertas = sistema_alertas
        self.__recordatorios = list(recordatorios)
        self.__mascotas = {}
        self.__id_seleccionado = None

        # Sincronizar mascotas con Excel
        self.__sincronizar_mascotas(mascotas_base)

        # Ventana principal
        self.root = tk.Tk()
        self.root.title("Petly - Sistema Inteligente de Cuidado y Salud de Mascotas")
        self.root.geometry("1120x660")
        self.root.configure(bg="#F4F6F9")

        # Variables de control Tkinter
        self.var_mascota = tk.StringVar()
        self.var_usuario = tk.StringVar()
        self.var_actividad = tk.StringVar()
        self.var_observaciones = tk.StringVar()
        self.var_prioridad = tk.StringVar(value="Normal")
        self.var_solo_clinicos = tk.BooleanVar(value=False)

        self.__construir_menu()
        self.__construir_interfaz()
        self.__cargar_datos_desde_excel()

    def __sincronizar_mascotas(self, mascotas_base):
        guardadas = self.__backend.leer_mascotas()
        if not guardadas:
            for m in mascotas_base:
                self.__backend.guardar_mascota(m)
                self.__mascotas[m.obtener_nombre()] = m
        else:
            for m in guardadas:
                self.__mascotas[m.obtener_nombre()] = m

    def __construir_menu(self):
        barra_menu = tk.Menu(self.root)

        menu_archivo = tk.Menu(barra_menu, tearoff=0)
        menu_archivo.add_command(label="Abrir archivo Excel...", command=self.__abrir_excel)
        menu_archivo.add_command(label="Exportar copia Excel...", command=self.__exportar_excel)
        menu_archivo.add_command(label="Recargar desde Excel", command=self.__cargar_datos_desde_excel)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.root.quit)
        barra_menu.add_cascade(label="Archivo", menu=menu_archivo)

        menu_gestion = tk.Menu(barra_menu, tearoff=0)
        menu_gestion.add_command(label="Mascotas y Recordatorios", command=self.__abrir_ventana_secundaria)
        menu_gestion.add_command(label="Reiniciar alertas diarias", command=self.__reiniciar_alertas_dia)
        barra_menu.add_cascade(label="Gestión", menu=menu_gestion)

        menu_ayuda = tk.Menu(barra_menu, tearoff=0)
        menu_ayuda.add_command(label="Acerca de Petly", command=self.__mostrar_acerca_de)
        barra_menu.add_cascade(label="Ayuda", menu=menu_ayuda)

        self.root.config(menu=barra_menu)

    def __construir_interfaz(self):
        # --- FRAME SUPERIOR (Banner y Estado de Salud) ---
        frame_superior = tk.Frame(self.root, bg="#1F4E78", padx=15, pady=10)
        frame_superior.pack(fill="x")

        tk.Label(
            frame_superior, text="🐾 PETLY | Bitácora Familiar y Control Veterinario",
            font=("Segoe UI", 15, "bold"), bg="#1F4E78", fg="white"
        ).pack(side="left")

        self.lbl_archivo_actual = tk.Label(
            frame_superior, text=f"Excel: {self.__backend.obtener_ruta()}",
            font=("Segoe UI", 9), bg="#1F4E78", fg="#D9E2EC"
        )
        self.lbl_archivo_actual.pack(side="right")

        # --- CONTENEDOR PRINCIPAL ---
        frame_contenido = tk.Frame(self.root, bg="#F4F6F9", padx=12, pady=12)
        frame_contenido.pack(fill="both", expand=True)

        # --- PANEL IZQUIERDO: FORMULARIO DE REGISTRO ---
        frame_form = tk.LabelFrame(
            frame_contenido, text=" Registro y Edición de Actividad ",
            font=("Segoe UI", 10, "bold"), bg="white", padx=14, pady=12
        )
        frame_form.pack(side="left", fill="y", padx=(0, 10))

        # Mascota (Combobox)
        tk.Label(frame_form, text="Mascota:", bg="white", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", pady=4)
        self.combo_mascota = ttk.Combobox(
            frame_form, textvariable=self.var_mascota,
            values=list(self.__mascotas.keys()), state="readonly", width=30
        )
        self.combo_mascota.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        if self.__mascotas:
            self.combo_mascota.current(0)
        self.combo_mascota.bind("<<ComboboxSelected>>", lambda e: self.__actualizar_panel_bienestar())

        # Usuario / Responsable (Combobox)
        tk.Label(frame_form, text="Responsable (Rol):", bg="white", font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky="w", pady=4)
        self.combo_usuario = ttk.Combobox(
            frame_form, textvariable=self.var_usuario,
            values=list(self.__usuarios.keys()), state="readonly", width=30
        )
        self.combo_usuario.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        self.combo_usuario.bind("<<ComboboxSelected>>", self.__actualizar_tareas_por_usuario)

        # Actividad (Combobox dinámico según polimorfismo)
        tk.Label(frame_form, text="Actividad / Labor:", bg="white", font=("Segoe UI", 9, "bold")).grid(row=4, column=0, sticky="w", pady=4)
        self.combo_actividad = ttk.Combobox(
            frame_form, textvariable=self.var_actividad, state="readonly", width=30
        )
        self.combo_actividad.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        if self.__usuarios:
            self.combo_usuario.current(0)
            self.__actualizar_tareas_por_usuario()

        # Prioridad (Radiobuttons)
        tk.Label(frame_form, text="Nivel de Atención:", bg="white", font=("Segoe UI", 9, "bold")).grid(row=6, column=0, sticky="w", pady=4)
        frame_radios = tk.Frame(frame_form, bg="white")
        frame_radios.grid(row=7, column=0, columnspan=2, sticky="w", pady=(0, 8))
        for nivel in ["Normal", "Importante", "Urgente"]:
            tk.Radiobutton(
                frame_radios, text=nivel, variable=self.var_prioridad,
                value=nivel, bg="white"
            ).pack(side="left", padx=(0, 8))

        # Observaciones (Entry + .bind Return)
        tk.Label(frame_form, text="Observaciones (Enter para guardar):", bg="white", font=("Segoe UI", 9, "bold")).grid(row=8, column=0, sticky="w", pady=4)
        self.entry_obs = tk.Entry(frame_form, textvariable=self.var_observaciones, width=33, font=("Segoe UI", 10))
        self.entry_obs.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        self.entry_obs.bind("<Return>", lambda event: self.__registrar_actividad())

        # Botones CRUD
        tk.Button(
            frame_form, text="Registrar Nueva Actividad", command=self.__registrar_actividad,
            bg="#2E8B57", fg="white", font=("Segoe UI", 9, "bold"), pady=6
        ).grid(row=10, column=0, columnspan=2, sticky="ew", pady=3)

        tk.Button(
            frame_form, text="Actualizar Seleccionado", command=self.__actualizar_registro,
            bg="#2B6CB0", fg="white", font=("Segoe UI", 9, "bold"), pady=6
        ).grid(row=11, column=0, columnspan=2, sticky="ew", pady=3)

        tk.Button(
            frame_form, text="Eliminar Seleccionado", command=self.__eliminar_registro,
            bg="#C53030", fg="white", font=("Segoe UI", 9, "bold"), pady=6
        ).grid(row=12, column=0, columnspan=2, sticky="ew", pady=3)

        tk.Button(
            frame_form, text="Limpiar Formulario", command=self.__limpiar_formulario,
            bg="#718096", fg="white", font=("Segoe UI", 9), pady=5
        ).grid(row=13, column=0, columnspan=2, sticky="ew", pady=3)

        tk.Button(
            frame_form, text="Abrir Mascotas y Recordatorios", command=self.__abrir_ventana_secundaria,
            bg="#1F4E78", fg="white", font=("Segoe UI", 9, "bold"), pady=6
        ).grid(row=14, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        # --- PANEL DERECHO: ESTADO + TREEVIEW ---
        frame_derecho = tk.Frame(frame_contenido, bg="#F4F6F9")
        frame_derecho.pack(side="right", fill="both", expand=True)

        # Sub-frame Estado y Elemento Adicional (ttk.Progressbar)
        frame_estado = tk.LabelFrame(
            frame_derecho, text=" Diagnóstico Rápido y Bienestar Diario ",
            font=("Segoe UI", 10, "bold"), bg="white", padx=12, pady=8
        )
        frame_estado.pack(fill="x", pady=(0, 10))

        self.lbl_diagnostico = tk.Label(
            frame_estado, text="Estado: Cargando...", font=("Segoe UI", 10, "bold"),
            bg="white", fg="#1F4E78"
        )
        self.lbl_diagnostico.pack(anchor="w")

        frame_progreso = tk.Frame(frame_estado, bg="white")
        frame_progreso.pack(fill="x", pady=(6, 2))

        self.lbl_progreso = tk.Label(
            frame_progreso, text="Rutina diaria completada: 0%",
            font=("Segoe UI", 9), bg="white"
        )
        self.lbl_progreso.pack(side="left")

        # ELEMENTO ADICIONAL NO EXPLICADO EN CLASE: ttk.Progressbar
        self.barra_bienestar = ttk.Progressbar(
            frame_progreso, orient="horizontal", length=320, mode="determinate", maximum=100
        )
        self.barra_bienestar.pack(side="right", fill="x", expand=True, padx=(12, 0))

        # Sub-frame Bitácora (Checkbutton filtro + Treeview)
        frame_tabla = tk.LabelFrame(
            frame_derecho, text=" Bitácora Histórica (Persistida en Excel) ",
            font=("Segoe UI", 10, "bold"), bg="white", padx=10, pady=8
        )
        frame_tabla.pack(fill="both", expand=True)

        tk.Checkbutton(
            frame_tabla, text="Mostrar únicamente registros clínicos / veterinarios",
            variable=self.var_solo_clinicos, command=self.__refrescar_treeview,
            bg="white", font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(0, 6))

        columnas = ("ID", "Fecha", "Mascota", "Tipo", "Actividad", "Responsable", "Prioridad", "Observaciones")
        self.tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=16)

        anchos = {
            "ID": 40, "Fecha": 130, "Mascota": 75, "Tipo": 70,
            "Actividad": 115, "Responsable": 145, "Prioridad": 80, "Observaciones": 180
        }
        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=anchos[col], anchor="center" if col in ("ID", "Tipo", "Prioridad") else "w")

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Evento .bind() en el Treeview
        self.tree.bind("<<TreeviewSelect>>", self.__seleccionar_fila_tree)

    def __actualizar_tareas_por_usuario(self, event=None):
        etiqueta_usuario = self.var_usuario.get()
        usuario = self.__usuarios.get(etiqueta_usuario)
        if usuario:
            tareas = usuario.obtener_tareas_disponibles()
            self.combo_actividad["values"] = tareas
            if tareas:
                self.combo_actividad.current(0)

    def __cargar_datos_desde_excel(self):
        try:
            for m in self.__mascotas.values():
                m.reiniciar_estado_diario()
                m._Mascota__historial.clear()

            registros = self.__backend.leer_registros()
            for reg in registros:
                nombre_m = reg.obtener_mascota()
                if nombre_m not in self.__mascotas:
                    self.__mascotas[nombre_m] = Mascota(nombre_m)
                self.__mascotas[nombre_m].cargar_registro_existente(reg)

            self.combo_mascota["values"] = list(self.__mascotas.keys())
            self.__refrescar_treeview()
            self.__actualizar_panel_bienestar()
        except Exception as e:
            messagebox.showerror("Error de Lectura", f"No se pudo leer el archivo Excel:\n{e}")

    def __refrescar_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        registros = self.__backend.leer_registros()
        solo_clinicos = self.var_solo_clinicos.get()

        for reg in registros:
            if solo_clinicos and not reg.es_clinico():
                continue
            self.tree.insert("", "end", values=reg.a_fila_excel())

    def __actualizar_panel_bienestar(self):
        nombre_m = self.var_mascota.get()
        mascota = self.__mascotas.get(nombre_m)
        if not mascota:
            return

        texto_estado, color = self.__sistema_alertas.evaluar_estado(mascota)
        porcentaje = self.__sistema_alertas.calcular_progreso_diario(mascota)

        self.lbl_diagnostico.config(text=texto_estado, fg=color)
        self.lbl_progreso.config(text=f"Rutina diaria de {nombre_m} completada: {porcentaje}%")
        self.barra_bienestar["value"] = porcentaje

    def __registrar_actividad(self):
        try:
            nombre_m = self.var_mascota.get()
            etiqueta_u = self.var_usuario.get()
            actividad = self.var_actividad.get()
            obs = self.var_observaciones.get()
            prioridad = self.var_prioridad.get()

            if not nombre_m or not etiqueta_u or not actividad:
                raise ValueError("Debes seleccionar mascota, responsable y actividad.")

            mascota = self.__mascotas[nombre_m]
            usuario = self.__usuarios[etiqueta_u]

            # Llamada polimórfica y validación de reglas de salud
            nuevo_registro = usuario.realizar_tarea(mascota, actividad, obs, prioridad)
            self.__backend.guardar_registro(nuevo_registro)

            self.__refrescar_treeview()
            self.__actualizar_panel_bienestar()
            self.__limpiar_formulario()
            messagebox.showinfo("Registro Exitoso", f"Actividad '{actividad}' guardada en Excel para {nombre_m}.")

        except ValueError as error_validacion:
            messagebox.showwarning("Alerta de Seguridad Petly", str(error_validacion))
        except PermissionError:
            messagebox.showerror("Archivo Bloqueado", "Cierra el archivo Excel antes de guardar nuevos registros.")
        except Exception as e:
            messagebox.showerror("Error del Sistema", f"Ocurrió un fallo inesperado:\n{e}")

    def __seleccionar_fila_tree(self, event):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        valores = self.tree.item(seleccion[0], "values")
        self.__id_seleccionado = valores[0]
        self.var_mascota.set(valores[2])
        self.var_actividad.set(valores[4])
        self.var_prioridad.set(valores[6])
        self.var_observaciones.set(valores[7])
        self.__actualizar_panel_bienestar()

    def __actualizar_registro(self):
        try:
            if not self.__id_seleccionado:
                raise ValueError("Selecciona primero un registro en la tabla para actualizarlo.")

            etiqueta_u = self.var_usuario.get()
            usuario = self.__usuarios.get(etiqueta_u)
            autor = usuario.obtener_nombre() if usuario else "Sistema"

            exito = self.__backend.actualizar_registro(
                self.__id_seleccionado,
                self.var_actividad.get(),
                autor,
                self.var_prioridad.get(),
                self.var_observaciones.get()
            )
            if exito:
                self.__cargar_datos_desde_excel()
                self.__limpiar_formulario()
                messagebox.showinfo("Actualizado", "El registro fue modificado correctamente en Excel.")
        except ValueError as ve:
            messagebox.showwarning("Selección Requerida", str(ve))
        except Exception as e:
            messagebox.showerror("Error al Actualizar", str(e))

    def __eliminar_registro(self):
        try:
            if not self.__id_seleccionado:
                raise ValueError("Selecciona primero un registro en la tabla para eliminarlo.")

            confirmar = messagebox.askyesno(
                "Confirmar Eliminación",
                f"¿Deseas eliminar permanentemente el registro ID #{self.__id_seleccionado}?"
            )
            if confirmar:
                if self.__backend.eliminar_registro(self.__id_seleccionado):
                    self.__cargar_datos_desde_excel()
                    self.__limpiar_formulario()
                    messagebox.showinfo("Eliminado", "Registro eliminado de la base de datos Excel.")
        except ValueError as ve:
            messagebox.showwarning("Selección Requerida", str(ve))
        except Exception as e:
            messagebox.showerror("Error al Eliminar", str(e))

    def __limpiar_formulario(self):
        self.__id_seleccionado = None
        self.var_observaciones.set("")
        self.var_prioridad.set("Normal")
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def __abrir_excel(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo Excel de Petly",
            filetypes=[("Archivos Excel", "*.xlsx")]
        )
        if ruta:
            try:
                self.__backend.cambiar_ruta(ruta)
                self.lbl_archivo_actual.config(text=f"Excel: {ruta}")
                self.__cargar_datos_desde_excel()
                messagebox.showinfo("Archivo Cargado", "Base de datos Excel vinculada correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")

    def __exportar_excel(self):
        ruta = filedialog.asksaveasfilename(
            title="Guardar respaldo Excel",
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx")]
        )
        if ruta:
            try:
                self.__backend.exportar_copia(ruta)
                messagebox.showinfo("Respaldo Exitoso", f"Copia guardada en:\n{ruta}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar la copia:\n{e}")

    def __reiniciar_alertas_dia(self):
        for m in self.__mascotas.values():
            m.reiniciar_estado_diario()
        self.__actualizar_panel_bienestar()
        messagebox.showinfo("Estado Reiniciado", "Se han reiniciado los bloqueos diarios de alimentación y medicamento.")

    def __mostrar_acerca_de(self):
        messagebox.showinfo(
            "Acerca de Petly",
            "Petly v3.0 - Programación II\nGestión orientada a objetos de salud y cuidados de mascotas con persistencia en Excel."
        )

    # --- VENTANA SECUNDARIA (Toplevel) ---
    def __abrir_ventana_secundaria(self):
        ventana_sec = tk.Toplevel(self.root)
        ventana_sec.title("Petly - Gestión de Mascotas y Recordatorios")
        ventana_sec.geometry("540x480")
        ventana_sec.configure(bg="#F4F6F9")
        ventana_sec.grab_set()

        # Sección 1: Agregar Mascota
        frame_m = tk.LabelFrame(ventana_sec, text=" Registrar Nueva Mascota ", bg="white", padx=12, pady=10, font=("Segoe UI", 9, "bold"))
        frame_m.pack(fill="x", padx=12, pady=10)

        var_nom = tk.StringVar()
        var_esp = tk.StringVar(value="Perro")
        var_raza = tk.StringVar()
        var_peso = tk.StringVar()

        tk.Label(frame_m, text="Nombre:", bg="white").grid(row=0, column=0, sticky="w")
        tk.Entry(frame_m, textvariable=var_nom, width=18).grid(row=0, column=1, padx=5, pady=3)

        tk.Label(frame_m, text="Especie:", bg="white").grid(row=0, column=2, sticky="w")
        ttk.Combobox(frame_m, textvariable=var_esp, values=["Perro", "Gato", "Ave", "Otro"], state="readonly", width=15).grid(row=0, column=3, padx=5, pady=3)

        tk.Label(frame_m, text="Raza:", bg="white").grid(row=1, column=0, sticky="w")
        tk.Entry(frame_m, textvariable=var_raza, width=18).grid(row=1, column=1, padx=5, pady=3)

        tk.Label(frame_m, text="Peso (kg):", bg="white").grid(row=1, column=2, sticky="w")
        tk.Entry(frame_m, textvariable=var_peso, width=18).grid(row=1, column=3, padx=5, pady=3)

        def agregar_mascota():
            try:
                nombre = var_nom.get().strip()
                if not nombre:
                    raise ValueError("El nombre de la mascota es obligatorio.")
                peso = float(var_peso.get())
                if peso <= 0:
                    raise ValueError("El peso debe ser mayor a cero.")

                nueva_m = Mascota(nombre, var_esp.get(), var_raza.get().strip() or "Mestizo", peso)
                if not self.__backend.guardar_mascota(nueva_m):
                    raise ValueError(f"La mascota '{nombre}' ya existe.")

                self.__mascotas[nombre] = nueva_m
                self.combo_mascota["values"] = list(self.__mascotas.keys())
                self.var_mascota.set(nombre)
                self.__actualizar_panel_bienestar()
                messagebox.showinfo("Mascota Agregada", f"{nombre} fue registrada en el sistema.", parent=ventana_sec)
                var_nom.set("")
                var_raza.set("")
                var_peso.set("")
            except ValueError as ve:
                messagebox.showwarning("Dato Inválido", str(ve), parent=ventana_sec)

        tk.Button(
            frame_m, text="Guardar Mascota", command=agregar_mascota,
            bg="#2E8B57", fg="white", font=("Segoe UI", 9, "bold")
        ).grid(row=2, column=0, columnspan=4, sticky="ew", pady=(8, 0))

        # Sección 2: Recordatorios
        frame_r = tk.LabelFrame(ventana_sec, text=" Agenda de Recordatorios ", bg="white", padx=12, pady=10, font=("Segoe UI", 9, "bold"))
        frame_r.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        lista_rec = tk.Listbox(frame_r, height=8, font=("Segoe UI", 9))
        lista_rec.pack(fill="both", expand=True, pady=(0, 8))

        def refrescar_lista_rec():
            lista_rec.delete(0, tk.END)
            for r in self.__recordatorios:
                lista_rec.insert(tk.END, r.obtener_resumen())

        refrescar_lista_rec()

        frame_nuevo_rec = tk.Frame(frame_r, bg="white")
        frame_nuevo_rec.pack(fill="x")

        var_hora = tk.StringVar(value="09:00")
        var_desc_rec = tk.StringVar()

        tk.Entry(frame_nuevo_rec, textvariable=var_hora, width=8).pack(side="left", padx=(0, 5))
        tk.Entry(frame_nuevo_rec, textvariable=var_desc_rec, width=28).pack(side="left", fill="x", expand=True, padx=(0, 5))

        def agregar_recordatorio():
            desc = var_desc_rec.get().strip()
            if not desc:
                messagebox.showwarning("Campo Vacío", "Escribe la descripción del recordatorio.", parent=ventana_sec)
                return
            nuevo_id = len(self.__recordatorios) + 1
            rec = Recordatorio(nuevo_id, self.var_mascota.get(), var_hora.get().strip(), desc, self.var_usuario.get())
            self.__recordatorios.append(rec)
            var_desc_rec.set("")
            refrescar_lista_rec()

        def completar_recordatorio():
            sel = lista_rec.curselection()
            if sel:
                self.__recordatorios[sel[0]].marcar_completado()
                refrescar_lista_rec()

        tk.Button(frame_nuevo_rec, text="Añadir", command=agregar_recordatorio, bg="#1F4E78", fg="white").pack(side="left", padx=(0, 4))
        tk.Button(frame_nuevo_rec, text="Completar", command=completar_recordatorio, bg="#2E8B57", fg="white").pack(side="left")

    def iniciar(self):
        self.root.mainloop()