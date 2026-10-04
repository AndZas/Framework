# Normal Windows launchers: visible Qt windows, hidden console, no physical input.
param([string]$Output = 'evidence/TASK-0010/launch')
$ErrorActionPreference = 'Stop'
$repoPath = Split-Path $PSScriptRoot -Parent
$outputPath = [System.IO.Path]::GetFullPath((Join-Path $repoPath $Output))
New-Item -ItemType Directory -Force -Path $outputPath | Out-Null
$customDirectory = Join-Path $env:TEMP 'framework TASK-0010 launch'
New-Item -ItemType Directory -Force -Path $customDirectory | Out-Null
$customThemePath = Join-Path $customDirectory 'custom palette.theme'
Copy-Item -LiteralPath (Join-Path $repoPath 'examples/lagoon.theme') -Destination $customThemePath
$launches = @(
    @{ Name = 'ordinary'; Script = 'run.cmd'; Title = 'Python UI'; Argument = '' },
    @{ Name = 'studio'; Script = 'run-themes.cmd'; Title = 'Production themes'; Argument = '' },
    @{ Name = 'alternate-path'; Script = 'run-themes.cmd'; Title = 'Production themes'; Argument = $customThemePath }
)
$results = @()
foreach ($spec in $launches) {
    $oldProcessIds = @(Get-Process -Name python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id)
    $launcherPath = Join-Path $repoPath $spec.Script
    $commandText = 'call "' + $launcherPath + '"'
    if ($spec.Argument) { $commandText += ' "' + $spec.Argument + '"' }
    $stdoutPath = Join-Path $outputPath ($spec.Name + '-stdout.log')
    $stderrPath = Join-Path $outputPath ($spec.Name + '-stderr.log')
    $launcher = Start-Process -FilePath $env:ComSpec -ArgumentList @('/d', '/c', $commandText) `
        -WorkingDirectory $env:TEMP -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
    $visibleProcess = $null
    for ($attempt = 0; $attempt -lt 40; $attempt++) {
        Start-Sleep -Milliseconds 250
        $visibleProcess = Get-Process -Name python -ErrorAction SilentlyContinue |
            Where-Object { $_.Id -notin $oldProcessIds -and $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle.StartsWith($spec.Title) } |
            Select-Object -First 1
        if ($visibleProcess) { break }
        $launcher.Refresh()
        if ($launcher.HasExited) { break }
    }
    if (-not $visibleProcess) { throw "No new visible Qt window for $($spec.Name)" }
    $record = [ordered]@{ name = $spec.Name; command = $commandText; working_directory = $env:TEMP;
        window_title = $visibleProcess.MainWindowTitle; native_handle = $visibleProcess.MainWindowHandle.ToInt64();
        process_id = $visibleProcess.Id; physical_input = $false }
    if (-not $visibleProcess.CloseMainWindow()) { throw 'Unable to request window close' }
    if (-not $launcher.WaitForExit(10000)) { throw 'Launcher did not exit after closing window' }
    $launcher.Refresh()
    $record.exit_code = $launcher.ExitCode
    $record.stderr = [System.IO.File]::ReadAllText($stderrPath)
    $results += [pscustomobject]$record
    if ($launcher.ExitCode -ne 0 -or $record.stderr) { throw "Launch failed: $($spec.Name): $($record.stderr)" }
}
$results | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $outputPath 'launch.json') -Encoding UTF8
$results | Select-Object name, window_title, native_handle, exit_code, stderr
