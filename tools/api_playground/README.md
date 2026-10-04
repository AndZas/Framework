# API Playground (Windows)

Run `setup.cmd` once with Python 3.13 installed, then run `run-playground.cmd`
from the repository or double-click it. The launcher resolves its own folder,
so it also works from another current directory. It uses the existing
`.venv-framework`; if that environment is missing, it prints
`Run setup.cmd first.` It does not install anything itself.

The Qt Quick editor starts with a short example using the public `App`,
`Window`, `Label`, and `Button` API. The authored app opens in a separate
native top-level window and Python process. See [the public API](../../docs/api.md)
for what the framework currently supports.

| Control | Behavior |
| --- | --- |
| Run / F5 | Save the exact current buffer, stop any previous child, then launch the saved file. |
| Stop / Shift+F5 | Stop the child and cancel any queued rerun. |
| Open / Ctrl+O | Open a Python file as UTF-8 (also accepts a UTF-8 BOM). |
| Save / Ctrl+S | Save as UTF-8 to the active file, or `.playground/scratch.py` for the initial buffer. |
| Save As / Ctrl+Shift+S | Select a file and make it the active source. |

An asterisk marks unsaved edits. Open and closing the editor offer Save,
Discard, or Cancel for unsaved text. A new starter asks before overwriting an
existing scratch file. To resume an earlier experiment, use Open. Personal
scratch files under the root `.playground/` directory are ignored by Git.
Save As can use a folder outside the repository; paths containing spaces work.
Tab inserts four spaces; the editor provides ordinary multi-line text editing.

The child uses the same Python executable as the editor and runs from the
active source file's parent folder, so relative assets and imports resolve
there. The editable framework installed by `setup.cmd` remains available.
Standard output and errors are decoded as UTF-8 and shown unbuffered in the
output panel, with startup, running, exit code, crash, and start-error status.
The panel retains the most recent 120,000 characters.

Run, Stop, and editor shutdown use asynchronous `QProcess` signals. Stop
first asks the child to terminate, then kills it after 1.5 seconds if needed;
on Windows the virtual-environment launcher or a console script may require
this fallback. Unsaved changes are handled before closing, and the editor
stays open until its child exits.
Only one direct child is managed. Python code that starts its own subprocesses
is responsible for their lifetime; forced termination cannot guarantee its
cleanup handlers run.

This repository tool currently targets Windows. It has no syntax highlighting,
completion, debugger, project navigation, API help pane, theme editor, or live
reload. Runs do not preserve application state. Execute your own trusted code:
the child process isolates ordinary crashes and hangs but provides unrestricted
Python file/system access. The public framework still owns one Window per App;
the Playground editor is a separate application. Physical usability, other
hardware/DPI setups, and other platforms require owner checks.
