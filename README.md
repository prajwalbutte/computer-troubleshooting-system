# AI-Based Computer Troubleshooting and Fault Diagnosis System

A Python mini-project that demonstrates an **AI rule-based expert system** for common computer faults. It uses a Tkinter graphical interface and needs no external libraries or dataset.

## AI concepts demonstrated

- **Knowledge base:** questions and IF-THEN rules are kept separately in `expert_system.py`.
- **Working memory:** the user's Yes/No/Not sure answers are stored as facts during one diagnosis session.
- **Forward chaining:** every rule whose conditions match the known facts is fired to derive possible diagnoses.
- **Backward chaining:** the selected conclusion is verified by showing every condition that led to its rule firing.
- **Inference engine:** `InferenceEngine` evaluates the knowledge base and ranks conclusions by rule priority.

## Included troubleshooting areas

1. Computer will not turn on
2. Computer is very slow
3. Wi-Fi / internet is not working
4. Printer is not printing
5. No sound or audio problem
6. Display / monitor problem

## Project files

| File | Purpose |
|---|---|
| `main.py` | Tkinter GUI, question flow, and local history |
| `expert_system.py` | Knowledge base, production rules, forward/backward inference engine |
| `troubleshooting_history.json` | Created automatically after a completed session |

## How to run

1. Install Python 3.10 or later.
2. Open a terminal in this project folder.
3. Run:

```powershell
python main.py
```

No `pip install` step is required because Tkinter and JSON are part of Python's standard library.

## Example rule

```text
IF charger_connected = True
AND power_indicator_on = False
THEN possible_fault = "Power adapter or power supply fault"
```

## Suggested mini-project demonstration

Choose **Computer will not turn on**, answer **Yes** to charger connected and **No** to the power indicator, then complete the remaining questions. The system will fire rule `P02`, suggest checking the adapter/cable/port, and display the forward- and backward-chaining explanation.

## Important note

The diagnoses are educational first-level troubleshooting suggestions, not a substitute for a trained hardware technician. Do not open power supplies or laptop batteries yourself.
