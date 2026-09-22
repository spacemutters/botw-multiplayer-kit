# BotW Multiplayer Kit

Everything needed to join Davis's Breath of the Wild online multiplayer server (Milk Bar Launcher mod on Cemu 1.26.2), proven on his machine on 2026-09-21.

**To use it:** open `AGENT_PROMPT.md`, fill in the three values Davis sends you, and give the whole prompt to Claude on your PC. It does the rest and tells you when to click something.

What's here:
- `AGENT_PROMPT.md`: the step-by-step setup prompt, with official download links, exact versions, SHA-256 hashes, and every error we hit and how we fixed it.
- `setup/bcml_setup.py`: points BCML at Cemu and your game, installs the mod, and builds the merged pack, then prints OK/FAIL checks.
- `setup/cemu-1.26.2-settings.xml`: Cemu settings with the graphics packs the mod requires, sound on, and auto-update off.
- `setup/controller0.xml`: keyboard controls.

Not included on purpose:
- **The game.** You need your own copy of BotW with update v208 and the DLC.
- **Third-party programs.** Cemu, the Milk Bar Launcher, Python, and BCML are downloaded from their official sources. The Milk Bar license doesn't allow redistributing it.
