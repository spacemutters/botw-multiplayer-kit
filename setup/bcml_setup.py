"""Point BCML at Cemu 1.26.2 and the BotW files, install the Milk Bar mod, and build the merged pack.

Run with the Python 3.8 that has bcml installed:
  python bcml_setup.py --cemu "C:\\BOTWMP\\Cemu" --game "<Game>\\content" --update "<Update>\\content"
                       --dlc "<DLC>\\content\\0010" --bnp "C:\\BOTWMP\\MilkBarLauncher\\BNPs\\MilkBarLauncher.bnp"

Proven on the host machine 2026-09-21. Notes:
- The launcher reads %LOCALAPPDATA%\\bcml\\settings.json directly and needs EVERY key (it failed with
  "The given key 'store_dir' was not present" when only a few were written), so this saves BCML's full set.
- install_mod(merge_now=True) merges but does not build merged\\content; link_master_mod() does, and the
  launcher checks for bcml\\merged\\content\\Actor\\Pack.
"""
import argparse
import json
import os
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cemu", required=True)
    ap.add_argument("--game", required=True, help="base game content folder (has Pack\\Dungeon000.pack)")
    ap.add_argument("--update", required=True, help="update v208 content folder")
    ap.add_argument("--dlc", required=True, help="DLC content\\0010 folder (has Pack\\AocMainField.pack)")
    ap.add_argument("--bnp", required=True)
    a = ap.parse_args()

    data_dir = Path(os.path.expandvars("%LOCALAPPDATA%")) / "bcml"
    data_dir.mkdir(parents=True, exist_ok=True)
    path = data_dir / "settings.json"
    settings = json.loads(path.read_text()) if path.exists() else {}
    settings.update({
        "cemu_dir": str(Path(a.cemu)),
        "game_dir": str(Path(a.game)),
        "update_dir": str(Path(a.update)),
        "dlc_dir": str(Path(a.dlc)),
        "lang": "USen",
        "wiiu": True,
        "no_cemu": False,
        "changelog": False,
        "suppress_update": True,
    })
    path.write_text(json.dumps(settings, indent=2), encoding="utf-8")

    from bcml import install, util
    util.get_settings()
    util.save_settings()  # writes BCML's full key set, including store_dir and export_dir
    print("game dir  :", util.get_game_dir())
    print("update dir:", util.get_update_dir())
    print("dlc dir   :", util.get_aoc_dir())
    print("cemu dir  :", util.get_cemu_dir())

    installed = [m.name for m in util.get_installed_mods()]
    if "Milk Bar Launcher" not in installed:
        install.install_mod(Path(a.bnp), merge_now=True)
    install.link_master_mod()

    store = Path(util.get_settings("store_dir"))
    gp = Path(a.cemu) / "graphicPacks"
    checks = {
        "settings.json has store_dir": "store_dir" in json.loads(path.read_text()),
        "merged Actor\\Pack (launcher's install check)": (store / "merged" / "content" / "Actor" / "Pack").is_dir(),
        "Cemu graphicPacks\\BreathOfTheWild_BCML": (gp / "BreathOfTheWild_BCML" / "rules.txt").exists(),
        "Cemu graphicPacks\\bcmlPatches\\MilkBarLauncher": (gp / "bcmlPatches" / "MilkBarLauncher" / "rules.txt").exists(),
    }
    for k, v in checks.items():
        print(("OK   " if v else "FAIL ") + k)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
