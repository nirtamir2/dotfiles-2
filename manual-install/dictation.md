# Dictation

Use **built-in macOS Dictation** for everyday speech-to-text. Verified in live
System Settings → Keyboard → Dictation on 30 September 2026:

- **Shortcut:** press **Right Command twice** to start or stop dictation.
- **Enabled:** on.
- **Languages:** English (United States) and Hebrew (Israel).
- **Microphone source:** Automatic (currently MacBook Pro Microphone).

Click in a text field, double-press Right Command, and speak. You can type
corrections while dictating on an Apple silicon Mac. Press Escape or double-press
Right Command again to finish. Switch dictation languages using the language
indicator next to the cursor.

`preferences/dictation.json` records the confirmed workflow. The active restore
settings are in `preferences/macos.json`: Dictation enabled, language selection,
and symbolic shortcut **164**. The installer merges that shortcut entry into
the existing macOS shortcut dictionary and backs up only the changed entry.

`./setup desktop` previews the restore; `./setup defaults`, `./setup desktop --apply`,
and the default `./setup install` apply it with backups. Log out and back in if
cached settings do not refresh, then verify the shortcut, languages, and Automatic
microphone source in Keyboard settings. macOS downloads required language assets
and may require its normal enablement prompts on a new Mac.

You can also restore the same settings with the installed `macos-defaults` tool:

```sh
macos-defaults --dry-run apply macos-defaults/dictation.yaml
macos-defaults apply macos-defaults/dictation.yaml
```

Its YAML merges nested dictionaries and preserves other shortcuts. The tool
creates its own `.plist.prev` backups; the `./setup` restore uses selective
preference journals. Verify Automatic microphone selection on the new Mac;
device identifiers and downloaded speech models are not copied.

Handy and other installed dictation apps are optional alternatives. Handy's
Right Option + 1 shortcut belongs to Handy; it is separate from the native
Right Command double-press.

The older setup note in `dicate-with-keyboard.md` is superseded by this workflow.
The saved `dictation.png` is a historical reference; the settings above were
verified live.

Reference: [Apple's Dictation guide](https://support.apple.com/guide/mac-help/dictate-messages-and-documents-mh40584/mac).
