# Getting the game files (joiner side)

Give this to Claude before step 1 of `AGENT_PROMPT.md` if you don't already have Breath of the Wild in folder form.

1. Download WiiUDownloader v3.2 from its official page:
   https://github.com/Xpl0itU/WiiUDownloader/releases/download/v3.2/WiiUDownloader-Windows.zip
   SHA-256: `6645ad7de293659004cdb9db406e64160404da3b7c1bf9e897fa250f8462f526`. Extract to `C:\BOTWMP\WiiUDownloader`.
2. Before opening it, write `%APPDATA%\WiiUDownloader\config.json`:
   ```json
   {"decryptContents": true, "deleteEncryptedContents": true, "didInitialSetup": true,
    "lastSelectedPath": "C:\BOTWMP\Games", "rememberLastPath": true, "selectedRegion": 2}
   ```
   `2` = USA only, matching the host's US copy. Create `C:\BOTWMP\Games`. The Claude-app AppData gotcha in `AGENT_PROMPT.md` applies here too.
3. Open WiiUDownloader. The person does the clicking: search "Breath of the Wild", tick the Game row, then the same game on the Update and DLC tabs, and click Download. About 16 GB, saved straight into `C:\BOTWMP\Games`, already decrypted for Cemu.
4. Verify:
   - `...[Game] [00050000101c9400]\content\Pack\Dungeon000.pack` and `code\U-King.rpx` exist
   - `...[Update] [0005000e101c9400]\meta\meta.xml` contains `<title_version>208`
   - `...[DLC] [0005000c101c9400]\content\0010\Pack\AocMainField.pack` exists
   - no leftover `.app` or `.h3` files under those folders (they mean decryption didn't finish)
5. Use those three paths in steps 2, 6 and 7 of `AGENT_PROMPT.md`. `GAME_FOLDER` in the Cemu settings template is `C:\BOTWMP\Games`.

WiiUDownloader pulls the files from Nintendo's own servers. It's meant for people who own the game.
