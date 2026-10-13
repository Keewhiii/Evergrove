param(
    [string]$EngineRoot = 'E:\UE5\UE_5.8'
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ProjectFile = Join-Path $ProjectRoot 'AdventureRPG.uproject'
$AutomationTool = Join-Path $EngineRoot 'Engine\Build\BatchFiles\RunUAT.bat'
$EditorCommandlet = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$ArchiveDirectory = Join-Path $ProjectRoot 'Saved\PackagedSmoke'

foreach ($RequiredPath in @($ProjectFile, $AutomationTool, $EditorCommandlet)) {
    if (-not (Test-Path -LiteralPath $RequiredPath)) {
        throw "Required file does not exist: $RequiredPath"
    }
}

# Use the installed editor for cooking rather than rebuilding an editor target.
& $AutomationTool BuildCookRun "-project=$ProjectFile" -noP4 -platform=Win64 `
    -clientconfig=Development -nocompileeditor "-unrealexe=$EditorCommandlet" `
    -build -cook -stage -pak -package -archive "-archivedirectory=$ArchiveDirectory" `
    -unattended -utf8output
if ($LASTEXITCODE -ne 0) {
    throw "Unreal packaging failed with exit code $LASTEXITCODE."
}

Write-Output "Windows package: $ArchiveDirectory"
