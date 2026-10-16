$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$packageRoot = Join-Path $projectRoot 'Saved/BaselinePackage/Windows'
$manifest = Get-Content -LiteralPath (Join-Path $packageRoot 'Manifest_UFSFiles_Win64.txt') -Raw
foreach ($mapName in @('L_EvergroveIntro', 'L_WoodlandBlockout', 'L_EvergroveStart', 'L_EvergroveForest')) {
    if ($manifest -notmatch [regex]::Escape("Content/Maps/$mapName.umap")) {
        throw "Required map missing from package: $mapName"
    }
}
$travelLog = Join-Path $projectRoot 'Saved/Logs/EvergrovePackagedTravel.log'
$userDir = Join-Path $projectRoot 'Saved/EvergroveIntroAudit/PackagedTravelUser'
$gameExe = Join-Path $packageRoot 'AdventureRPG.exe'
& $gameExe -nullrhi -nosound -unattended -nosplash -seconds=10 "-UserDir=$userDir" "-abslog=$travelLog" '-ExecCmds=open /Game/Maps/L_EvergroveForest' | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Packaged game exited with $LASTEXITCODE" }
$logText = Get-Content -LiteralPath $travelLog -Raw
if ($logText -notmatch 'LoadMap: /Game/Maps/L_EvergroveIntro') { throw 'Intro map did not start' }
if ($logText -notmatch 'Bringing World .+L_EvergroveForest.+ up for play') { throw 'Packaged travel did not enter the rural forest map' }
if ($logText -match 'TravelFailure|Accessed None|Fatal error|Log\w+: Error:') { throw 'Packaged travel reported a runtime failure' }
$report = @{ introLoaded = $true; forestTravelSucceeded = $true; runtimeErrors = 0; exitCode = 0 }
$report | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $projectRoot 'Saved/EvergroveIntroAudit/packaged_travel.json')
$report | ConvertTo-Json
