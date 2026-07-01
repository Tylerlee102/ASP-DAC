# Agent Instructions

Before making project-status judgments or code/paper changes, read `docs/CHAT_CONTEXT.md`.

After adding, removing, or materially changing RTL, firmware, scripts, paper text, generated evidence, or artifact files, refresh the context snapshot:

```sh
make chat-context
```

On this Windows workspace, if `python` or `python3` resolves to the Microsoft Store alias, use:

```sh
make PYTHON="C:/Users/tyboy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe" chat-context
```

Do not manually edit `docs/CHAT_CONTEXT.md` for lasting changes. Edit `scripts/update_chat_context.py`, then regenerate the file.
