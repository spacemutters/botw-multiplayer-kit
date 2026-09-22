# Prompt for the Claude agent on the joining friend's PC

Copy everything below the line into Claude Code (or the Claude desktop app's Code tab) on the friend's Windows PC. Fill in the three `<<...>>` values that Davis sends you privately first.

---

You are setting up **Breath of the Wild online multiplayer** (the open-source "Milk Bar Launcher", the re-release of PointCrow's BotW Multiplayer mod) on this Windows PC so I can join my friend Davis's server. Davis already has this exact setup working as the host. Your kit, with scripts and settings proven on Davis's machine, is at **https://github.com/spacemutters/botw-multiplayer-kit**. Clone or download it first and read `README.md`.

Davis's server details (from Davis, keep private):
- Radmin VPN network name: `<<NETWORK NAME>>`
- Radmin VPN network password: `<<NETWORK PASSWORD>>`
- Davis's Radmin VPN IP (shown in his Radmin window, starts with 26.): `<<HOST IP>>`, port `5050`

## Rules
- Download only from the official sources below. Verify every SHA-256 before extracting. Stop and tell me if a hash does not match.
- Do not change system or security settings yourself. When Windows asks for admin permission (UAC) or shows a firewall prompt, tell me what to click. I click it.
- Game files: I need my own copy of BotW in folder form (see step 1). If I don't have it, follow `GAME_FILES.md`: you set up the downloader, I click Download.
- Plain language when you talk to me. Verify each step before moving on. "The file exists" is not "it works".

## Versions must match Davis exactly
| Piece | Version | Official source | SHA-256 |
|---|---|---|---|
| Cemu | **1.26.2** (newer breaks the mod) | https://cemu.info/releases/cemu_1.26.2.zip | `b0e3abf5048f78e352b42c3e1660a2c6e85d6905cd9f60d06ca2f2318fa3152c` |
| Milk Bar Launcher | **2.0.1** | https://github.com/MilkBarModding/MilkBarLauncher/releases/download/2.0.1/MilkBarLauncher.zip | `8ed0b624489d601a54ce6cf16d6c1a0f43bac6a608d5e30cfb783d944a30f9b9` |
| Community graphic packs | v981 | https://github.com/cemu-project/cemu_graphic_packs/releases/download/Github981/graphicPacks981.zip | `f139e8e0107bce78934bd75326092f51d3ceaf73bcb216315a818e76cf39c6f8` |
| Python | **3.8.10** (BCML's GUI dependency cefpython3 has no wheels past 3.9) | https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe | Authenticode signer must be "Python Software Foundation" |
| BCML | 3.10.8 | `pip install bcml==3.10.8` into that Python 3.8 | from PyPI |
| BotW | base + **update v208** + **DLC** | my own copy | see step 1 |

Virus scan notes from Davis's machine: Defender is clean on all of these. On VirusTotal, the Milk Bar zip gets 1/66 (DrWeb "Program.Unwanted") and `Resources\InjectDLL.dll` gets 1/72 (Cynet heuristic). That is expected: the mod works by injecting that DLL into Cemu, and its source is public on the same GitHub repo.

## IMPORTANT gotcha if you run inside the Claude desktop app
The Claude desktop app is an MSIX package. When a process you launch creates a **new** folder under `%LOCALAPPDATA%` or `%APPDATA%`, the folder silently lands in `%LOCALAPPDATA%\Packages\Claude_<id>\LocalCache\{Local,Roaming}\...`. You will see it at the normal path, but apps I start from the desktop will not. On Davis's PC this broke BCML's settings, the merged mod, and the launcher's data.
- After any step that writes to AppData, check whether the folder exists under `%LOCALAPPDATA%\Packages\Claude_*\LocalCache\`.
- If it does, write a .bat that `robocopy /E`s it to the real path. Run it outside the sandbox with `Start-Process explorer.exe -ArgumentList "<path-to.bat>"`. Then **rename** (don't delete) the LocalCache copy so your view falls through to the real one.
- To test like a real user, open shortcuts with `explorer.exe "<shortcut>.lnk"`, not `Start-Process`.
- Paths outside AppData (for example `C:\BOTWMP`) are not affected.

## Steps
Use `C:\BOTWMP` as the install root unless I say otherwise.

1. **Find my BotW files.** (No files yet? Do `GAME_FILES.md` first.) The folder form has `code\`, `content\`, and `meta\` inside each title. Confirm:
   - base: `...\content\Pack\Dungeon000.pack` exists
   - update: `...\meta\meta.xml` has `<title_version>` **208**
   - DLC: `...\content\0010\Pack\AocMainField.pack` exists

   If they are in the encrypted form (title.tmd + .app files), use Cemu's File > "Install game title, update or DLC" instead, and adapt the paths below to Cemu's `mlc01\usr\title\...`.
2. **Cemu 1.26.2.** Download, verify, and extract to `C:\BOTWMP\Cemu` (Cemu.exe directly inside). Then give it the update and DLC with directory junctions, not copies:
   `mklink /J C:\BOTWMP\Cemu\mlc01\usr\title\0005000e\101c9400 "<Update folder>"` and
   `mklink /J C:\BOTWMP\Cemu\mlc01\usr\title\0005000c\101c9400 "<DLC folder>"`. Create the parent folders first.
3. **Graphic packs.** Extract graphicPacks981.zip into `C:\BOTWMP\Cemu\graphicPacks\downloadedGraphicPacks\`. Write `version.txt` there containing exactly `Cemu Graphic Packs: v981` (no newline).
4. **Python 3.8.10 + BCML.** Install per-user and quietly, without touching PATH or file associations:
   `python-3.8.10-amd64.exe /quiet InstallAllUsers=0 PrependPath=0 Include_launcher=0 AssociateFiles=0 Shortcuts=0 Include_test=0 TargetDir=%LOCALAPPDATA%\Programs\Python\Python38`
   Then run `%LOCALAPPDATA%\Programs\Python\Python38\python.exe -m pip install bcml==3.10.8` and confirm `import bcml` works.
5. **Milk Bar Launcher.** Download, verify, and extract to `C:\BOTWMP\MilkBarLauncher` (`Milk Bar Launcher.exe` directly inside). It needs the **.NET 8 Desktop Runtime**. Check with `dotnet --list-runtimes`. If it's missing, tell me and I'll run `winget install Microsoft.DotNet.DesktopRuntime.8`.
6. **BCML + mod install.** Run the kit's `setup\bcml_setup.py` with the Python 3.8 from step 4:
   `python setup\bcml_setup.py --cemu C:\BOTWMP\Cemu --game "<Game>\content" --update "<Update>\content" --dlc "<DLC>\content\0010" --bnp C:\BOTWMP\MilkBarLauncher\BNPs\MilkBarLauncher.bnp`
   All four lines must print `OK`. Then check the MSIX gotcha above for `%LOCALAPPDATA%\bcml`.
7. **Cemu settings.** Copy the kit's `setup\cemu-1.26.2-settings.xml` to `C:\BOTWMP\Cemu\settings.xml`. Replace `GAME_FOLDER` with the folder that *contains* my BotW game folder. Copy `setup\controller0.xml` to `C:\BOTWMP\Cemu\controllerProfiles\controller0.xml` for keyboard controls:
   - WASD: move
   - arrows: camera
   - Space: A
   - Left Shift: B
   - E: X
   - F: Y
   - Q/R: L/R
   - 1/3: ZL/ZR
   - Enter: +
   - Backspace: −

   If I have a gamepad, set it up in Cemu's Options > Input settings instead.
8. **A save past the starting shrine.** The mod's guide requires it. If I don't have such a save, launch Cemu directly: `C:\BOTWMP\Cemu\Cemu.exe -g "<Game folder>\code\U-King.rpx"`, *not* through the launcher. Let me play until I've walked out of the shrine, then save from the System menu.
9. **Radmin VPN.** Download the installer from https://www.radmin-vpn.com/ and check that it's signed by Famatech. I approve the UAC prompt. In Radmin VPN: Network > Join existing network, using the name and password above. Confirm Davis shows up online in the list.
10. **Launcher.**
    - Start `C:\BOTWMP\MilkBarLauncher\Milk Bar Launcher.exe` once. It creates `%APPDATA%\BOTWM\*`; check the MSIX gotcha. Let me type my player name. It asks for one while the name is "Link".
    - Click **Add Server**: any name, IP `<<HOST IP>>`, port `5050`, password blank.
    - **REQUIRED before every Connect:** start the kit's crash fix and leave it running: `python setup\mp_pinfix.py --loop 600` (any Python 3, no packages). Without it the mod crashes Cemu about 2 minutes after connecting. This is a bug in the mod on this build, proven on Davis's PC; details in README.md. Check `setup\mp_pinfix.log` shows "patched 32 marker records" and "planted terminator" after the game loads.
    - Once Davis's server is running, the entry shows a player count and ping. Then click **Connect**. The launcher starts Cemu, injects the mod, and opens the game.
11. **Verify it actually works.** Report each of these to me:
    - The server entry shows a ping, not an error.
    - After Connect, Cemu's window title shows `Breath of the Wild [US v208]`.
    - `%APPDATA%\BOTWM\LatestLog.txt` shows "Connected to server successfully" and "Scanned game instance successfully", with no repeating "Could not find map pin address".
    - Davis sees "Player <my name> joined the server" in his server window.
    - In game, Davis's Link is visible.

## Known errors and fixes
- **"The given key 'store_dir' was not present in the dictionary"**: BCML's settings.json is missing keys. Re-run `bcml_setup.py`, which saves BCML's full settings.
- **"The following needed graphic packs are not selected on Cemu"**: settings.xml is missing the `bcmlPatches\MilkBarLauncher` or `ExtendedMemory` entry (backslashes, relative paths), or Cemu rewrote it. Re-copy the template.
- **"Mod is not setup on BCML"**: `%LOCALAPPDATA%\bcml\merged\content\Actor\Pack` is missing. Re-run `bcml_setup.py`, then check the MSIX gotcha.
- **Cemu closes ~2 minutes after connecting** (mod log repeats "Could not find map pin address", or Cemu's log.txt shows an exception in InjectDLL.dll): `mp_pinfix.py` wasn't running. Start it, then Connect again.
- **Cemu opens with no sound**: `<TVDevice>` is empty. It must be `default`.
- **Cemu wants to update**: say no. It must stay 1.26.2.
- **Can't see Davis's server**: both machines must be online in the same Radmin network, and Davis's server must be running. Ping `<<HOST IP>>`.
