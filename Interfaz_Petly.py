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

        self.__sincronizar_mascotas(mascotas_base)

        # Ventana principal más compacta
        self.root = tk.Tk()
        self.root.title("Petly - Cuidado de Mascotas")
        self.root.geometry("950x560")
        self.root.configure(bg="#F4F6F9")

        # Variables de control
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
        menu_archivo.add_command(label="Abrir Excel...", command=self.__abrir_excel)
        menu_archivo.add_command(label="Exportar copia...", command=self.__exportar_excel)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.root.quit)
        barra_menu.add_cascade(label="Archivo", menu=menu_archivo)

        menu_gestion = tk.Menu(barra_menu, tearoff=0)
        menu_gestion.add_command(label="Mascotas y Recordatorios", command=self.__abrir_ventana_secundaria)
        menu_gestion.add_command(label="Reiniciar alertas del día", command=self.__reiniciar_alertas_dia)
        barra_menu.add_cascade(label="Gestión", menu=menu_gestion)

        self.root.config(menu=barra_menu)

    def __construir_interfaz(self):
        # Encabezado simple
        header = tk.Frame(self.root, bg="#1F4E78", padx=15, pady=8)
        header.pack(fill="x")

        tk.Label(
            header, text="🐾 PETLY | Control de Mascotas",
            font=("Segoe UI", 13, "bold"), bg="#1F4E78", fg="white"
        ).pack(side="left")

        self.lbl_archivo_actual = tk.Label(
            header, text=f"Archivo: {self.__backend.obtener_ruta()}",
            font=("Segoe UI", 9), bg="#1F4E78", fg="#D9E2EC"
        )
        self.lbl_archivo_actual.pack(side="right")

        # Contenedor principal
        contenedor = tk.Frame(self.root, bg="#F4F6F9", padx=10, pady=10)
        contenedor.pack(fill="both", expand=True)

        # --- PANEL IZQUIERDO: FORMULARIO ---
        form = tk.LabelFrame(contenedor, text=" Registrar Actividad ", bg="white", padx=12, pady=10, font=("Segoe UI", 9, "bold"))
        form.pack(side="left", fill="y", padx=(0, 10))

        tk.Label(form, text="Mascota:", bg="white").pack(anchor="w")
        self.combo_mascota = ttk.Combobox(form, textvariable=self.var_mascota, values=list(self.__mascotas.keys()), state="readonly", width=28)
        self.combo_mascota.pack(fill="x", pady=(2, 8))
        if self.__mascotas:
            self.combo_mascota.current(0)
        self.combo_mascota.bind("<<ComboboxSelected>>", lambda e: self.__actualizar_panel_bienestar())

        tk.Label(form, text="Responsable:", bg="white").pack(anchor="w")
        self.combo_usuario = ttk.Combobox(form, textvariable=self.var_usuario, values=list(self.__usuarios.keys()), state="readonly", width=28)
        self.combo_usuario.pack(fill="x", pady=(2, 8))
        self.combo_usuario.bind("<<ComboboxSelected>>", self.__actualizar_tareas_por_usuario)

        tk.Label(form, text="Actividad:", bg="white").pack(anchor="w")
        self.combo_actividad = ttk.Combobox(form, textvariable=self.var_actividad, state="readonly", width=28)
        self.combo_actividad.pack(fill="x", pady=(2, 8))

        if self.__usuarios:
            self.combo_usuario.current(0)
            self.__actualizar_tareas_por_usuario()

        tk.Label(form, text="Prioridad:", bg="white").pack(anchor="w")
        frame_radios = tk.Frame(form, bg="white")
        frame_radios.pack(fill="x", pady=(2, 8))
        for nivel in ["Normal", "Importante", "Urgente"]:
            tk.Radiobutton(frame_radios, text=nivel, variable=self.var_prioridad, value=nivel, bg="white").pack(side="left", padx=(0, 6))

        tk.Label(form, text="Observaciones:", bg="white").pack(anchor="w")
        self.entry_obs = tk.Entry(form, textvariable=self.var_observaciones, width=30)
        self.entry_obs.pack(fill="x", pady=(2, 12))
        self.entry_obs.bind("<Return>", lambda e: self.__registrar_actividad())

        # Botón principal + fila compacta de acciones
        tk.Button(
            form, text="Guardar Actividad", command=self.__registrar_actividad,
            bg="#2E8B57", fg="white", font=("Segoe UI", 9, "bold"), pady=5
        ).pack(fill="x", pady=(0, 6))

        fila_botones = tk.Frame(form, bg="white")
        fila_botones.pack(fill="x")
        tk.Button(fila_botones, text="Editar", command=self.__actualizar_registro, bg="#2B6CB0", fg="white").pack(side="left", expand=True, fill="x", padx=(0, 3))
        tk.Button(fila_botones, text="Eliminar", command=self.__eliminar_registro, bg="#C53030", fg="white").pack(side="left", expand=True, fill="x", padx=3)
        tk.Button(fila_botones, text="Limpiar", command=self.__limpiar_formulario, bg="#718096", fg="white").pack(side="left", expand=True, fill="x", padx=(3, 0))

        # --- PANEL DERECHO: ESTADO + TABLA ---
        derecho = tk.Frame(contenedor, bg="#F4F6F9")
        derecho.pack(side="right", fill="both", expand=True)

        # Estado y barra de progreso
        panel_estado = tk.LabelFrame(derecho, text=" Estado Diario ", bg="white", padx=10, pady=8, font=("Segoe UI", 9, "bold"))
        panel_estado.pack(fill="x", pady=(0, 8))

        self.lbl_diagnostico = tk.Label(panel_estado, text="Estado: Cargando...", font=("Segoe UI", 9, "bold"), bg="white", fg="#1F4E78")
        self.lbl_diagnostico.pack(anchor="w")

        self.lbl_progreso = tk.Label(panel_estado, text="Rutina completada: 0%", font=("Segoe UI", 8), bg="white")
        self.lbl_progreso.pack(anchor="w", pady=(4, 2))

        self.barra_bienestar = ttk.Progressbar(panel_estado, orient="horizontal", mode="determinate", maximum=100)
        self.barra_bienestar.pack(fill="x")

        # Tabla histórica
        panel_tabla = tk.LabelFrame(derecho, text=" Bitácora de Actividades ", bg="white", padx=10, pady=8, font=("Segoe UI", 9, "bold"))
        panel_tabla.pack(fill="both", expand=True)

        tk.Checkbutton(
            panel_tabla, text="Solo registros clínicos", variable=self.var_solo_clinicos,
            command=self.__refrescar_treeview, bg="white"
        ).pack(anchor="w", pady=(0, 5))

        columnas = ("ID", "Fecha", "Mascota", "Tipo", "Actividad", "Responsable", "Prioridad", "Observaciones")
        visibles = ("ID", "Fecha", "Mascota", "Actividad", "Responsable", "Prioridad", "Observaciones")
        self.tree = ttk.Treeview(panel_tabla, columns=columnas, displaycolumns=visibles, show="headings", height=14)

        anchos = {"ID": 35, "Fecha": 120, "Mascota": 70, "Actividad": 110, "Responsable": 130, "Prioridad": 75, "Observaciones": 160}
        for col in visibles:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=anchos[col], anchor="center" if col in ("ID", "Prioridad") else "w")

        scroll = ttk.Scrollbar(panel_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.__seleccionar_fila_tree)

    def __actualizar_tareas_por_usuario(self, event=None):
        usuario = self.__usuarios.get(self.var_usuario.get())
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

            for reg in self.__backend.leer_registros():
                nombre_m = reg.obtener_mascota()
                if nombre_m not in self.__mascotas:
                    self.__mascotas[nombre_m] = Mascota(nombre_m)
                self.__mascotas[nombre_m].cargar_registro_existente(reg)

            self.combo_mascota["values"] = list(self.__mascotas.keys())
            self.__refrescar_treeview()
            self.__actualizar_panel_bienestar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el Excel:\n{e}")

    def __refrescar_treeview(self):
        self.tree.delete(*self.tree.get_children())
        solo_clinicos = self.var_solo_clinicos.get()

        for reg in self.__backend.leer_registros():
            if not (solo_clinicos and not reg.es_clinico()):
                self.tree.insert("", "end", values=reg.a_fila_excel())

    def __actualizar_panel_bienestar(self):
        mascota = self.__mascotas.get(self.var_mascota.get())
        if not mascota:
            return
        texto_estado, color = self.__sistema_alertas.evaluar_estado(mascota)
        porcentaje = self.__sistema_alertas.calcular_progreso_diario(mascota)

        self.lbl_diagnostico.config(text=texto_estado, fg=color)
        self.lbl_progreso.config(text=f"Rutina de {mascota.obtener_nombre()} completada: {porcentaje}%")
        self.barra_bienestar["value"] = porcentaje

    def __registrar_actividad(self):
        try:
            nombre_m = self.var_mascota.get()
            etiqueta_u = self.var_usuario.get()
            actividad = self.var_actividad.get()
            if not nombre_m or not etiqueta_u or not actividad:
                raise ValueError("Completa mascota, responsable y actividad.")

            nuevo_registro = self.__usuarios[etiqueta_u].realizar_tarea(
                self.__mascotas[nombre_m], actividad, self.var_observaciones.get(), self.var_prioridad.get()
            )
            self.__backend.guardar_registro(nuevo_registro)
            self.__refrescar_treeview()
            self.__actualizar_panel_bienestar()
            self.__limpiar_formulario()
            messagebox.showinfo("Listo", f"Actividad '{actividad}' registrada.")
        except ValueError as ve:
            messagebox.showwarning("Aviso", str(ve))
        except PermissionError:
            messagebox.showerror("Error", "Cierra el archivo Excel antes de guardar.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def __seleccionar_fila_tree(self, event):
        seleccion = self.tree.selection()
        if seleccion:
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
                raise ValueError("Selecciona un registro de la tabla para editar.")
            usuario = self.__usuarios.get(self.var_usuario.get())
            autor = usuario.obtener_nombre() if usuario else "Sistema"

            if self.__backend.actualizar_registro(
                self.__id_seleccionado, self.var_actividad.get(), autor,
                self.var_prioridad.get(), self.var_observaciones.get()
            ):
                self.__cargar_datos_desde_excel()
                self.__limpiar_formulario()
                messagebox.showinfo("Actualizado", "Registro modificado correctamente.")
        except Exception as e:
            messagebox.showwarning("Aviso", str(e))

    def __eliminar_registro(self):
        try:
            if not self.__id_seleccionado:
                raise ValueError("Selecciona un registro de la tabla para eliminar.")
            if messagebox.askyesno("Confirmar", f"¿Eliminar el registro #{self.__id_seleccionado}?"):
                if self.__backend.eliminar_registro(self.__id_seleccionado):
                    self.__cargar_datos_desde_excel()
                    self.__limpiar_formulario()
        except Exception as e:
            messagebox.showwarning("Aviso", str(e))

    def __limpiar_formulario(self):
        self.__id_seleccionado = None
        self.var_observaciones.set("")
        self.var_prioridad.set("Normal")
        self.tree.selection_remove(*self.tree.selection())

    def __abrir_excel(self):
        ruta = filedialog.askopenfilename(title="Abrir Excel", filetypes=[("Excel", "*.xlsx")])
        if ruta:
            self.__backend.cambiar_ruta(ruta)
            self.lbl_archivo_actual.config(text=f"Archivo: {ruta}")
            self.__cargar_datos_desde_excel()

    def __exportar_excel(self):
        ruta = filedialog.asksaveasfilename(title="Exportar copia", defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if ruta:
            self.__backend.exportar_copia(ruta)
            messagebox.showinfo("Exportado", "Copia guardada correctamente.")

    def __reiniciar_alertas_dia(self):
        for m in self.__mascotas.values():
            m.reiniciar_estado_diario()
        self.__actualizar_panel_bienestar()
        messagebox.showinfo("Reiniciado", "Alertas diarias reiniciadas.")

    def __abrir_ventana_secundaria(self):
        win = tk.Toplevel(self.root)
        win.title("Mascotas y Recordatorios")
        win.geometry("450x420")
        win.configure(bg="#F4F6F9")
        win.grab_set()

        # Nueva mascota
        frame_m = tk.LabelFrame(win, text=" Nueva Mascota ", bg="white", padx=10, pady=8, font=("Segoe UI", 9, "bold"))
        frame_m.pack(fill="x", padx=10, pady=8)

        var_nom, var_esp, var_raza, var_peso = tk.StringVar(), tk.StringVar(value="Perro"), tk.StringVar(), tk.StringVar()

        tk.Label(frame_m, text="Nombre:", bg="white").grid(row=0, column=0, sticky="w")
        tk.Entry(frame_m, textvariable=var_nom, width=16).grid(row=0, column=1, padx=4, pady=2)
        tk.Label(frame_m, text="Especie:", bg="white").grid(row=0, column=2, sticky="w")
        ttk.Combobox(frame_m, textvariable=var_esp, values=["Perro", "Gato", "Ave", "Otro"], state="readonly", width=13).grid(row=0, column=3, padx=4, pady=2)

        tk.Label(frame_m, text="Raza:", bg="white").grid(row=1, column=0, sticky="w")
        tk.Entry(frame_m, textvariable=var_raza, width=16).grid(row=1, column=1, padx=4, pady=2)
        tk.Label(frame_m, text="Peso (kg):", bg="white").grid(row=1, column=2, sticky="w")
        tk.Entry(frame_m, textvariable=var_peso, width=16).grid(row=1, column=3, padx=4, pady=2)

        def guardar_mascota():
            try:
                nombre = var_nom.get().strip()
                peso = float(var_peso.get())
                if not nombre or peso <= 0:
                    raise ValueError("Ingresa un nombre válido y un peso mayor a 0.")
                nueva = Mascota(nombre, var_esp.get(), var_raza.get().strip() or "Mestizo", peso)
                if not self.__backend.guardar_mascota(nueva):
                    raise ValueError("Esa mascota ya existe.")
                self.__mascotas[nombre] = nueva
                self.combo_mascota["values"] = list(self.__mascotas.keys())
                self.var_mascota.set(nombre)
                self.__actualizar_panel_bienestar()
                var_nom.set(""); var_raza.set(""); var_peso.set("")
                messagebox.showinfo("Guardado", f"{nombre} agregada.", parent=win)
            except ValueError as e:
                messagebox.showwarning("Aviso", str(e), parent=win)

        tk.Button(frame_m, text="Agregar Mascota", command=guardar_mascota, bg="#2E8B57", fg="white").grid(row=2, column=0, columnspan=4, sticky="ew", pady=(6, 0))

        # Recordatorios
        frame_r = tk.LabelFrame(win, text=" Recordatorios ", bg="white", padx=10, pady=8, font=("Segoe UI", 9, "bold"))
        frame_r.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        lista = tk.Listbox(frame_r, height=7)
        lista.pack(fill="both", expand=True, pady=(0, 6))

        def refrescar():
            lista.delete(0, tk.END)
            for r in self.__recordatorios:
                lista.insert(tk.END, r.obtener_resumen())

        refrescar()

        fila_rec = tk.Frame(frame_r, bg="white")
        fila_rec.pack(fill="x")
        var_hora, var_desc = tk.StringVar(value="09:00"), tk.StringVar()
        tk.Entry(fila_rec, textvariable=var_hora, width=7).pack(side="left", padx=(0, 4))
        tk.Entry(fila_rec, textvariable=var_desc).pack(side="left", fill="x", expand=True, padx=(0, 4))

        def añadir_rec():
            if var_desc.get().strip():
                self.__recordatorios.append(Recordatorio(len(self.__recordatorios) + 1, self.var_mascota.get(), var_hora.get(), var_desc.get().strip(), self.var_usuario.get()))
                var_desc.set("")
                refrescar()

        def completar_rec():
            if lista.curselection():
                self.__recordatorios[lista.curselection()[0]].marcar_completado()
                refrescar()

        tk.Button(fila_rec, text="+", command=añadir_rec, bg="#1F4E78", fg="white", width=3).pack(side="left", padx=(0, 2))
        tk.Button(fila_rec, text="✓", command=completar_rec, bg="#2E8B57", fg="white", width=3).pack(side="left")

    def iniciar(self):
        self.root.mainloop()