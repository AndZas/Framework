# Real launcher and visible Qt window; programmatic close, no physical input.
param([string]$Output = 'evidence/TASK-0012/launch')
$ErrorActionPreference = 'Stop'
$repoPath = Split-Path $PSScriptRoot -Parent
$outputPath = [System.IO.Path]::GetFullPath((Join-Path $repoPath $Output))
New-Item -ItemType Directory -Force -Path $outputPath | Out-Null
$oldProcessIds = @(Get-Process -Name python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id)
$launcherPath = Join-Path $repoPath 'run-playground.cmd'
$commandText = 'call "' + $launcherPath + '"'
$stdoutPath = Join-Path $outputPath 'stdout.log'
$stderrPath = Join-Path $outputPath 'stderr.log'
$launcher = Start-Process -FilePath $env:ComSpec -ArgumentList @('/d', '/c', $commandText) `
    -WorkingDirectory $env:TEMP -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
$visibleProcess = $null
try {
    for ($attempt = 0; $attempt -lt 40; $attempt++) {
        Start-Sleep -Milliseconds 250
        $visibleProcess = Get-Process -Name python -ErrorAction SilentlyContinue |
            Where-Object { $_.Id -notin $oldProcessIds -and $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle.StartsWith('API Playground') } |
            Select-Object -First 1
        if ($visibleProcess) { break }
        $launcher.Refresh()
        if ($launcher.HasExited) { break }
    }
    if (-not $visibleProcess) { throw 'No new visible Playground window' }
    $record = [ordered]@{
        command = $commandText; working_directory = $env:TEMP
        window_title = $visibleProcess.MainWindowTitle
        native_handle = $visibleProcess.MainWindowHandle.ToInt64()
        process_id = $visibleProcess.Id; physical_input = $false
    }
    if (-not $visibleProcess.CloseMainWindow()) { throw 'Unable to request window close' }
    if (-not $launcher.WaitForExit(10000)) { throw 'Launcher did not exit after editor close' }
    $launcher.Refresh()
    $record.exit_code = $launcher.ExitCode
    $record.stderr = [System.IO.File]::ReadAllText($stderrPath)
    if ($launcher.ExitCode -ne 0 -or $record.stderr) { throw "Launch failed: $($record.stderr)" }

    # Copy just the launcher into an isolated spaced folder with no environment.
    $missingFolder = Join-Path $repoPath ".playground/launcher check with spaces $PID"
    New-Item -ItemType Directory -Force -Path $missingFolder | Out-Null
    $missingLauncher = Join-Path $missingFolder 'run-playground.cmd'
    Copy-Item -LiteralPath $launcherPath -Destination $missingLauncher
    $missingText = & $env:ComSpec /d /c "call `"$missingLauncher`"" 2>&1
    $missingCode = $LASTEXITCODE
    if ($missingCode -ne 1 -or ($missingText -join "`n") -notmatch 'Run setup.cmd first\.') {
        throw 'Missing-environment instruction failed'
    }
    $record.missing_environment_exit_code = $missingCode
    $record.missing_environment_output = ($missingText -join "`n")
    $record | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $outputPath 'launch.json') -Encoding UTF8
    [pscustomobject]$record | Format-List
}
finally {
    # Clean up only the processes created by this probe if a check failed.
    if ($visibleProcess -and -not $visibleProcess.HasExited) { $visibleProcess.Kill() }
    if (-not $launcher.HasExited) { $launcher.Kill() }
}
