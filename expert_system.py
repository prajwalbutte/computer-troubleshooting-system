"""Knowledge base and inference engine for the troubleshooting expert system.

The module intentionally contains no user-interface code.  This keeps the
knowledge base, working memory, and inference engine separate, as an expert
system should be.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class Question:
    """A yes/no question used to collect one item of evidence."""

    fact: str
    text: str


@dataclass(frozen=True)
class Rule:
    """An IF-THEN production rule in the knowledge base."""

    rule_id: str
    conditions: Dict[str, bool]
    fault: str
    solution: str
    explanation: str
    priority: int = 1


@dataclass
class Diagnosis:
    """A conclusion derived by the inference engine."""

    fault: str
    solution: str
    explanation: str
    fired_rules: List[Rule]
    confidence: int


PROBLEMS = {
    "no_power": "Computer will not turn on",
    "slow": "Computer is very slow",
    "wifi": "Wi-Fi / internet is not working",
    "printer": "Printer is not printing",
    "audio": "No sound or audio problem",
    "display": "Display / monitor problem",
}


QUESTIONS: Dict[str, List[Question]] = {
    "no_power": [
        Question("charger_connected", "Is the charger or power cable connected securely?"),
        Question("power_indicator_on", "Is the power indicator light on?"),
        Question("battery_charged", "Is the battery charged (or does the computer work on AC power)?"),
        Question("fan_starts", "Does the cooling fan start or make a sound?"),
        Question("beep_sound", "Do you hear a startup beep sound?"),
    ],
    "slow": [
        Question("disk_usage_high", "Is disk usage consistently very high (near 100%)?"),
        Question("many_startup_apps", "Are many applications set to start automatically?"),
        Question("low_storage", "Is the main drive nearly full?"),
        Question("malware_symptoms", "Do you see unexpected pop-ups or unknown programs?"),
        Question("overheating", "Does the computer become unusually hot or is the fan constantly loud?"),
    ],
    "wifi": [
        Question("wifi_enabled", "Is Wi-Fi enabled and is Airplane mode turned off?"),
        Question("other_devices_online", "Can other devices use the same Wi-Fi connection?"),
        Question("router_lights_normal", "Are the router/modem power and internet lights normal?"),
        Question("connected_no_internet", "Does it show connected to Wi-Fi but websites still do not open?"),
        Question("network_visible", "Can you see your Wi-Fi network in the available networks list?"),
    ],
    "printer": [
        Question("printer_on", "Is the printer switched on?"),
        Question("paper_loaded", "Is paper loaded correctly in the tray?"),
        Question("ink_or_toner_available", "Is there enough ink or toner?"),
        Question("printer_error_light", "Is an error or warning light showing on the printer?"),
        Question("print_queue_stuck", "Are print jobs stuck in the print queue?"),
    ],
    "audio": [
        Question("volume_up", "Is the system volume turned up?"),
        Question("not_muted", "Is the sound unmuted?"),
        Question("correct_output_selected", "Is the correct speaker/headphone output device selected?"),
        Question("headphones_connected", "Are headphones plugged in?"),
        Question("audio_driver_ok", "Does Device Manager show the audio device without an error?"),
    ],
    "display": [
        Question("monitor_on", "Is the monitor/display powered on?"),
        Question("display_cable_secure", "Is the HDMI/VGA/DisplayPort cable connected securely?"),
        Question("brightness_up", "Is the display brightness turned up?"),
        Question("computer_running", "Does the computer appear to be running (lights/fan active)?"),
        Question("external_display_works", "Does an external display work, if you can test one?"),
    ],
}


RULES: List[Rule] = [
    # Power and startup
    Rule("P01", {"charger_connected": False}, "Power source disconnected",
         "Connect the charger/power cable firmly and try another wall outlet.",
         "The machine has no confirmed source of electrical power.", 3),
    Rule("P02", {"charger_connected": True, "power_indicator_on": False}, "Power adapter or power supply fault",
         "Test with a compatible adapter and inspect the cable, charging port, and wall outlet.",
         "External power is connected, but the system receives no visible power.", 4),
    Rule("P03", {"power_indicator_on": True, "fan_starts": False}, "Internal power or motherboard fault",
         "Disconnect peripherals, hold the power button for 15 seconds, then seek hardware service if it persists.",
         "The indicator has power but internal startup hardware does not begin operating.", 4),
    Rule("P04", {"power_indicator_on": True, "fan_starts": True, "beep_sound": True}, "Memory (RAM) or startup hardware issue",
         "Note the beep pattern; reseat RAM only if you are trained to do so, otherwise contact a technician.",
         "The startup beep suggests the BIOS detected a hardware problem.", 4),
    Rule("P05", {"power_indicator_on": True, "fan_starts": True, "beep_sound": False}, "Display or boot process issue",
         "Check the display cable/brightness and try to enter the BIOS. If no image appears, have the device inspected.",
         "The computer begins powering on but does not complete a normal visible startup.", 3),
    # Performance
    Rule("S01", {"disk_usage_high": True, "low_storage": True}, "Storage overload",
         "Free disk space, delete temporary files, and restart the computer.",
         "A nearly full drive together with high disk activity can severely slow Windows.", 4),
    Rule("S02", {"many_startup_apps": True}, "Too many startup programs",
         "Disable non-essential startup apps from Task Manager, then restart.",
         "Many programs launching at sign-in compete for CPU, memory, and disk resources.", 3),
    Rule("S03", {"malware_symptoms": True}, "Possible malware or unwanted software",
         "Run a full scan with trusted antivirus software and remove suspicious programs.",
         "Unexpected pop-ups or programs are common signs of unwanted software.", 4),
    Rule("S04", {"overheating": True}, "Overheating / cooling problem",
         "Shut down and let it cool, clear air vents, and have the fan or thermal paste checked if needed.",
         "Excess heat can make the processor reduce speed to protect itself.", 4),
    Rule("S05", {"disk_usage_high": True, "low_storage": False}, "High background disk activity",
         "Use Task Manager to identify disk-heavy programs; allow updates to finish or remove the problematic app.",
         "Disk use is high even though free space is available.", 2),
    # Network
    Rule("W01", {"wifi_enabled": False}, "Wi-Fi disabled or Airplane mode enabled",
         "Turn off Airplane mode and enable Wi-Fi, then reconnect to the network.",
         "The wireless adapter cannot connect when Wi-Fi is disabled.", 4),
    Rule("W02", {"wifi_enabled": True, "network_visible": False}, "Wi-Fi network not detected",
         "Move closer to the router, restart the router, and check whether the router is broadcasting its network.",
         "Wi-Fi is enabled but the expected network is not visible.", 3),
    Rule("W03", {"other_devices_online": False, "router_lights_normal": False}, "Router, modem, or ISP problem",
         "Restart the modem/router and check your internet service provider for an outage.",
         "Multiple devices are offline and router lights indicate a connection problem.", 4),
    Rule("W04", {"other_devices_online": True, "connected_no_internet": True}, "Local network configuration problem",
         "Forget and reconnect to the Wi-Fi network, then run the Windows network troubleshooter.",
         "The internet works on other devices, so the issue is likely limited to this computer.", 4),
    Rule("W05", {"other_devices_online": False, "router_lights_normal": True}, "Possible ISP outage or router configuration issue",
         "Restart the router and contact the ISP if the connection does not return.",
         "No connected device can access the internet despite normal-looking lights.", 2),
    # Printer
    Rule("R01", {"printer_on": False}, "Printer is powered off",
         "Turn on the printer and check its power cable and wall socket.",
         "A switched-off printer cannot receive or process jobs.", 4),
    Rule("R02", {"printer_on": True, "paper_loaded": False}, "Paper tray empty or paper-feed issue",
         "Load the correct paper, align the guides, and clear any visible jam.",
         "The printer has power but no usable paper supply.", 4),
    Rule("R03", {"printer_on": True, "ink_or_toner_available": False}, "Low or empty ink/toner",
         "Replace or refill the indicated ink/toner cartridge and run a test page.",
         "The printer cannot produce output without sufficient consumables.", 4),
    Rule("R04", {"printer_error_light": True}, "Printer hardware/status error",
         "Read the printer display/error code, clear jams, close covers, and consult the printer manual.",
         "The device itself reports an error condition.", 4),
    Rule("R05", {"print_queue_stuck": True}, "Stuck print queue",
         "Cancel stuck jobs, restart the Print Spooler service, and resend the document.",
         "Jobs waiting indefinitely in the queue prevent normal printing.", 3),
    # Audio
    Rule("A01", {"volume_up": False}, "System volume too low",
         "Increase the system and application volume, then test sound again.",
         "The system volume is not high enough to hear audio.", 4),
    Rule("A02", {"not_muted": False}, "Audio muted",
         "Unmute the system and application audio controls.",
         "Muted audio prevents sound output even when speakers work.", 4),
    Rule("A03", {"correct_output_selected": False}, "Wrong audio output device selected",
         "Select the intended speakers or headphones in Sound settings.",
         "Audio may be routed to a different device such as HDMI or Bluetooth.", 4),
    Rule("A04", {"headphones_connected": True, "correct_output_selected": True}, "Audio routed to headphones",
         "Unplug headphones or choose the speakers as the output device.",
         "Connected headphones commonly take priority over built-in speakers.", 3),
    Rule("A05", {"audio_driver_ok": False}, "Audio driver problem",
         "Restart the computer, then update or reinstall the audio driver from the device manufacturer's site.",
         "The operating system reports a problem with the audio hardware driver.", 4),
    # Display
    Rule("D01", {"monitor_on": False}, "Monitor/display powered off",
         "Turn on the monitor and check its power cable and power indicator.",
         "The display itself has no confirmed power.", 4),
    Rule("D02", {"monitor_on": True, "display_cable_secure": False}, "Loose or disconnected display cable",
         "Reconnect the cable at both ends and try a known-good cable or port.",
         "The monitor is powered but has no reliable video connection.", 4),
    Rule("D03", {"monitor_on": True, "display_cable_secure": True, "brightness_up": False}, "Display brightness too low",
         "Increase brightness using the monitor controls or keyboard brightness keys.",
         "The display path is connected but the image may be too dim to see.", 3),
    Rule("D04", {"monitor_on": True, "display_cable_secure": True, "computer_running": False}, "Computer startup/power issue",
         "Use the power troubleshooting section because the computer itself does not appear to start.",
         "The monitor is ready, but the computer is not running to provide a video signal.", 4),
    Rule("D05", {"computer_running": True, "external_display_works": True}, "Built-in display panel or cable issue",
         "Back up data and have the laptop display panel/cable inspected by a technician.",
         "Video works externally, isolating the fault to the built-in display path.", 4),
]


class InferenceEngine:
    """Runs forward chaining and exposes a backward-verification explanation."""

    def __init__(self, rules: Iterable[Rule] = RULES) -> None:
        self.rules = list(rules)

    @staticmethod
    def _rule_matches(rule: Rule, facts: Dict[str, Optional[bool]]) -> bool:
        return all(facts.get(fact) is value for fact, value in rule.conditions.items())

    def forward_chain(self, facts: Dict[str, Optional[bool]]) -> List[Diagnosis]:
        """Fire every fully supported IF-THEN rule, highest priority first."""
        matches = [rule for rule in self.rules if self._rule_matches(rule, facts)]
        grouped: Dict[str, List[Rule]] = {}
        for rule in matches:
            grouped.setdefault(rule.fault, []).append(rule)

        diagnoses = []
        for fault, fired in grouped.items():
            main_rule = max(fired, key=lambda item: item.priority)
            confidence = min(100, 55 + 10 * main_rule.priority + 5 * (len(fired) - 1))
            diagnoses.append(Diagnosis(
                fault=fault,
                solution=main_rule.solution,
                explanation=main_rule.explanation,
                fired_rules=fired,
                confidence=confidence,
            ))
        return sorted(diagnoses, key=lambda item: item.confidence, reverse=True)

    def likely_rules(self, facts: Dict[str, Optional[bool]], limit: int = 3) -> List[Rule]:
        """Return partially supported rules while the interview is unfinished."""
        scored = []
        for rule in self.rules:
            known = [(fact, expected) for fact, expected in rule.conditions.items() if facts.get(fact) is not None]
            conflicts = [pair for pair in known if facts.get(pair[0]) is not pair[1]]
            if conflicts or not known:
                continue
            score = len(known) / len(rule.conditions)
            scored.append((score, rule.priority, rule))
        return [item[2] for item in sorted(scored, reverse=True, key=lambda item: (item[0], item[1]))[:limit]]

    def verify_backward(self, diagnosis: Diagnosis, facts: Dict[str, Optional[bool]]) -> str:
        """Explain backward chaining: test a conclusion against its rule premises."""
        rule = diagnosis.fired_rules[0]
        checks = []
        for fact, expected in rule.conditions.items():
            observed = facts.get(fact)
            expected_word = "Yes" if expected else "No"
            observed_word = "Yes" if observed else "No" if observed is False else "Not sure"
            checks.append(f"{fact.replace('_', ' ')}: expected {expected_word}, observed {observed_word}")
        return "Backward verification of rule " + rule.rule_id + ":\n• " + "\n• ".join(checks)
