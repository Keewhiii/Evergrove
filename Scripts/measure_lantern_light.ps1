$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$auditDirectory = Join-Path (Split-Path -Parent $PSScriptRoot) 'Saved\DayNightAudit'
$means = @()
foreach ($fileName in @('Midnight.png', 'Midnight_PointLightsOff.png')) {
    $bitmap = New-Object System.Drawing.Bitmap (Join-Path $auditDirectory $fileName)
    try {
        $sum = 0.0
        for ($y = 320; $y -lt 500; $y++) {
            for ($x = 300; $x -lt 600; $x++) {
                $pixel = $bitmap.GetPixel($x, $y)
                $sum += [double]$pixel.R + $pixel.G + $pixel.B
            }
        }
        $means += $sum / (300 * 180)
    } finally {
        $bitmap.Dispose()
    }
}
$result = @{ rgbMeanOn = $means[0]; rgbMeanOff = $means[1]; difference = $means[0] - $means[1] }
function Get-RegionLuminance([string]$Name, [int]$Left, [int]$Top, [int]$Right, [int]$Bottom) {
    $image = New-Object System.Drawing.Bitmap (Join-Path $auditDirectory $Name)
    try {
        $total = 0.0
        for ($row = $Top; $row -lt $Bottom; $row++) {
            for ($column = $Left; $column -lt $Right; $column++) {
                $color = $image.GetPixel($column, $row)
                $total += .2126 * $color.R + .7152 * $color.G + .0722 * $color.B
            }
        }
        return $total / (($Right - $Left) * ($Bottom - $Top))
    } finally { $image.Dispose() }
}
$forestDay = Get-RegionLuminance 'Noon.png' 900 50 1300 150
$forestNight = Get-RegionLuminance 'Midnight.png' 900 50 1300 150
$pathWithoutLight = Get-RegionLuminance 'Midnight_PointLightsOff.png' 300 400 600 480
$result.forestDayLuminance = $forestDay
$result.forestNightLuminance = $forestNight
$result.forestNightRatio = $forestNight / $forestDay
$result.pathNightLuminanceWithoutPointLights = $pathWithoutLight
$result | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $auditDirectory 'actual_light_contribution.json')
if ($result.difference -le 1) { throw 'Point light contribution was too small in the sampled ground region.' }
if ($result.forestNightRatio -ge .8) { throw 'Forest artwork did not darken enough compared with daytime.' }
if ($pathWithoutLight -le 20) { throw 'Night path was too dark without point lights.' }
$result | ConvertTo-Json
