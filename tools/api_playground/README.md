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
| Run / F5 | Save the exact Python source buffer, stop any previous child, then launch the saved Python file. |
| Stop / Shift+F5 | Stop the child and cancel any queued rerun. |
| Open / Ctrl+O | Open a Python file, or a `.theme` file while the Theme tab is selected, as UTF-8 (also accepts a UTF-8 BOM). |
| Save / Ctrl+S | Save the selected text buffer as plain UTF-8 to its active file, or `.playground/scratch.py` / `.playground/scratch.theme` for a new buffer. |
| Save As / Ctrl+Shift+S | Select a file for the selected buffer. Theme files use a `.theme` filter and default extension. |
| Python source / API Docs / Theme tabs | Switch between independent source/theme buffers and the formatted API reference. Output and Run/Stop remain available. |
| Validate (Theme) | Check the current in-memory text with the public `Theme.parse` API; show success or the parser's source/line/token diagnostic. |
| Preview Theme (Theme) | Validate, offer Save/Cancel when the theme needs saving, then replace the current child with a native theme sample. |
| Reload (API Docs) | Reread this checkout's `docs/api.md`, including changes made since startup. |
| Find field / Ctrl+F (API Docs) | Case-insensitive literal search in the rendered document, including code and table cells. The current match is selected and scrolled into view. |
| Next / Enter / F3; Previous / Shift+F3 | Navigate matches, wrapping at either end. |
| Clear / Esc (API Docs) | Clear the query and its selection. |

An asterisk on each text tab marks its unsaved edits. Open protects only the
buffer it replaces; closing offers Save, Discard, or Cancel for Python and then
Theme when each is dirty. Cancel keeps the editor, both buffers, and the child
open, including when Discard was selected in the preceding prompt. Saving one
buffer never saves or changes the other. A new starter asks before overwriting
its existing scratch file. To resume an earlier experiment, use Open. Personal
scratch files under the root `.playground/` directory are ignored by Git.
Save As can use a folder outside the repository; paths containing spaces work.
Tab inserts four spaces; the editor provides ordinary multi-line text editing.

Theme starts with an editable palette covering all supported tokens. Use Open
on the Theme tab to load `examples/lagoon.theme` or your own file. Validate is
read-only: it leaves both buffers, saved files, and the running child alone.
Invalid preview input shows the same parser diagnostic and does not save or
stop the child. Save can still store invalid text for later editing. The
format is the framework's small [CSS-inspired theme grammar](../../docs/themes.md),
with no general CSS support, highlighting, or color picker.

Preview Theme needs a saved file. If the theme is new, dirty, deleted, or
changed externally, choose Save to write the editor text or Cancel to keep the
current child. Use Save As first to choose another location. Preview loads
the saved file with `Theme.load` and passes it to `App(..., theme=theme)`;
it does not modify the authored Python file. Its Window and Labels show
background, foreground/panel, radius and opacity. Two clickable Buttons show
the theme's gradient and solid accent, plus accent text; activation updates
a status Label and Output. Theme opacity below 1 affects the native window
and each control, so the effects can compound.

Only one child runs: Preview Theme replaces a running authored app or earlier
preview through the same asynchronous stop/start lifecycle. The Theme tab
states this beside the action, and Output records the preview path. Save or
reopen edits and press Preview again to restart with the new values; no live
reload occurs. Run / F5 always saves and relaunches the Python source,
including while Theme or API Docs is selected. File controls on API Docs
continue to act on Python source.

API Docs reads the canonical `docs/api.md` at startup, resolving it from the
repository containing the Playground rather than the process working directory
or the active Python file. There is no generated or separately maintained copy.
Qt Quick renders Markdown headings, lists, tables, inline code, fenced code,
and links. The pane has its own vertical and horizontal scrolling: prose wraps
as the window resizes, while code indentation and long code lines are preserved.
Drag the divider above Output to give either panel more space.

The viewer is read-only. Search and Reload leave the Python buffer, unsaved
state, and child application alone. Reload keeps the query and selects its first
match in the newly loaded document. A missing, unreadable, or invalid UTF-8 file
produces an in-pane error showing the source path; restore the file/access and
press Reload to retry. Run/Open/Save remain usable during a documentation error.
Internal heading links navigate within the pane. Other links show their target
in the pane for reference; the viewer does not open files or browse external
sites. Reload is explicit; the pane does not watch the document for changes.

The child uses the same Python executable as the editor and runs from the
active source file's parent folder, so relative assets and imports resolve
there. The theme sample uses the selected theme's parent folder. The editable
framework installed by `setup.cmd` remains available.
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
completion, debugger, project navigation, or live
reload. Runs do not preserve application state. Execute your own trusted code:
the child process isolates ordinary crashes and hangs but provides unrestricted
Python file/system access. The public framework still owns one Window per App;
the Playground editor is a separate application. Physical usability, other
hardware/DPI setups, and other platforms require owner checks.
