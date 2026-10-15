"""Tkinter front end for the AI-Based Computer Troubleshooting System."""

from __future__ import annotations

import json
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk

from expert_system import InferenceEngine, PROBLEMS, QUESTIONS


APP_DIR = Path(__file__).resolve().parent
HISTORY_FILE = APP_DIR / "troubleshooting_history.json"


class TroubleshootingApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("AI-Based Computer Troubleshooting System")
        self.geometry("900x680")
        self.minsize(780, 580)
        self.configure(bg="#eef3f8")

        self.engine = InferenceEngine()
        self.problem_key = tk.StringVar(value=list(PROBLEMS)[0])
        self.question_index = 0
        self.facts = {}
        self.current_diagnoses = []

        self._build_ui()
        self.start_session()

    def _build_ui(self) -> None:
        header = tk.Frame(self, bg="#143a5a", padx=24, pady=16)
        header.pack(fill="x")
        tk.Label(header, text="AI-Based Computer Troubleshooting System",
                 font=("Segoe UI", 19, "bold"), bg="#143a5a", fg="white").pack(anchor="w")
        tk.Label(header, text="Rule-based expert system using forward and backward chaining",
                 font=("Segoe UI", 10), bg="#143a5a", fg="#d7e9f7").pack(anchor="w", pady=(4, 0))

        body = tk.Frame(self, bg="#eef3f8", padx=24, pady=18)
        body.pack(fill="both", expand=True)

        select = tk.Frame(body, bg="#eef3f8")
        select.pack(fill="x")
        tk.Label(select, text="Choose a problem:", font=("Segoe UI", 11, "bold"),
                 bg="#eef3f8", fg="#1d3345").pack(side="left")
        self.problem_box = ttk.Combobox(select, state="readonly", width=42,
                                        values=list(PROBLEMS.values()))
        self.problem_box.current(0)
        self.problem_box.pack(side="left", padx=10)
        self.problem_box.bind("<<ComboboxSelected>>", self._on_problem_change)

        self.progress = ttk.Progressbar(body, mode="determinate")
        self.progress.pack(fill="x", pady=(18, 10))
        self.progress_label = tk.Label(body, bg="#eef3f8", fg="#557080", font=("Segoe UI", 9))
        self.progress_label.pack(anchor="e")

        card = tk.Frame(body, bg="white", padx=28, pady=28, highlightbackground="#c9d9e5", highlightthickness=1)
        card.pack(fill="x", pady=(12, 16))
        self.question_label = tk.Label(card, text="", justify="left", wraplength=760,
                                       font=("Segoe UI", 15, "bold"), bg="white", fg="#1a3448")
        self.question_label.pack(anchor="w", pady=(0, 24))
        buttons = tk.Frame(card, bg="white")
        buttons.pack(anchor="w")
        self.yes_button = ttk.Button(buttons, text="Yes", command=lambda: self.answer(True), width=16)
        self.yes_button.pack(side="left", padx=(0, 10))
        self.no_button = ttk.Button(buttons, text="No", command=lambda: self.answer(False), width=16)
        self.no_button.pack(side="left", padx=(0, 10))
        self.unknown_button = ttk.Button(buttons, text="Not sure", command=lambda: self.answer(None), width=16)
        self.unknown_button.pack(side="left")

        result_frame = tk.LabelFrame(body, text=" Diagnosis and explanation ", bg="#eef3f8", fg="#143a5a",
                                     font=("Segoe UI", 11, "bold"), padx=12, pady=10)
        result_frame.pack(fill="both", expand=True)
        self.result_text = tk.Text(result_frame, height=13, wrap="word", font=("Segoe UI", 10),
                                   bg="white", fg="#1d3345", relief="flat", padx=12, pady=10)
        self.result_text.pack(fill="both", expand=True)
        self.result_text.configure(state="disabled")

        footer = tk.Frame(body, bg="#eef3f8")
        footer.pack(fill="x", pady=(12, 0))
        ttk.Button(footer, text="Start Again", command=self.start_session).pack(side="left")
        ttk.Button(footer, text="View History", command=self.show_history).pack(side="right")

    def _on_problem_change(self, _event=None) -> None:
        self.problem_key.set(list(PROBLEMS)[self.problem_box.current()])
        self.start_session()

    def start_session(self) -> None:
        self.question_index = 0
        self.facts = {}
        self.current_diagnoses = []
        self._set_result("Answer the questions below. The inference engine will use the facts you provide to fire IF-THEN rules.")
        self._show_question()

    def _show_question(self) -> None:
        questions = QUESTIONS[self.problem_key.get()]
        if self.question_index >= len(questions):
            self._finish_diagnosis()
            return
        question = questions[self.question_index]
        self.question_label.configure(text=question.text)
        self.progress["maximum"] = len(questions)
        self.progress["value"] = self.question_index
        self.progress_label.configure(text=f"Question {self.question_index + 1} of {len(questions)}")
        for button in (self.yes_button, self.no_button, self.unknown_button):
            button.configure(state="normal")

    def answer(self, value) -> None:
        question = QUESTIONS[self.problem_key.get()][self.question_index]
        self.facts[question.fact] = value  # Working memory: facts provided by the user.
        self.question_index += 1
        self._show_question()

    def _finish_diagnosis(self) -> None:
        for button in (self.yes_button, self.no_button, self.unknown_button):
            button.configure(state="disabled")
        questions = QUESTIONS[self.problem_key.get()]
        self.progress["value"] = len(questions)
        self.progress_label.configure(text="Interview complete")
        self.question_label.configure(text="Diagnosis complete — see the expert system's reasoning below.")
        self.current_diagnoses = self.engine.forward_chain(self.facts)

        if not self.current_diagnoses:
            likely = self.engine.likely_rules(self.facts)
            text = "No rule was fully satisfied. Try answering all questions with confirmed information.\n\n"
            if likely:
                text += "Partially supported possibilities:\n" + "\n".join(
                    f"• {rule.fault} — needs more evidence for rule {rule.rule_id}" for rule in likely
                )
            else:
                text += "The current knowledge base has no matching rule for these answers."
        else:
            lines = ["Forward-chaining result (rules fired from your symptoms):\n"]
            for number, diagnosis in enumerate(self.current_diagnoses, 1):
                rule_ids = ", ".join(rule.rule_id for rule in diagnosis.fired_rules)
                lines.extend([
                    f"{number}. Possible fault: {diagnosis.fault}  [{diagnosis.confidence}% confidence]",
                    f"   Suggested action: {diagnosis.solution}",
                    f"   Why: {diagnosis.explanation}",
                    f"   Rules fired: {rule_ids}",
                    "   " + self.engine.verify_backward(diagnosis, self.facts).replace("\n", "\n   "),
                    "",
                ])
            text = "\n".join(lines)
        self._set_result(text)
        self._save_history()

    def _set_result(self, text: str) -> None:
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", text)
        self.result_text.configure(state="disabled")

    def _save_history(self) -> None:
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "problem": PROBLEMS[self.problem_key.get()],
            "diagnoses": [item.fault for item in self.current_diagnoses] or ["No conclusive diagnosis"],
        }
        try:
            old_data = json.loads(HISTORY_FILE.read_text(encoding="utf-8")) if HISTORY_FILE.exists() else []
            old_data.append(entry)
            HISTORY_FILE.write_text(json.dumps(old_data[-50:], indent=2), encoding="utf-8")
        except OSError:
            # The expert system still works if the folder is read-only.
            pass

    def show_history(self) -> None:
        try:
            entries = json.loads(HISTORY_FILE.read_text(encoding="utf-8")) if HISTORY_FILE.exists() else []
        except (OSError, json.JSONDecodeError):
            entries = []
        message = "No troubleshooting sessions have been saved yet." if not entries else "\n\n".join(
            f"{entry['date']} — {entry['problem']}\nDiagnosis: {', '.join(entry['diagnoses'])}"
            for entry in reversed(entries)
        )
        messagebox.showinfo("Troubleshooting History", message)


if __name__ == "__main__":
    TroubleshootingApp().mainloop()
