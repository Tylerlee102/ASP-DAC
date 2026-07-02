# Agent Instructions

Before making project-status judgments or code/paper changes, read `docs/CHAT_CONTEXT.md`.

After adding, removing, or materially changing RTL, firmware, scripts, paper text, generated evidence, or artifact files, refresh the context snapshot:

```sh
make chat-context
```

On Windows, if `python` or `python3` resolves to the Microsoft Store alias, pass a real Python executable explicitly:

```sh
make PYTHON="<path-to-real-python.exe>" chat-context
```

Do not manually edit `docs/CHAT_CONTEXT.md` for lasting changes. Edit `scripts/update_chat_context.py`, then regenerate the file.
