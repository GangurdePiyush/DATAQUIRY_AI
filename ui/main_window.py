"""
ui/main_window.py
-----------------
Tkinter Desktop GUI for the Simple Dataset Upload & Query System.
Part 6 Integration: Voice interaction (Speech-to-Text microphone recording,
auto-populating question entries, and offline Text-to-Speech query result summaries).
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import threading

import config
from dataset import DatasetHandler
from database import DatabaseHandler
from query import QueryEngine, is_safe_sql
from voice import VoiceHandler


class MainWindow(tk.Tk):
    """
    Main application window built using Python Tkinter.
    Organizes the UI into clear, professional sections.
    """

    def __init__(self):
        super().__init__()

        # Initialize core module handlers
        self.dataset_handler = DatasetHandler()
        self.db_handler = DatabaseHandler()
        self.query_engine = QueryEngine()
        self.voice_handler = VoiceHandler()

        # State Variables
        self.manual_sql_mode = False
        self.latest_query_result = None

        # Window Setup
        self.title(config.APP_TITLE)
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.minsize(config.MIN_WIDTH, config.MIN_HEIGHT)
        self.configure(bg=config.COLOR_BG)

        # Apply TTK Theme and Custom Styles
        self._setup_styles()

        # Build UI Components
        self._create_header()
        self._create_main_content()
        self._create_footer()

    def _setup_styles(self):
        """Configure standard TTK styles for consistent UI appearance."""
        self.style = ttk.Style()

        # Select native base theme
        theme_names = self.style.theme_names()
        if "clam" in theme_names:
            self.style.theme_use("clam")

        # LabelFrame Style
        self.style.configure(
            "TLabelframe",
            background=config.COLOR_CARD_BG,
            bordercolor="#BDC3C7",
            lightcolor="#BDC3C7",
            darkcolor="#BDC3C7",
            borderwidth=1,
            relief="solid",
        )
        self.style.configure(
            "TLabelframe.Label",
            background=config.COLOR_CARD_BG,
            foreground=config.COLOR_PRIMARY,
            font=config.FONT_TITLE,
        )

        # Frame Style
        self.style.configure("Card.TFrame", background=config.COLOR_CARD_BG)
        self.style.configure("Main.TFrame", background=config.COLOR_BG)

        # Button Styles
        self.style.configure(
            "Primary.TButton",
            font=config.FONT_BUTTON,
            background=config.COLOR_PRIMARY,
            foreground="white",
            padding=(8, 4),
        )
        self.style.map(
            "Primary.TButton",
            background=[("active", config.COLOR_ACCENT)],
            foreground=[("active", "white")],
        )

        self.style.configure(
            "Accent.TButton",
            font=config.FONT_BUTTON,
            background=config.COLOR_ACCENT,
            foreground="white",
            padding=(8, 4),
        )

        self.style.configure(
            "Execute.TButton",
            font=config.FONT_BUTTON,
            background=config.COLOR_SUCCESS,
            foreground="white",
            padding=(8, 4),
        )
        self.style.map(
            "Execute.TButton",
            background=[("active", "#27AE60")],
            foreground=[("active", "white")],
        )

        self.style.configure(
            "Danger.TButton",
            font=config.FONT_BUTTON,
            background=config.COLOR_DANGER,
            foreground="white",
            padding=(8, 4),
        )
        self.style.map(
            "Danger.TButton",
            background=[("active", "#C0392B")],
            foreground=[("active", "white")],
        )

        # Treeview Style for Dataset & Query Results Tables
        self.style.configure(
            "Treeview",
            font=config.FONT_BODY,
            rowheight=24,
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground=config.COLOR_TEXT_PRIMARY,
        )
        self.style.configure(
            "Treeview.Heading",
            font=config.FONT_SUBHEADER,
            background=config.COLOR_PRIMARY,
            foreground="white",
            relief="flat",
        )
        self.style.map("Treeview.Heading", background=[("active", config.COLOR_ACCENT)])

    def _create_header(self):
        """Creates the header banner at the top of the window."""
        header_frame = tk.Frame(self, bg=config.COLOR_PRIMARY, height=70, padx=20, pady=12)
        header_frame.pack(fill=tk.X, side=tk.TOP)

        # Application Title
        title_label = tk.Label(
            header_frame,
            text=config.APP_TITLE,
            font=config.FONT_HEADER,
            bg=config.COLOR_PRIMARY,
            fg="white",
            anchor="w",
        )
        title_label.pack(side=tk.TOP, fill=tk.X)

        # Subtitle / Version Info
        subtitle_label = tk.Label(
            header_frame,
            text="College Project Shell | Part 6 - Voice Interaction & Audio Result Summaries",
            font=config.FONT_MUTED,
            bg=config.COLOR_PRIMARY,
            fg="#BDC3C7",
            anchor="w",
        )
        subtitle_label.pack(side=tk.TOP, fill=tk.X)

    def _create_main_content(self):
        """Creates the main grid container for all sections."""
        main_container = ttk.Frame(self, style="Main.TFrame", padding=15)
        main_container.pack(fill=tk.BOTH, expand=True)

        # 2-column layout
        main_container.columnconfigure(0, weight=1, uniform="group1")
        main_container.columnconfigure(1, weight=1, uniform="group1")
        main_container.rowconfigure(0, weight=1)

        # Left Column (Dataset Upload, Dataset Information & Database Schema, Voice Input)
        left_column = ttk.Frame(main_container, style="Main.TFrame")
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)

        # Right Column (Ask Question & SQL Generation, SQL Query Execution & Results)
        right_column = ttk.Frame(main_container, style="Main.TFrame")
        right_column.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=0)

        # Build sections
        self._build_dataset_upload_section(left_column)
        self._build_dataset_info_section(left_column)
        self._build_voice_section(left_column)

        self._build_ask_question_section(right_column)
        self._build_results_section(right_column)

    def _build_dataset_upload_section(self, parent):
        """1. Dataset Upload Section"""
        frame = ttk.LabelFrame(parent, text=" 📁 1. Dataset Upload ", padding=10)
        frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 10))

        desc = tk.Label(
            frame,
            text="Select a CSV or Excel file (.csv, .xlsx, .xls) to upload and save into SQLite:",
            font=config.FONT_BODY,
            bg=config.COLOR_CARD_BG,
            fg=config.COLOR_TEXT_PRIMARY,
            anchor="w",
            justify=tk.LEFT,
        )
        desc.pack(fill=tk.X, pady=(0, 6))

        # File Selection Row
        row = ttk.Frame(frame, style="Card.TFrame")
        row.pack(fill=tk.X, pady=(0, 6))

        self.file_path_var = tk.StringVar(value="No file selected...")
        path_entry = ttk.Entry(row, textvariable=self.file_path_var, state="readonly", font=config.FONT_BODY)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        browse_btn = ttk.Button(row, text="Browse...", style="Primary.TButton", command=self._on_browse_clicked)
        browse_btn.pack(side=tk.RIGHT)

        # Upload & Process Button
        upload_btn = ttk.Button(
            frame,
            text="Upload & Build SQLite DB",
            style="Accent.TButton",
            command=self._on_upload_clicked,
        )
        upload_btn.pack(anchor="e")

    def _build_dataset_info_section(self, parent):
        """2. Dataset Information & Database Schema Section"""
        frame = ttk.LabelFrame(parent, text=" 📊 2. Dataset Metadata & SQLite Schema ", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP, pady=(0, 10))

        # Metadata & Database Summary Banner
        self.meta_frame = tk.Frame(frame, bg="#F1F2F6", bd=1, relief="solid", padx=8, pady=6)
        self.meta_frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 6))

        self.lbl_status = tk.Label(self.meta_frame, text="Status: No dataset loaded", font=config.FONT_SUBHEADER, bg="#F1F2F6", fg=config.COLOR_TEXT_MUTED, anchor="w")
        self.lbl_status.pack(fill=tk.X)

        self.lbl_db_status = tk.Label(
            self.meta_frame,
            text="SQLite DB Status: Database Inactive (data/app.db)",
            font=config.FONT_BODY,
            bg="#F1F2F6",
            fg=config.COLOR_TEXT_MUTED,
            anchor="w",
        )
        self.lbl_db_status.pack(fill=tk.X, pady=(2, 0))

        self.lbl_details = tk.Label(
            self.meta_frame,
            text="File: N/A  |  Rows: 0  |  Columns: 0",
            font=config.FONT_BODY,
            bg="#F1F2F6",
            fg=config.COLOR_TEXT_PRIMARY,
            anchor="w",
        )
        self.lbl_details.pack(fill=tk.X, pady=(2, 0))

        # Schema Display Box
        self.lbl_schema = tk.Label(
            self.meta_frame,
            text="Detected SQLite Schema: None",
            font=config.FONT_MUTED,
            bg="#F1F2F6",
            fg=config.COLOR_TEXT_MUTED,
            anchor="w",
            wraplength=400,
            justify=tk.LEFT,
        )
        self.lbl_schema.pack(fill=tk.X, pady=(2, 0))

        # Tabular Preview Container (Treeview with Scrollbars)
        tbl_container = ttk.Frame(frame)
        tbl_container.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tbl_container, columns=(), show="headings", height=4)

        v_scroll = ttk.Scrollbar(tbl_container, orient=tk.VERTICAL, command=self.tree.yview)
        h_scroll = ttk.Scrollbar(tbl_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        tbl_container.columnconfigure(0, weight=1)
        tbl_container.rowconfigure(0, weight=1)

    def _build_voice_section(self, parent):
        """3. Voice Input & Audio Controls Section"""
        frame = ttk.LabelFrame(parent, text=" 🎙️ 3. Voice Interaction & Controls ", padding=10)
        frame.pack(fill=tk.X, side=tk.TOP)

        desc = tk.Label(
            frame,
            text="Speak your question via microphone or listen to query result summaries:",
            font=config.FONT_BODY,
            bg=config.COLOR_CARD_BG,
            fg=config.COLOR_TEXT_PRIMARY,
            anchor="w",
        )
        desc.pack(fill=tk.X, pady=(0, 6))

        row = ttk.Frame(frame, style="Card.TFrame")
        row.pack(fill=tk.X, pady=(0, 4))

        self.voice_input_btn = ttk.Button(
            row,
            text="🎤 Start Voice Input",
            style="Primary.TButton",
            command=self._on_voice_input_clicked,
        )
        self.voice_input_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.speak_result_btn = ttk.Button(
            row,
            text="🔊 Speak Result",
            style="Accent.TButton",
            command=self._on_speak_result_clicked,
        )
        self.speak_result_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.voice_status_label = tk.Label(
            row,
            text="Voice status: Ready | Click 'Start Voice Input' to speak",
            font=config.FONT_MUTED,
            bg=config.COLOR_CARD_BG,
            fg=config.COLOR_TEXT_MUTED,
            anchor="w",
        )
        self.voice_status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _build_ask_question_section(self, parent):
        """4. Ask Question & Execute Section"""
        frame = ttk.LabelFrame(parent, text=" 🤖 4. Ask Question & Query Controls ", padding=10)
        frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 10))

        desc = tk.Label(
            frame,
            text="Type a natural language question (or switch to Manual SQL mode):",
            font=config.FONT_BODY,
            bg=config.COLOR_CARD_BG,
            fg=config.COLOR_TEXT_PRIMARY,
            anchor="w",
        )
        desc.pack(fill=tk.X, pady=(0, 6))

        # Question Entry Input
        self.question_var = tk.StringVar()
        self.question_entry = ttk.Entry(
            frame,
            textvariable=self.question_var,
            font=config.FONT_BODY,
        )
        self.question_entry.pack(fill=tk.X, pady=(0, 6))
        self.question_entry.insert(0, "e.g. Show employees whose age is greater than 30")

        # Action Buttons Row
        btn_row = ttk.Frame(frame, style="Card.TFrame")
        btn_row.pack(fill=tk.X)

        gen_btn = ttk.Button(
            btn_row,
            text="🤖 Generate SQL",
            style="Primary.TButton",
            command=self._on_generate_sql_clicked,
        )
        gen_btn.pack(side=tk.LEFT, padx=(0, 4))

        exec_btn = ttk.Button(
            btn_row,
            text="▶️ Execute Query",
            style="Execute.TButton",
            command=self._on_execute_sql_clicked,
        )
        exec_btn.pack(side=tk.LEFT, padx=(0, 4))

        manual_btn = ttk.Button(
            btn_row,
            text="✍️ Manual SQL",
            style="Accent.TButton",
            command=self._on_toggle_manual_sql,
        )
        manual_btn.pack(side=tk.LEFT, padx=(0, 4))

        clear_btn = ttk.Button(
            btn_row,
            text="🧹 Clear",
            style="Danger.TButton",
            command=self._on_clear_clicked,
        )
        clear_btn.pack(side=tk.RIGHT)

    def _build_results_section(self, parent):
        """5. SQL Preview & Query Results Table Section"""
        frame = ttk.LabelFrame(parent, text=" 📋 5. SQL Preview & Query Results ", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        # Mode Indicator Banner
        top_row = tk.Frame(frame, bg=config.COLOR_CARD_BG)
        top_row.pack(fill=tk.X, pady=(0, 4))

        self.lbl_mode = tk.Label(
            top_row,
            text="Mode: Local AI Generator (Ollama)",
            font=config.FONT_SUBHEADER,
            bg=config.COLOR_CARD_BG,
            fg=config.COLOR_ACCENT,
            anchor="w",
        )
        self.lbl_mode.pack(side=tk.LEFT)

        # SQL Preview Text Widget
        sql_frame = tk.Frame(frame, bg="#F1F2F6", bd=1, relief="solid")
        sql_frame.pack(fill=tk.X, pady=(0, 6))

        self.sql_text = tk.Text(
            sql_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#F1F2F6",
            fg="#2C3E50",
            bd=0,
            padx=6,
            pady=6,
            height=3,
        )
        self.sql_text.pack(fill=tk.BOTH, expand=True)
        self.sql_text.insert(
            tk.END,
            "-- SQL Preview: Type a question and click 'Generate SQL', then click 'Execute Query'.",
        )

        # Results Metric Banner
        self.lbl_res_status = tk.Label(
            frame,
            text="Query Results: Ready (No query executed yet)",
            font=config.FONT_SUBHEADER,
            bg=config.COLOR_CARD_BG,
            fg=config.COLOR_TEXT_MUTED,
            anchor="w",
        )
        self.lbl_res_status.pack(fill=tk.X, pady=(0, 4))

        # Results Table Container (Treeview with Scrollbars)
        res_container = ttk.Frame(frame)
        res_container.pack(fill=tk.BOTH, expand=True)

        self.res_tree = ttk.Treeview(res_container, columns=(), show="headings", height=5)

        res_v_scroll = ttk.Scrollbar(res_container, orient=tk.VERTICAL, command=self.res_tree.yview)
        res_h_scroll = ttk.Scrollbar(res_container, orient=tk.HORIZONTAL, command=self.res_tree.xview)
        self.res_tree.configure(yscrollcommand=res_v_scroll.set, xscrollcommand=res_h_scroll.set)

        self.res_tree.grid(row=0, column=0, sticky="nsew")
        res_v_scroll.grid(row=0, column=1, sticky="ns")
        res_h_scroll.grid(row=1, column=0, sticky="ew")

        res_container.columnconfigure(0, weight=1)
        res_container.rowconfigure(0, weight=1)

    def _create_footer(self):
        """Creates the footer bar containing status text and the Exit button."""
        footer_frame = tk.Frame(self, bg="#EAECEE", height=45, padx=15, pady=8)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Status Message Label on the left
        self.status_label = tk.Label(
            footer_frame,
            text="System Ready | Use voice or text input to query your dataset",
            font=config.FONT_BODY,
            bg="#EAECEE",
            fg=config.COLOR_TEXT_PRIMARY,
            anchor="w",
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Exit Button on the right
        exit_btn = ttk.Button(
            footer_frame,
            text="🚪 Exit Application",
            style="Danger.TButton",
            command=self._on_exit_clicked,
        )
        exit_btn.pack(side=tk.RIGHT)

    # ------------------------------------------------------------------
    # Event Handlers & Voice Pipeline
    # ------------------------------------------------------------------

    def _on_browse_clicked(self):
        """Open desktop file picker for dataset selection."""
        filepath = filedialog.askopenfilename(
            title="Select Dataset File",
            filetypes=[
                ("All Supported Datasets", "*.csv;*.xlsx;*.xls"),
                ("CSV Files (*.csv)", "*.csv"),
                ("Excel Files (*.xlsx, *.xls)", "*.xlsx;*.xls"),
                ("All Files", "*.*"),
            ],
        )
        if filepath:
            self.file_path_var.set(filepath)
            self._update_status(f"File selected: {os.path.basename(filepath)}")

    def _on_upload_clicked(self):
        """Uploads dataset file and builds SQLite database table."""
        filepath = self.file_path_var.get()
        if not filepath or filepath == "No file selected...":
            messagebox.showwarning(
                "No File Selected",
                "Please click 'Browse...' to select a CSV or Excel file first.",
            )
            return

        success, load_msg = self.dataset_handler.load_dataset(filepath)
        if not success:
            messagebox.showerror("Dataset Load Error", load_msg)
            self._update_status(f"Error: {load_msg.splitlines()[0]}")
            self._reset_info_display()
            return

        df = self.dataset_handler.get_dataframe()
        db_success, db_msg, schema = self.db_handler.import_dataframe(df, table_name="dataset")
        if not db_success:
            messagebox.showerror("SQLite Integration Error", db_msg)
            self._update_status(f"Database Error: {db_msg.splitlines()[0]}")
            self._reset_info_display()
            return

        meta = self.dataset_handler.get_dataset_info()
        self._update_metadata_and_schema_display(meta, schema)
        self._populate_preview_table()

        self._update_status(f"Dataset '{meta['filename']}' imported into SQLite ('data/app.db' | Table: 'dataset').")
        messagebox.showinfo("Success - SQLite Database Ready", f"{load_msg}\n\n{db_msg}")

    def _on_voice_input_clicked(self):
        """Starts microphone audio listening in a background thread to prevent GUI freezing."""
        self.voice_status_label.config(
            text="Voice status: 🔴 Listening... Speak into microphone now",
            fg=config.COLOR_WARNING,
        )
        self.voice_input_btn.config(state="disabled")
        self._update_status("Listening for voice input...")

        # Run speech recognition in a daemon background thread
        thread = threading.Thread(target=self._voice_listen_worker, daemon=True)
        thread.start()

    def _voice_listen_worker(self):
        """Worker thread for recording and recognizing speech audio."""
        success, recognized_text, status_msg = self.voice_handler.listen_and_recognize()

        # Update GUI on main thread
        self.after(0, self._handle_voice_result, success, recognized_text, status_msg)

    def _handle_voice_result(self, success: bool, text: str, status_msg: str):
        """Main thread callback to process speech recognition results."""
        self.voice_input_btn.config(state="normal")

        if success and text:
            # Auto-populate recognized text into Section 4 Question Box!
            self.question_var.set(text)
            self.voice_status_label.config(
                text=f"Voice status: ✅ Recognized: '{text}'",
                fg=config.COLOR_SUCCESS,
            )
            self._update_status(f"Voice recognized: '{text}'. Click 'Generate SQL' to proceed.")
            messagebox.showinfo(
                "Voice Input Recognized",
                f"Recognized Spoken Question:\n\"{text}\"\n\nQuestion has been filled into the Question Box. Click 'Generate SQL' to generate query.",
            )
        else:
            self.voice_status_label.config(
                text=f"Voice status: ⚠️ {status_msg}",
                fg=config.COLOR_DANGER,
            )
            self._update_status(f"Voice Notice: {status_msg}")
            messagebox.showwarning("Voice Notice", f"{status_msg}\n\nText-based querying remains fully functional.")

    def _on_speak_result_clicked(self):
        """Speaks a concise audio summary of the current query execution results."""
        if not self.latest_query_result:
            messagebox.showwarning("No Results to Speak", "Please execute a SQL query first to generate results.")
            return

        spoken_summary = self.voice_handler.speak_query_result(self.latest_query_result)
        self.voice_status_label.config(
            text=f"Voice status: 🔊 Speaking: '{spoken_summary}'",
            fg=config.COLOR_ACCENT,
        )
        self._update_status(f"Audio summary: '{spoken_summary}'")

    def _on_generate_sql_clicked(self):
        """Generates SQL from user question using NLToSQLConverter."""
        question = self.question_var.get().strip()
        if not question:
            messagebox.showwarning("Empty Question", "Please enter a question first.")
            return

        if not self.db_handler.is_ready():
            messagebox.showwarning(
                "Database Not Ready",
                "Please upload a dataset file first to build the SQLite database.",
            )
            return

        schema = self.db_handler.get_schema()

        # Call QueryEngine to generate SQL
        res = self.query_engine.process_question(question, schema)
        sql_output = res["sql"]
        status_msg = res["message"]

        # Display generated SQL in preview box
        self.sql_text.delete("1.0", tk.END)
        self.sql_text.insert(tk.END, sql_output)

        self.lbl_mode.config(text=f"Mode: Local AI Generator ({status_msg})", fg=config.COLOR_ACCENT)
        self._update_status(f"SQL Generation: {status_msg}")

        if not res["success"]:
            messagebox.showinfo("AI Service Notice", status_msg)

    def _on_execute_sql_clicked(self):
        """Executes SQL query currently in SQL Preview box against SQLite database."""
        sql_query = self.sql_text.get("1.0", tk.END).strip()
        if not sql_query or sql_query.startswith("-- SQL Preview"):
            messagebox.showwarning("Empty SQL", "Please generate or type a SQL query to execute first.")
            return

        if not self.db_handler.is_ready():
            messagebox.showwarning("Database Not Ready", "Please upload a dataset file first.")
            return

        # Execute query via QueryEngine
        res = self.query_engine.execute_sql(sql_query, self.db_handler)
        self.latest_query_result = res

        if not res["success"]:
            messagebox.showerror("Query Execution Error", res["message"])
            self.lbl_res_status.config(text=f"Query Results: ❌ Execution Error ({res['error']})", fg=config.COLOR_DANGER)
            self._update_status(f"Execution Error: {res['error']}")
            self._clear_results_table()
            return

        # Success - populate query results Treeview table
        self._populate_results_table(res["columns"], res["rows"])
        self.lbl_res_status.config(
            text=f"Query Results: ✅ Returned {res['row_count']} row(s) and {res['column_count']} column(s)",
            fg=config.COLOR_SUCCESS,
        )
        self._update_status(f"Query Executed Successfully ({res['row_count']} rows returned). Click 'Speak Result' to listen.")

    def _populate_results_table(self, columns: list, rows: list):
        """Populates the Query Results Treeview table."""
        self.res_tree.delete(*self.res_tree.get_children())
        self.res_tree["columns"] = ()

        if not columns:
            return

        self.res_tree["columns"] = columns
        for col in columns:
            self.res_tree.heading(col, text=col, anchor="w")
            self.res_tree.column(col, width=120, minwidth=80, stretch=True)

        for row_idx, row_values in enumerate(rows):
            tag = "evenrow" if row_idx % 2 == 0 else "oddrow"
            self.res_tree.insert("", tk.END, values=row_values, tags=(tag,))

        self.res_tree.tag_configure("evenrow", background="#FFFFFF")
        self.res_tree.tag_configure("oddrow", background="#F8F9FA")

    def _clear_results_table(self):
        """Clears the Query Results Treeview table."""
        self.res_tree.delete(*self.res_tree.get_children())
        self.res_tree["columns"] = ()

    def _on_toggle_manual_sql(self):
        """Switches UI to Manual SQL mode where user can type SQL directly."""
        self.manual_sql_mode = True
        self.lbl_mode.config(text="Mode: ✍️ Manual SQL Entry (User Input)", fg=config.COLOR_WARNING)
        self.sql_text.config(bg="#FFFFFF")
        self.sql_text.focus_set()
        self._update_status("Switched to Manual SQL Entry Mode.")
        messagebox.showinfo(
            "Manual SQL Mode",
            "You can now type or edit SQL queries directly in the SQL Preview box below.",
        )

    def _on_clear_clicked(self):
        """Clears user question, SQL preview text box, and query results table."""
        self.question_var.set("")
        self.sql_text.delete("1.0", tk.END)
        self.sql_text.insert(
            tk.END,
            "-- SQL preview cleared.\n"
            "-- Type a question above and click 'Generate SQL (Local AI)'.",
        )
        self._clear_results_table()
        self.latest_query_result = None
        self.lbl_res_status.config(text="Query Results: Ready (No query executed yet)", fg=config.COLOR_TEXT_MUTED)
        self.voice_status_label.config(text="Voice status: Ready | Click 'Start Voice Input' to speak", fg=config.COLOR_TEXT_MUTED)
        self._update_status("Cleared question, SQL preview, and query results.")

    def _update_metadata_and_schema_display(self, meta: dict, schema):
        """Populates the dataset information label panel and detected SQLite schema."""
        self.lbl_status.config(text=f"Status: ✅ Loaded Successfully ({meta['filename']})", fg=config.COLOR_SUCCESS)
        self.lbl_db_status.config(
            text="SQLite DB Status: ✅ Database Ready (data/app.db | Table: 'dataset')",
            fg=config.COLOR_SUCCESS,
        )
        self.lbl_details.config(
            text=f"File: {meta['filename']}  |  Rows: {schema.row_count if schema else meta['row_count']}  |  Columns: {schema.column_count if schema else meta['column_count']}"
        )

        if schema and schema.columns:
            types_list = [f"{col.clean_name}: {col.sqlite_type}" for col in schema.columns]
            schema_str = ", ".join(types_list)
            if len(schema_str) > 130:
                schema_str = schema_str[:127] + "..."
            self.lbl_schema.config(text=f"Detected SQLite Schema: {schema_str}")
        else:
            self.lbl_schema.config(text="Detected SQLite Schema: None")

    def _populate_preview_table(self):
        """Populates the Tkinter Treeview widget with dataset preview rows."""
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ()

        columns, rows = self.dataset_handler.get_preview_table(max_rows=15)
        if not columns:
            return

        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(col, width=120, minwidth=80, stretch=True)

        for row_idx, row_values in enumerate(rows):
            tag = "evenrow" if row_idx % 2 == 0 else "oddrow"
            self.tree.insert("", tk.END, values=row_values, tags=(tag,))

        self.tree.tag_configure("evenrow", background="#FFFFFF")
        self.tree.tag_configure("oddrow", background="#F8F9FA")

    def _reset_info_display(self):
        """Resets metadata panel and clears preview table."""
        self.lbl_status.config(text="Status: No dataset loaded", fg=config.COLOR_TEXT_MUTED)
        self.lbl_db_status.config(text="SQLite DB Status: Database Inactive (data/app.db)", fg=config.COLOR_TEXT_MUTED)
        self.lbl_details.config(text="File: N/A  |  Rows: 0  |  Columns: 0")
        self.lbl_schema.config(text="Detected SQLite Schema: None")

        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ()
        self._clear_results_table()

    def _on_exit_clicked(self):
        """Cleanly exits the application."""
        if messagebox.askyesno("Exit Application", "Are you sure you want to close the application?"):
            self.destroy()

    def _update_status(self, message: str):
        """Helper function to update status bar message."""
        self.status_label.config(text=message)


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
