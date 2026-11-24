"""Desktop entry point for the Advanced Software Engineering workbench."""

import queue
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from engine import CHECKS, PROFILES, Workspace
from execution import RunCancelled
from scaffold import DEFAULT_PORT, DEFAULT_TLS_PORT, valid_port
from stages import NOTE_TEMPLATES, STAGES

BG = "#f1f5f9"
INK = "#0f172a"
MUTED = "#475569"


class Workbench:
    def __init__(self, window):
        self.window = window
        self.workspace = None
        self.active = "vision"
        self.messages = queue.Queue()
        self.busy = False
        self.cancel = None
        self.close_after_run = False

        window.title("ASE Workflow Workbench")
        window.geometry("1240x820")
        window.minsize(960, 640)
        window.configure(background=BG)
        window.protocol("WM_DELETE_WINDOW", self.close)
        style = ttk.Style(window)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=INK)
        style.configure("TButton", padding=(9, 6))
        style.configure("Treeview", rowheight=30, background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=("TkDefaultFont", 10, "bold"), padding=6)
        style.map("Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", INK)])

        header = tk.Frame(window, background=INK, padx=22, pady=15)
        header.pack(fill="x")
        tk.Label(header, text="ASE Workflow Workbench", bg=INK, fg="white",
                 font=("TkDefaultFont", 21, "bold")).pack(anchor="w")
        self.location = tk.StringVar(value="Choose a project folder to start.")
        tk.Label(header, textvariable=self.location, bg=INK, fg="#cbd5e1",
                 anchor="w", justify="left").pack(anchor="w")

        toolbar = ttk.Frame(window, padding=(15, 8))
        toolbar.pack(fill="x")
        self.controls = []
        self.button(toolbar, "Open workspace", self.open_workspace)
        self.button(toolbar, "Scaffold project", self.scaffold)
        self.button(toolbar, "Check tools", self.check_tools)
        self.button(toolbar, "Install project tools", lambda: self.run(("setup",)))
        self.button(toolbar, "Export evidence", self.export_report)

        runbar = ttk.Frame(window, padding=(15, 0, 15, 8))
        runbar.pack(fill="x")
        for profile, label in (("quick", "Quick checks"), ("baseline", "Run baseline"),
                               ("full", "Run full pipeline")):
            self.button(runbar, label, lambda profile=profile: self.run(PROFILES[profile]))
        self.button(runbar, "Stop stacks", lambda: self.run(("down",)))
        self.cancel_button = ttk.Button(runbar, text="Cancel run", state="disabled", command=self.cancel_run)
        self.cancel_button.pack(side="right")
        self.activity = tk.StringVar(value="Ready")
        ttk.Label(window, textvariable=self.activity, padding=(18, 4), anchor="w").pack(fill="x", side="bottom")

        body = ttk.Panedwindow(window, orient="horizontal")
        body.pack(fill="both", expand=True, padx=15, pady=(0, 8))
        left = ttk.Frame(body)
        right = ttk.Frame(body, padding=(12, 0))
        body.add(left, weight=2)
        body.add(right, weight=4)

        self.tree = ttk.Treeview(left, columns=("stage", "state"), show="headings", selectmode="browse")
        self.tree.heading("stage", text="Workflow stage")
        self.tree.heading("state", text="Status")
        self.tree.column("stage", width=390, minwidth=300)
        self.tree.column("state", width=106, minwidth=85, stretch=False, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(left, command=self.tree.yview)
        scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll.set)
        for key, stage in STAGES.items():
            self.tree.tag_configure(key, foreground=stage.color)
            self.tree.insert("", "end", key, values=(stage.title, "Pending"), tags=(key,))
        self.tree.bind("<<TreeviewSelect>>", self.select)

        self.heading = tk.Label(right, anchor="w", justify="left", background=BG,
                                font=("TkDefaultFont", 16, "bold"))
        self.heading.pack(fill="x")
        self.details = tk.Label(right, anchor="w", justify="left", background=BG, foreground=MUTED, pady=8)
        self.details.pack(fill="x")
        self.details.bind("<Configure>", self.wrap_details)
        self.heading.bind("<Configure>", self.wrap_details)

        ttk.Label(right, text="Stage notes and evidence").pack(anchor="w")
        self.notes = self.text_box(right, 6, scrollable=False)
        actions = ttk.Frame(right)
        actions.pack(fill="x", pady=6)
        self.button(actions, "Save notes", self.save_notes)
        self.button(actions, "Insert prompts", self.insert_prompts)
        self.button(actions, "Mark reviewed", self.review)
        self.button(actions, "Run stage checks", lambda: self.run(STAGES[self.active].checks))
        self.candidate_button = self.button(actions, "Record candidate", self.candidate)
        self.checks = tk.StringVar()
        ttk.Label(right, textvariable=self.checks, justify="left").pack(anchor="w", pady=(0, 8))
        self.output_tabs = ttk.Notebook(right)
        self.output_tabs.pack(fill="both", expand=True)
        self.live_tab = ttk.Frame(self.output_tabs, padding=4)
        self.output_tabs.add(self.live_tab, text="Run log")
        self.log = self.text_box(self.live_tab, 9, scrollable=True)
        self.log.configure(state="disabled", background="#101827", foreground="#e2e8f0")
        self.create_history()
        self.tree.selection_set("vision")
        self.show_stage()
        window.after(100, self.poll)

    def button(self, parent, label, command):
        button = ttk.Button(parent, text=label, command=command)
        button.pack(side="left", padx=(0, 5))
        self.controls.append(button)
        return button

    @staticmethod
    def text_box(parent, height, scrollable):
        box = ttk.Frame(parent)
        box.pack(fill="both" if scrollable else "x", expand=scrollable, pady=(3, 2))
        widget = tk.Text(box, height=height, wrap="word", relief="flat", padx=8, pady=6, undo=not scrollable)
        widget.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(box, command=widget.yview)
        scrollbar.pack(side="right", fill="y")
        widget.configure(yscrollcommand=scrollbar.set)
        return widget

    def wrap_details(self, event):
        event.widget.configure(wraplength=max(300, event.width - 10))

    def require_workspace(self):
        if self.workspace:
            return True
        messagebox.showinfo("Open a workspace", "Choose a project folder first.", parent=self.window)
        return False

    def show_location(self):
        try:
            endpoints = f"  ·  HTTP {self.workspace.port()}  ·  HTTPS {self.workspace.port(secure=True)}"
        except (OSError, ValueError):
            endpoints = ""
        self.location.set(str(self.workspace.root) + endpoints)

    def open_workspace(self):
        directory = filedialog.askdirectory(parent=self.window, title="Open a trusted ASE project folder")
        if not directory:
            return
        try:
            if not self.save_notes(quiet=True):
                return
            self.workspace = Workspace(directory)
            self.show_location()
            self.clear_log()
            self.refresh()
            self.show_stage()
            self.append(f"Opened {directory}")
        except (ValueError, OSError) as error:
            self.error(error)

    def scaffold(self):
        if not self.require_workspace():
            return
        try:
            paths = ("compose.json", "compose.secure.json")
            if any((self.workspace.root / path).exists() for path in paths):
                created, kept = self.workspace.scaffold()
            else:
                dialog = PortsDialog(self.window, title="Gateway ports")
                if dialog.result is None:
                    return
                created, kept = self.workspace.scaffold(*dialog.result)
            self.append("Created: " + (", ".join(created) or "none"))
            self.append("Existing files retained: " + (", ".join(kept) or "none"))
            self.show_location()
            self.refresh()
        except (OSError, ValueError) as error:
            self.error(error)

    def select(self, _event):
        selected = self.tree.selection()
        if not selected or selected[0] == self.active:
            return
        if self.busy:
            self.tree.selection_set(self.active)
            return
        if self.save_notes(quiet=True):
            self.active = selected[0]
            self.show_stage()
        else:
            self.tree.selection_set(self.active)

    def show_stage(self):
        stage = STAGES[self.active]
        self.heading.configure(text=stage.title, foreground=stage.color)
        self.details.configure(text=f"{stage.tools}\n\n{stage.action}\n\nExpected output  •  {stage.output}")
        self.notes.delete("1.0", "end")
        if self.workspace:
            self.notes.insert("1.0", self.workspace.data["notes"].get(self.active, ""))
        self.notes.edit_reset()
        if self.active == "delivery":
            self.candidate_button.pack(side="left")
        else:
            self.candidate_button.pack_forget()
        self.update_check_list()

    def update_check_list(self, revision=None):
        checks = STAGES[self.active].checks
        self.checks.set("\n".join(f"{CHECKS[key]}  ·  "
                                  f"{self.workspace.result(key, revision) if self.workspace else 'Pending'}"
                                  for key in checks) or "This stage is reviewed from notes and evidence.")

    def save_notes(self, quiet=False):
        if not self.workspace:
            return quiet or self.require_workspace()
        value = self.notes.get("1.0", "end-1c")
        previous = self.workspace.data["notes"].get(self.active, "")
        if value == previous:
            return True
        try:
            self.workspace.set_note(self.active, value)
            self.refresh()
            if not quiet:
                self.activity.set("Stage notes saved")
            return True
        except (OSError, ValueError) as error:
            self.error(error)
            return False

    def insert_prompts(self):
        if not self.require_workspace():
            return
        prompts = NOTE_TEMPLATES.get(self.active, ("Decision", "Evidence", "Follow-up"))
        current = self.notes.get("1.0", "end-1c")
        self.notes.insert("end", ("\n\n" if current.strip() else "")
                          + "\n\n".join(f"{prompt}\n" for prompt in prompts))
        self.notes.focus_set()

    def review(self):
        if self.require_workspace() and self.save_notes():
            try:
                self.workspace.review(self.active)
                self.refresh()
            except (ValueError, OSError) as error:
                self.error(error)

    def candidate(self):
        if self.require_workspace() and self.save_notes(quiet=True):
            try:
                output = self.workspace.release_candidate()
                self.append(f"Release evidence recorded in {output}")
            except (ValueError, OSError) as error:
                self.error(error)

    def refresh(self):
        revision = self.workspace.fingerprint() if self.workspace else None
        for key, stage in STAGES.items():
            self.tree.item(key, values=(stage.title, self.workspace.status(key, revision) if self.workspace else "Pending"))
        self.update_check_list(revision)
        self.refresh_history()

    def create_history(self):
        tab = ttk.Frame(self.output_tabs, padding=4)
        self.output_tabs.add(tab, text="History")
        table = ttk.Frame(tab)
        table.pack(fill="x")
        self.history_tree = ttk.Treeview(table, columns=("when", "check", "status", "time"),
                                         height=5, show="headings", selectmode="browse")
        for key, title, width in (("when", "Time", 112), ("check", "Check", 240),
                                   ("status", "Result", 88), ("time", "Seconds", 60)):
            self.history_tree.heading(key, text=title)
            self.history_tree.column(key, width=width, minwidth=60, stretch=key == "check")
        self.history_tree.pack(side="left", expand=True, fill="x")
        scrollbar = ttk.Scrollbar(table, command=self.history_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        self.history_log = self.text_box(tab, 5, scrollable=True)
        self.history_log.configure(state="disabled")
        self.history_tree.bind("<<TreeviewSelect>>", self.show_history_log)
        self.history_records = {}

    def refresh_history(self):
        selected = self.history_tree.selection()
        self.history_tree.delete(*self.history_tree.get_children())
        self.history_records.clear()
        history = self.workspace.data["history"] if self.workspace else []
        for entry in reversed(history[-200:]):
            when = datetime.fromisoformat(entry["when"]).astimezone().strftime("%d %b %H:%M:%S")
            check = CHECKS.get(entry["check"], entry["check"])
            seconds = entry.get("seconds", "—")
            key = entry["log"]
            if key in self.history_records:
                continue
            self.history_records[key] = entry
            self.history_tree.insert("", "end", iid=key, values=(when, check, entry["status"], seconds))
        if selected and selected[0] in self.history_records:
            self.history_tree.selection_set(selected[0])
        self.show_history_log()

    def show_history_log(self, _event=None):
        selected = self.history_tree.selection()
        entry = self.history_records.get(selected[0]) if selected else None
        preview = "Select a check to read its log."
        if entry:
            try:
                path = (self.workspace.root / entry["log"]).resolve()
                if not path.is_relative_to(self.workspace.state.resolve()):
                    raise ValueError("Log path is outside the workspace evidence folder.")
                with path.open("rb") as handle:
                    size = handle.seek(0, 2)
                    handle.seek(max(0, size - 64_000))
                    content = handle.read(64_000).decode("utf-8", errors="replace")
                header = entry["log"] + "\n"
                if entry.get("artifacts"):
                    header += "Evidence files\n" + "\n".join(entry["artifacts"]) + "\n"
                preview = header + "\n" + ("…\n" if size > 64_000 else "") + content
            except (ValueError, OSError) as error:
                preview = str(error)
        self.history_log.configure(state="normal")
        self.history_log.delete("1.0", "end")
        self.history_log.insert("1.0", preview)
        self.history_log.configure(state="disabled")

    def run(self, checks):
        if not self.require_workspace() or not checks or not self.save_notes(quiet=True):
            return
        if checks != ("down",) and not (self.workspace.root / "compose.json").is_file():
            self.error("Scaffold the project first.")
            return
        self.start_worker(self.run_checks, checks)

    def check_tools(self):
        if self.require_workspace() and self.save_notes(quiet=True):
            self.start_worker(self.run_doctor)

    def start_worker(self, target, *args):
        self.busy = True
        self.cancel = threading.Event()
        for control in self.controls:
            control.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.notes.configure(state="disabled")
        self.activity.set("Running checks…")
        self.output_tabs.select(self.live_tab)
        threading.Thread(target=self.worker, args=(target, self.workspace, self.cancel, *args), daemon=True).start()

    def worker(self, target, workspace, cancel, *args):
        try:
            result = target(workspace, cancel, *args)
        except RunCancelled:
            result = "Run cancelled."
        except Exception as error:
            result = f"Run interrupted: {error}"
        self.messages.put(("done", result))

    def run_checks(self, workspace, cancel, checks):
        def start(key):
            self.messages.put(("started", CHECKS[key]))

        def output(content):
            self.messages.put(("output", content))

        passed = 0
        for key, status, _ in workspace.run_plan(checks, cancel=cancel, output=output, on_start=start):
            self.messages.put(("line", f"{status} · {CHECKS[key]}"))
            passed += status == "Passed"
        result = f"{passed}/{len(checks)} checks passed."
        return f"Run cancelled. {result}" if cancel.is_set() else result

    def run_doctor(self, workspace, cancel):
        ready = []
        for tool, available, detail in workspace.doctor(cancel=cancel):
            label = "Ready" if available else "Unavailable"
            self.messages.put(("line", f"{label} · {tool}\n{detail}"))
            ready.append(available)
        return f"{sum(ready)}/{len(ready)} tool checks ready."

    def cancel_run(self):
        if self.cancel:
            self.cancel.set()
            self.cancel_button.configure(state="disabled")
            self.activity.set("Stopping the active check…")

    def poll(self):
        try:
            for _ in range(150):
                kind, value = self.messages.get_nowait()
                if kind == "started":
                    self.activity.set(value)
                    self.append(f"▶ {value}")
                elif kind == "output":
                    self.append(value, separator="")
                else:
                    self.append(value)
                if kind == "done":
                    self.busy = False
                    for control in self.controls:
                        control.configure(state="normal")
                    self.cancel_button.configure(state="disabled")
                    self.notes.configure(state="normal")
                    self.activity.set(value)
                    self.refresh()
                    if self.close_after_run:
                        self.close()
                        return
        except queue.Empty:
            pass
        self.window.after(100, self.poll)

    def append(self, value, separator="\n\n"):
        self.log.configure(state="normal")
        self.log.insert("end", value + separator)
        line_count = int(self.log.index("end-1c").split(".")[0])
        if line_count > 3000:
            self.log.delete("1.0", f"{line_count - 2500}.0")
        self.log.see("end")
        self.log.configure(state="disabled")

    def clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def export_report(self):
        if self.require_workspace() and self.save_notes(quiet=True):
            destination = filedialog.asksaveasfilename(parent=self.window, defaultextension=".md",
                                                       initialfile="ASE-evidence.md",
                                                       initialdir=self.workspace.state,
                                                       filetypes=[("Markdown", "*.md")])
            if destination:
                try:
                    self.workspace.report(Path(destination))
                    self.activity.set(f"Evidence exported to {destination}")
                except OSError as error:
                    self.error(error)

    def error(self, error):
        messagebox.showerror("ASE Workbench", str(error), parent=self.window)

    def close(self):
        if self.busy:
            if messagebox.askyesno("Checks are running", "Cancel the active check and close?", parent=self.window):
                self.close_after_run = True
                self.cancel_run()
        elif self.save_notes(quiet=True):
            self.window.destroy()


class PortsDialog(simpledialog.Dialog):
    def body(self, frame):
        self.entries = []
        for row, (label, port) in enumerate((("HTTP port", DEFAULT_PORT), ("HTTPS port", DEFAULT_TLS_PORT))):
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", padx=(6, 10), pady=4)
            field = ttk.Entry(frame, width=14)
            field.insert(0, str(port))
            field.grid(row=row, column=1, padx=(0, 6), pady=4)
            self.entries.append(field)
        return self.entries[0]

    def validate(self):
        try:
            http, https = (valid_port(field.get().strip()) for field in self.entries)
            if http == https:
                raise ValueError("HTTP and HTTPS need different host ports.")
            self.result = (http, https)
            return True
        except ValueError as error:
            messagebox.showerror("Gateway ports", str(error), parent=self)
            return False


def main():
    window = tk.Tk()
    Workbench(window)
    window.mainloop()


if __name__ == "__main__":
    main()
