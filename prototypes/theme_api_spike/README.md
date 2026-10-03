# Theme studio — TASK-0008

Standalone PySide6 + Qt Quick experiment. No production imports or API changes.
All names and rules here are proposals, not an accepted architecture decision.

From the repository root in Windows PowerShell:

```powershell
.\prototypes\theme_api_spike\setup.cmd
.\prototypes\theme_api_spike\run.cmd
```

Setup uses installed Python 3.13, creates the ignored `.venv-theme-spike`, and
installs pinned PySide6 6.11.2 there. No global pip install or extra CSS parser.
The scripts locate the checkout independently of the caller's directory.

Click Light/Dark/System/CSS/Python. CSS reads `lagoon.theme`; Python applies the
equivalent `CUSTOM` object. Edit the file and click Load / reload, or paste a
different file path. Use wheel/scrollbar to reach the status at short heights.
The amber constructor and method examples start equal. Update local style (or
click either local sample) changes only the constructor example through Python.
Clear local override restores its global appearance. Global style selects Python.
Tab and Space use Qt Controls defaults; physical keyboard behavior needs review.

## Authoring examples

```css
:theme {
    accent: #126e67;
    radius: 20;
    opacity: 0.94;
    gradient: linear-gradient(#126e67, #65b8a3);
}
```

Equivalent partial Python theme (omitted tokens use the same defaults):

```python
from theme import Theme
theme = Theme("Lagoon", accent="#126e67", radius=20, opacity=0.94,
              gradient=("#126e67", "#65b8a3"))
file_theme = Theme.load("lagoon.theme")
```

The full equivalent pair lives in `lagoon.theme` and `theme.py:CUSTOM`.
Four additional complete CSS-like themes can be loaded with the existing path
field and Load / reload button:

| File (under `prototypes/theme_api_spike/`) | Appearance |
| --- | --- |
| `sunset.theme` | Warm cream, rose accent, rose-to-copper gradient |
| `lavender.theme` | Pale lavender, violet accent, violet-to-berry gradient |
| `ocean.theme` | Cool blue, ocean accent, blue-to-teal gradient |
| `midnight.theme` | Dark indigo, lilac accent, purple-to-deep-blue gradient |

For example, from the normal repository-root launch, paste
`prototypes/theme_api_spike/sunset.theme` into the path field. Absolute paths
also work. Click Clear local override to let the constructor sample inherit the
new accent; the method sample keeps its intentional amber override.

Illustrative local authoring using this prototype's model:

```python
from app import Widget
widget = Widget(theme, style={"accent": "#b45309", "radius": 6})
twin = Widget(theme)
twin.set_style(accent="#b45309", radius=6)
widget.set_style(accent="#8e3e91", radius=24, opacity=0.8)
widget.set_style()  # clear local values
```

`Widget` is a small retained style model, not a proposed complete public control.
The laboratory binds two of these models to Qt Quick buttons. Production adoption
would require a separate task.

## Exact grammar and resolution

UTF-8 (optional BOM); one case-sensitive `:theme { ... }` block. Declarations
are `token: value;`, including the final semicolon. Whitespace/newlines allowed;
empty block allowed. Only these eight tokens exist:

| CSS token | Python name | Value |
| --- | --- | --- |
| background | background | #RRGGBB |
| foreground | foreground | #RRGGBB |
| panel | panel | #RRGGBB |
| accent | accent | #RRGGBB |
| accent-text | accent_text | #RRGGBB |
| radius | radius | unitless decimal, 0..48, interpreted as Qt logical pixels |
| opacity | opacity | unitless decimal, 0..1 |
| gradient | gradient | linear-gradient(#RRGGBB, #RRGGBB); fixed horizontal, two stops |

Hex digits are case-insensitive and normalized. Python uses finite int/float
(not bool), and a two-color tuple/list for gradient. Unsupported selectors,
comments, duplicate tokens, units, functions, named/short/alpha colors, variables,
imports, cascading blocks and CSS layout are rejected. No browser CSS claim.
Errors identify the file/source, token and input; declaration errors include
the starting token's line. Structural/final-semicolon errors identify the source.
Unknown tokens and out-of-range values do not silently fall back.

Resolution is **built-in light defaults < current theme < local explicit style**.
Omission inherits; it never keeps a token from the previously selected theme.
Theme construction and `set_style` validate before mutation. `set_style` replaces
the entire local dictionary, rather than merging, and an empty call clears it.
Theme selection leaves local dictionaries intact. Failed load retains the theme
and both widgets. There is no automatic contrast correction: local accent text
is explicitly white to preserve local intent. Authors must choose readable colors.

Background/foreground drive window and copy; panel drives cards; accent and
accent-text drive buttons and input selection. Radius drives cards/buttons;
opacity applies to whole buttons including text; gradient fills the hero card.
Hero text is fixed white, independent of accent-text. A production gradient-text
semantic token is an open choice. Focus/hover use a border; no animation timelines.

System uses `QGuiApplication.styleHints().colorScheme()` and subscribes to its
change signal. This Windows run reported Dark and selected the dark palette.
Actual Windows Light→Dark→Light transitions have not been verified. The window
shows this limitation. Unknown reports an error and keeps the last palette; no
scheme is guessed. No registry/native adapter or OS setting changes are used.

## Evaluation and recommendation

CSS-like files keep reusable palettes separate from behavior, are short to edit,
and need no Python execution. Their cost is a grammar, source diagnostics and
future migration/versioning. The small stdlib parser is enough for eight tokens;
full CSS would add considerably more complexity and is outside this experiment.
Python objects give editor completion opportunities, composition and calculated
values, with the same validation/resolution cost but no text parsing. Current
kwargs are not statically typed; a typed token object would improve tooling.

Recommend a minimal shared validated token model, `Theme.load(path)` and a Python
`Theme(...)` equivalent, plus constructor `style=` and one `set_style(...)`
replacement method for later changes. Both local paths are practical and render
identically initially. Prefer constructor configuration for initial intent, the
method for callbacks. Replacement makes reset and invalid-update rollback clear;
partial patch semantics, if desired, should get a distinct name.

Keep the single semantic block initially, with no selectors/cascade. Names,
allowed units/ranges, light/dark variants within a reusable theme, inheritance,
gradient direction/stops/text, disabled/pressed/focus tokens, contrast validation,
typed Python ergonomics, schema versioning, and file watching remain owner choices.
This experiment resolves a small token dictionary on notifications. No profiling,
large widget-tree performance or production lifecycle design is claimed.

## Verification

```powershell
.\.venv-theme-spike\Scripts\python.exe -m unittest discover -s prototypes/theme_api_spike -p test_theme.py -v
.\.venv-theme-spike\Scripts\python.exe prototypes/theme_api_spike/probe.py
```

Five focused unittest cases cover equivalent sources, partial fallback and all
three precedence levels, invalid syntax/value matrices and defensive copies.
`probe.py` opens a visible window and uses QtTest synthetic clicks/wheel input;
it verifies live sources, local update/clear/persistence, failed loads/updates,
file reload, detected system mode, and horizontal bounds at 620×520. CSS/Python
sample pixels are compared at x=0..1039, y=260..649 in a 1040×820 window (excluding
source-button focus and source-dependent status). Captures and `probe.json` are
in `evidence/`. Normal launcher title/handle/exit are in `launch.json`.

See the task report for observed environment/results and Git commits. Owner should
physically exercise input, editing/reloading invalid files, live Windows scheme
changes and visual preferences. Other OSs, DPI/hardware, accessibility, prolonged
use, file watching, touch and distribution are unverified or out of scope.
