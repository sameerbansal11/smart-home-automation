#!/usr/bin/env python3
"""
smart-home-automation — Python Backend / Simulation Engine
Simulates IoT sensor readings, device control logic, automation rules,
and generates a JSON data file the dashboard reads.

Author: Sameer Bansal
Reg No: RA2311032010061
College: SRM Institute of Science and Technology
Branch: B.Tech CSE (IoT) | Batch: 2023-2027
"""

import json
import os
import random
import time
import datetime
import math

# ── Constants ─────────────────────────────────────────────
OUTPUT_FILE = "output/home_data.json"
LOG_FILE = "output/automation_log.txt"

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BLUE = "\033[94m"

ROOMS = ["Living Room", "Bedroom", "Kitchen", "Bathroom", "Garage"]

os.makedirs("output", exist_ok=True)


# ── Device State ──────────────────────────────────────────
class SmartHome:
    def __init__(self) -> None:
        self.devices = {
            "Living Room": {
                "light": {"on": True, "brightness": 80, "color": "#FFD700"},
                "ac": {"on": True, "temp": 24, "mode": "cool", "fan": "auto"},
                "tv": {"on": False, "channel": 5, "volume": 30},
                "fan": {"on": True, "speed": 2},
            },
            "Bedroom": {
                "light": {"on": False, "brightness": 40, "color": "#4FC3F7"},
                "ac": {"on": True, "temp": 22, "mode": "cool", "fan": "low"},
                "fan": {"on": True, "speed": 1},
                "smart_lock": {"locked": True, "last_access": "08:32 AM"},
            },
            "Kitchen": {
                "light": {"on": True, "brightness": 100, "color": "#FFFFFF"},
                "exhaust": {"on": False, "speed": 1},
                "fridge": {"on": True, "temp": 4, "door": "closed"},
                "microwave": {"on": False, "timer": 0},
            },
            "Bathroom": {
                "light": {"on": False, "brightness": 60, "color": "#FFFFFF"},
                "exhaust": {"on": False, "speed": 1},
                "geyser": {"on": False, "temp": 45},
            },
            "Garage": {
                "light": {"on": False, "brightness": 100, "color": "#FFFFFF"},
                "gate": {"open": False, "auto_close": True},
                "security_cam": {"on": True, "recording": True, "motion": False},
            },
        }

        self.sensors = {
            room: {
                "temperature": round(random.uniform(22, 32), 1),
                "humidity": round(random.uniform(40, 75), 1),
                "motion": random.choice([True, False, False]),
                "light_level": random.randint(0, 1000),
                "air_quality": random.randint(50, 200),
            }
            for room in ROOMS
        }

        self.energy = {
            "total_kwh_today": round(random.uniform(4.0, 12.0), 2),
            "current_watts": random.randint(800, 2400),
            "monthly_kwh": round(random.uniform(120, 280), 1),
            "solar_generated": round(random.uniform(1.0, 5.0), 2),
            "cost_today_inr": 0.0,
            "peak_hour": "18:00 - 19:00",
        }
        self.energy["cost_today_inr"] = round(self.energy["total_kwh_today"] * 8.5, 2)

        self.automation_rules = [
            {
                "name": "Night Mode",
                "trigger": "time == 22:00",
                "action": "Turn off all lights except bedroom night lamp",
                "enabled": True,
                "last_triggered": "Yesterday 22:00",
            },
            {
                "name": "Motion Security",
                "trigger": "motion detected + time > 23:00",
                "action": "Turn on security cam + send alert",
                "enabled": True,
                "last_triggered": "2 hours ago",
            },
            {
                "name": "AC Auto-Off",
                "trigger": "no motion for 30 min",
                "action": "Turn off AC in that room",
                "enabled": True,
                "last_triggered": "10:45 AM",
            },
            {
                "name": "Morning Routine",
                "trigger": "time == 07:00",
                "action": "Open blinds, set AC to 25°C, turn on kitchen light",
                "enabled": True,
                "last_triggered": "Today 07:00",
            },
            {
                "name": "Rain Mode",
                "trigger": "humidity > 80%",
                "action": "Close windows alert, turn on exhaust fans",
                "enabled": False,
                "last_triggered": "3 days ago",
            },
        ]

        self.alerts: list = []
        self.log: list = []

    # ── Sensor Simulation ──────────────────────────────────
    def update_sensors(self) -> None:
        hour = datetime.datetime.now().hour
        for room, s in self.sensors.items():
            base_temp = 26 + 4 * math.sin((hour - 14) * math.pi / 12)
            s["temperature"] = round(base_temp + random.uniform(-1.5, 1.5), 1)
            s["humidity"] = round(
                max(30, min(90, s["humidity"] + random.uniform(-2, 2))), 1
            )
            s["motion"] = random.choices([True, False], weights=[1, 4])[0]
            s["light_level"] = max(0, s["light_level"] + random.randint(-50, 50))
            s["air_quality"] = max(
                30, min(300, s["air_quality"] + random.randint(-10, 10))
            )

    def run_automations(self) -> None:
        hour = datetime.datetime.now().hour
        alerts = []

        for room, s in self.sensors.items():
            if s["temperature"] > 35:
                alerts.append(
                    {
                        "type": "warning",
                        "room": room,
                        "msg": f"High temperature: {s['temperature']}°C",
                        "time": datetime.datetime.now().strftime("%H:%M:%S"),
                    }
                )
            if s["air_quality"] > 150:
                alerts.append(
                    {
                        "type": "warning",
                        "room": room,
                        "msg": f"Poor air quality AQI {s['air_quality']}",
                        "time": datetime.datetime.now().strftime("%H:%M:%S"),
                    }
                )
            if s["motion"] and hour >= 23:
                alerts.append(
                    {
                        "type": "security",
                        "room": room,
                        "msg": f"Motion detected at night in {room}",
                        "time": datetime.datetime.now().strftime("%H:%M:%S"),
                    }
                )

        self.alerts = alerts[-10:]

    def update_energy(self) -> None:
        active = sum(
            1
            for room in self.devices.values()
            for dev in room.values()
            if isinstance(dev, dict) and dev.get("on", False)
        )
        self.energy["current_watts"] = active * random.randint(80, 180)
        self.energy["total_kwh_today"] = round(
            self.energy["total_kwh_today"] + self.energy["current_watts"] / 1_000_000, 4
        )
        self.energy["cost_today_inr"] = round(self.energy["total_kwh_today"] * 8.5, 2)

    def to_dict(self) -> dict:
        return {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "devices": self.devices,
            "sensors": self.sensors,
            "energy": self.energy,
            "rules": self.automation_rules,
            "alerts": self.alerts,
        }

    def save(self) -> None:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def log_event(self, msg: str) -> None:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {msg}"
        self.log.append(line)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")


# ── CLI Display Helpers ───────────────────────────────────
def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def display_banner() -> None:
    print("=" * 56)
    print("       🏠 SMART HOME AUTOMATION BACKEND")
    print("       Author : Sameer Bansal | RA2311032010061")
    print("       College: SRMIST Kattankulathur")
    print("=" * 56)


def display_status(home: SmartHome) -> None:
    d = home.to_dict()
    print(f"\n  📅 {d['timestamp']}\n")

    e = d["energy"]
    print(f"  {BOLD}⚡ ENERGY{RESET}")
    print(
        f"  Current: {CYAN}{e['current_watts']}W{RESET}  "
        f"Today: {YELLOW}{e['total_kwh_today']} kWh{RESET}  "
        f"Cost: {GREEN}₹{e['cost_today_inr']}{RESET}  "
        f"Solar: {GREEN}{e['solar_generated']} kWh{RESET}"
    )

    print(f"\n  {BOLD}🌡️  ROOM SENSORS{RESET}")
    print(f"  {'Room':<14} {'Temp':>6} {'Humidity':>9} {'AQI':>5} {'Motion':>7}")
    print(f"  {'─' * 50}")
    for room, s in d["sensors"].items():
        temp_c = (
            GREEN
            if s["temperature"] <= 28
            else YELLOW if s["temperature"] <= 32 else RED
        )
        motion = f"{GREEN}YES{RESET}" if s["motion"] else "no"
        print(
            f"  {room:<14} "
            f"{temp_c}{s['temperature']:>5}°C{RESET} "
            f"{s['humidity']:>8}% "
            f"{s['air_quality']:>5} "
            f"{motion:>7}"
        )

    print(f"\n  {BOLD}📱 ACTIVE DEVICES{RESET}")
    for room, devs in d["devices"].items():
        active = [
            name
            for name, dev in devs.items()
            if isinstance(dev, dict)
            and dev.get("on", dev.get("open", dev.get("recording", False)))
        ]
        if active:
            print(f"  {CYAN}{room:<14}{RESET} {', '.join(active)}")

    if d["alerts"]:
        print(f"\n  {BOLD}{RED}🔔 ALERTS{RESET}")
        for a in d["alerts"][-3:]:
            icon = "🔐" if a["type"] == "security" else "⚠️ "
            print(f"  {icon} [{a['time']}] {a['room']}: {a['msg']}")


def control_device(home: SmartHome) -> None:
    print(f"\n  {BOLD}DEVICE CONTROL{RESET}")
    for i, r in enumerate(ROOMS, 1):
        print(f"  [{i}] {r}")
    try:
        ri = int(input("  Choose room: ").strip()) - 1
        room = ROOMS[ri]
    except (ValueError, IndexError):
        print(f"  {YELLOW}Invalid room.{RESET}")
        return

    devs = list(home.devices[room].keys())
    print(f"\n  Devices in {room}:")
    for i, d in enumerate(devs, 1):
        dev = home.devices[room][d]
        is_on = dev.get("on", dev.get("locked", dev.get("open", False)))
        color = GREEN if is_on else RED
        status = "ON / ACTIVE" if is_on else "OFF"
        print(f"  [{i}] {d:<16} {color}{status}{RESET}")

    try:
        di = int(input("  Choose device: ").strip()) - 1
        dev = devs[di]
        state = home.devices[room][dev]
    except (ValueError, IndexError):
        print(f"  {YELLOW}Invalid device.{RESET}")
        return

    if "on" in state:
        state["on"] = not state["on"]
        status = "ON" if state["on"] else "OFF"
        print(f"  {GREEN}✅ {room} → {dev} turned {status}{RESET}")
        home.log_event(f"{room} {dev} turned {status}")
    elif "locked" in state:
        state["locked"] = not state["locked"]
        print(
            f"  {GREEN}✅ Smart lock {'LOCKED' if state['locked'] else 'UNLOCKED'}{RESET}"
        )
        home.log_event(
            f"{room} smart_lock {'LOCKED' if state['locked'] else 'UNLOCKED'}"
        )
    elif "open" in state:
        state["open"] = not state["open"]
        print(f"  {GREEN}✅ Gate {'OPENED' if state['open'] else 'CLOSED'}{RESET}")
        home.log_event(f"{room} gate {'OPENED' if state['open'] else 'CLOSED'}")
    else:
        print(f"  {YELLOW}Cannot toggle this device directly.{RESET}")

    home.save()


def live_monitor(home: SmartHome, cycles: int = 5) -> None:
    print(f"\n  {CYAN}Live monitor: {cycles} updates every 2 seconds...{RESET}")
    for i in range(1, cycles + 1):
        home.update_sensors()
        home.run_automations()
        home.update_energy()
        home.save()
        print(f"\n  {'─' * 52}  Update #{i}/{cycles}")
        display_status(home)
        if i < cycles:
            time.sleep(2)
    print(f"\n  {GREEN}✅ Done. Data saved → {OUTPUT_FILE}{RESET}")


def show_rules(home: SmartHome) -> None:
    print(f"\n  {BOLD}⚙️  AUTOMATION RULES{RESET}")
    print(f"  {'─' * 54}")
    for i, r in enumerate(home.automation_rules, 1):
        status = f"{GREEN}ENABLED{RESET}" if r["enabled"] else f"{RED}DISABLED{RESET}"
        print(f"\n  [{i}] {BOLD}{r['name']}{RESET}  [{status}]")
        print(f"      Trigger  : {r['trigger']}")
        print(f"      Action   : {r['action']}")
        print(f"      Last run : {YELLOW}{r['last_triggered']}{RESET}")


def toggle_rule(home: SmartHome) -> None:
    show_rules(home)
    try:
        idx = int(input("\n  Enter rule number to toggle: ").strip()) - 1
        rule = home.automation_rules[idx]
        rule["enabled"] = not rule["enabled"]
        status = "ENABLED" if rule["enabled"] else "DISABLED"
        print(f"  {GREEN}✅ Rule '{rule['name']}' → {status}{RESET}")
        home.log_event(f"Rule '{rule['name']}' {status}")
        home.save()
    except (ValueError, IndexError):
        print(f"  {YELLOW}Invalid selection.{RESET}")


def show_energy(home: SmartHome) -> None:
    e = home.energy
    print(f"\n  {BOLD}⚡ ENERGY REPORT{RESET}")
    print(f"  {'─' * 40}")
    print(f"  Current Load     : {CYAN}{e['current_watts']} W{RESET}")
    print(f"  Today's Usage    : {YELLOW}{e['total_kwh_today']} kWh{RESET}")
    print(f"  Cost Today       : {GREEN}₹{e['cost_today_inr']}{RESET}  (@ ₹8.5/kWh)")
    print(f"  Monthly Usage    : {e['monthly_kwh']} kWh")
    print(f"  Solar Generated  : {GREEN}{e['solar_generated']} kWh{RESET}")
    print(f"  Peak Hour        : {e['peak_hour']}")
    net = round(e["total_kwh_today"] - e["solar_generated"], 2)
    print(f"  Net Grid Usage   : {YELLOW}{net} kWh{RESET}")


def show_menu() -> None:
    print(f"""
  {BOLD}MAIN MENU{RESET}
  [1] Live status (snapshot)
  [2] Live monitor (5 auto-updates, 2s interval)
  [3] Control a device
  [4] View/toggle automation rules
  [5] Energy report
  [6] View alerts
  [7] View event log
  [q] Quit
""")


# ── Main ──────────────────────────────────────────────────
def main() -> None:
    clear()
    display_banner()

    home = SmartHome()
    home.update_sensors()
    home.run_automations()
    home.save()
    home.log_event("Smart Home Backend started")

    total_devs = sum(len(d) for d in home.devices.values())
    print(f"\n  {GREEN}✅ Smart Home Backend Ready!{RESET}")
    print(f"  🏠 Rooms          : {len(ROOMS)}")
    print(f"  📱 Total devices  : {total_devs}")
    print(f"  📁 Data file      : {OUTPUT_FILE}")
    print(f"  📋 Log file       : {LOG_FILE}")

    show_menu()

    while True:
        try:
            choice = input("  → ").strip().lower()

            if choice == "q":
                home.log_event("Smart Home Backend stopped")
                print(f"\n  👋 Backend stopped. Goodbye!\n")
                break
            elif choice == "1":
                home.update_sensors()
                home.run_automations()
                home.update_energy()
                home.save()
                display_status(home)
            elif choice == "2":
                live_monitor(home)
            elif choice == "3":
                control_device(home)
            elif choice == "4":
                toggle_rule(home)
            elif choice == "5":
                show_energy(home)
            elif choice == "6":
                if home.alerts:
                    print(
                        f"\n  {BOLD}{RED}🔔 ACTIVE ALERTS ({len(home.alerts)}){RESET}"
                    )
                    for a in home.alerts:
                        icon = "🔐" if a["type"] == "security" else "⚠️ "
                        print(f"  {icon} [{a['time']}] {a['room']}: {a['msg']}")
                else:
                    print(f"\n  {GREEN}✅ No active alerts. All systems normal.{RESET}")
            elif choice == "7":
                if os.path.exists(LOG_FILE):
                    print(f"\n  {BOLD}📋 EVENT LOG (last 15 entries){RESET}")
                    with open(LOG_FILE) as f:
                        lines = f.readlines()
                    for line in lines[-15:]:
                        print(f"  {CYAN}{line.rstrip()}{RESET}")
                else:
                    print(f"  {YELLOW}Log file is empty.{RESET}")
            elif choice == "menu":
                show_menu()
            else:
                print(
                    f"  {YELLOW}⚠️  Unknown option. Type 'menu' to see choices.{RESET}"
                )

        except KeyboardInterrupt:
            home.log_event("Smart Home Backend interrupted")
            print(f"\n\n  👋 Interrupted. Goodbye!")
            break


if __name__ == "__main__":
    main()
