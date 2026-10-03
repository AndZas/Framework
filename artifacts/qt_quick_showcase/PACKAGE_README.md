# Qt Quick showcase package (Windows evaluation)

Double-click `START_SHOWCASE.cmd`. Keep it beside the complete `QtQuickShowcase.dist` folder. The executable is `QtQuickShowcase.dist/example_app.exe`; neither Python nor a Qt SDK should be needed on the tested Windows setup.

The package includes the EXE, Python runtime, PySide6/Qt libraries and QML modules, local QML controls, multimedia plugins, and a synthetic MP4. It creates a WAV tone and a 2048 × 2048 test image in the Windows temporary directory on first launch. No media is downloaded. The folder is approximately 207 MB.

If the package fails, keep the console open and read the error. The source fallback is `demos/qt_quick_showcase/START_SOURCE.cmd` in the repository; it requires 64-bit Python 3.12 or 3.13 and may need internet on first launch. Full instructions and verified limits are in `demos/qt_quick_showcase/START_HERE.md`.

This is a personal evaluation build from the selected MVP foundation, PySide6 + Qt Quick (see the project decision record `docs/architecture/decisions/ADR-0001-pyside6-qt-quick.md`). The package is a showcase, not the production framework distribution.
