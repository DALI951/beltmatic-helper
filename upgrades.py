import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
UPGRADES_FILE = os.path.join(DATA_DIR, "upgrades.json")
PROGRESS_FILE = os.path.join(DATA_DIR, "progress.json")


def load_upgrades():
    with open(UPGRADES_FILE, "r") as f:
        return json.load(f)


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {
        "current_level": 1,
        "upgrade_levels": {
            "belt": 0,
            "extractor": 0,
            "adder": 0,
            "multiplier": 0,
            "subtractor_divider": 0,
            "exponentiator": 0
        },
        "delivered_numbers": {}
    }


def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def get_next_upgrade(upgrade_data, current_level):
    upgrades = load_upgrades()
    upgrade = upgrades.get(upgrade_data)
    if not upgrade:
        return None

    levels = upgrade["levels"]
    if current_level >= len(levels):
        return None

    return levels[current_level]


def get_all_upgrade_status():
    upgrades = load_upgrades()
    progress = load_progress()
    status = {}

    for key, upgrade in upgrades.items():
        current = progress["upgrade_levels"].get(key, 0)
        levels = upgrade["levels"]

        next_upgrade = None
        if current < len(levels):
            next_upgrade = levels[current]

        status[key] = {
            "name": upgrade["name"],
            "description": upgrade["description"],
            "current_level": current,
            "max_level": len(levels),
            "next_upgrade": next_upgrade,
            "all_levels": levels
        }

    return status


def get_level_requirements():
    with open(os.path.join(DATA_DIR, "levels.json"), "r") as f:
        data = json.load(f)
    return data["levels"]


def get_hub_status():
    progress = load_progress()
    delivered = progress.get("delivered_numbers", {})
    upgrades = load_upgrades()

    needed_for_upgrades = {}
    for key, upgrade in upgrades.items():
        current = progress["upgrade_levels"].get(key, 0)
        levels = upgrade["levels"]
        if current < len(levels):
            req = levels[current]["requirements"]
            for r in req:
                num = str(r["number"])
                if num not in needed_for_upgrades:
                    needed_for_upgrades[num] = {"total_needed": 0, "used_for": []}
                needed_for_upgrades[num]["total_needed"] += r["count"]
                needed_for_upgrades[num]["used_for"].append(upgrade["name"])

    result = {}
    for num_str, info in needed_for_upgrades.items():
        delivered_count = delivered.get(num_str, 0)
        result[num_str] = {
            "delivered": delivered_count,
            "needed": info["total_needed"],
            "used_for": info["used_for"],
            "remaining": max(0, info["total_needed"] - delivered_count)
        }

    return result
