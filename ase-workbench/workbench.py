"""Desktop entry point for the Advanced Software Engineering workbench."""

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from engine import BASELINE, CHECKS, FULL_RUN, Workspace
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

        toolbar = ttk.Frame(window, padding=(15, 10))
        toolbar.pack(fill="x")
        self.controls = []
        self.button(toolbar, "Open workspace", self.open_workspace)
        self.button(toolbar, "Scaffold project", self.scaffold)
        self.button(toolbar, "Install project tools", lambda: self.run(("setup",)))
        self.button(toolbar, "Run baseline", lambda: self.run(BASELINE))
        self.button(toolbar, "Run full local pipeline", lambda: self.run(FULL_RUN, collect_all=True))
        self.button(toolbar, "Export evidence", self.export_report)
        self.button(toolbar, "Stop stacks", lambda: self.run(("down",)))
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
        ttk.Label(right, text="Run log").pack(anchor="w")
        self.log = self.text_box(right, 10, scrollable=True)
        self.log.configure(state="disabled", background="#101827", foreground="#e2e8f0")
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

    def open_workspace(self):
        directory = filedialog.askdirectory(parent=self.window, title="Open a trusted ASE project folder")
        if not directory:
            return
        try:
            self.save_notes(quiet=True)
            self.workspace = Workspace(directory)
            self.location.set(str(self.workspace.root))
            self.refresh()
            self.show_stage()
            self.append(f"Opened {directory}")
        except (ValueError, OSError) as error:
            self.error(error)

    def scaffold(self):
        if not self.require_workspace():
            return
        try:
            created, kept = self.workspace.scaffold()
            self.append("Created: " + (", ".join(created) or "none"))
            self.append("Existing files retained: " + (", ".join(kept) or "none"))
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
        if self.active == "delivery":
            self.candidate_button.pack(side="left")
        else:
            self.candidate_button.pack_forget()
        self.update_check_list()

    def update_check_list(self):
        checks = STAGES[self.active].checks
        self.checks.set("\n".join(f"{CHECKS[key]}  ·  "
                                  f"{self.workspace.result(key) if self.workspace else 'Pending'}"
                                  for key in checks) or "This stage is reviewed from notes and evidence.")

    def save_notes(self, quiet=False):
        if not self.workspace:
            return quiet or self.require_workspace()
        value = self.notes.get("1.0", "end-1c")
        previous = self.workspace.data["notes"].get(self.active, "")
        if value == previous:
            return True
        try:
            self.workspace.data["notes"][self.active] = value
            self.workspace.data["reviews"].pop(self.active, None)
            self.workspace.save()
            self.refresh()
            if not quiet:
                self.activity.set("Stage notes saved")
            return True
        except OSError as error:
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
        for key, stage in STAGES.items():
            self.tree.item(key, values=(stage.title, self.workspace.status(key) if self.workspace else "Pending"))
        self.update_check_list()

    def run(self, checks, collect_all=False):
        if not self.require_workspace() or not checks or not self.save_notes(quiet=True):
            return
        if not (self.workspace.root / "compose.json").is_file():
            self.error("Scaffold the project first.")
            return
        self.busy = True
        for control in self.controls:
            control.configure(state="disabled")
        self.notes.configure(state="disabled")
        self.activity.set("Running checks…")
        threading.Thread(target=self.worker, args=(self.workspace, checks, collect_all), daemon=True).start()

    def worker(self, workspace, checks, collect_all):
        try:
            summary = []
            for key in checks:
                self.messages.put(("line", f"▶ {CHECKS[key]}"))
                status, output = workspace.run(key)
                self.messages.put(("line", f"{status}\n{output}"))
                summary.append(status)
                if status != "Passed" and not collect_all:
                    break
            self.messages.put(("done", f"Checks passed: {summary.count('Passed')}/{len(checks)}"))
        except Exception as error:
            self.messages.put(("done", f"Run interrupted: {error}"))

    def poll(self):
        try:
            while True:
                kind, value = self.messages.get_nowait()
                self.append(value)
                if kind == "done":
                    self.busy = False
                    for control in self.controls:
                        control.configure(state="normal")
                    self.notes.configure(state="normal")
                    self.activity.set(value)
                    self.refresh()
        except queue.Empty:
            pass
        self.window.after(100, self.poll)

    def append(self, value):
        self.log.configure(state="normal")
        self.log.insert("end", value[-20000:] + "\n\n")
        self.log.see("end")
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
            messagebox.showinfo("Checks are running", "Wait for the current run to finish.", parent=self.window)
        elif self.save_notes(quiet=True):
            self.window.destroy()


def main():
    window = tk.Tk()
    Workbench(window)
    window.mainloop()


if __name__ == "__main__":
    main()
