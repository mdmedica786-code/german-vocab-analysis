# Extract_Here.ps1 - unpacks the downloaded zip files into ONE folder: Documents\German_Study
#   German_Study\AI        words, Anki JSON, Redemittel, order guide  (give this folder to your AI agent)
#   German_Study\Obsidian  the vault                                  (in Obsidian: Open folder as vault -> Obsidian\German_Vault)
# The zip files in Downloads are NOT deleted; delete them yourself when everything looks right.
# Run:  right-click the file -> "Run with PowerShell"   (or: powershell -ExecutionPolicy Bypass -File .\Extract_Here.ps1)

$dl   = Join-Path $env:USERPROFILE 'Downloads'
$root = Join-Path $env:USERPROFILE 'Documents\German_Study'
$ai   = Join-Path $root 'AI'
$obs  = Join-Path $root 'Obsidian'
New-Item -ItemType Directory -Force -Path $ai, $obs | Out-Null

$jobs = @(
    @{ Name = '1_Words_to_learn';       To = (Join-Path $ai  '1_Words_to_learn') },
    @{ Name = '3_Anki_JSON_for_AI';     To = (Join-Path $ai  '3_Anki_JSON') },
    @{ Name = '4_Redemittel_up_to_B1';  To = (Join-Path $ai  '4_Redemittel_up_to_B1') },
    @{ Name = '2_Obsidian_Vault';       To = $obs }
)

foreach ($j in $jobs) {
    $zip = Get-ChildItem -Path $dl -Filter ($j.Name + '*.zip') -ErrorAction SilentlyContinue |
           Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $zip) { Write-Host ('NOT FOUND in Downloads: ' + $j.Name + '*.zip') -ForegroundColor Yellow; continue }
    Expand-Archive -LiteralPath $zip.FullName -DestinationPath $j.To -Force
    Write-Host ('OK  ' + $zip.Name + '  ->  ' + $j.To) -ForegroundColor Green
}

Write-Host ''
Write-Host ('Done. Everything is in: ' + $root)
Write-Host ('Obsidian: open the folder  ' + (Join-Path $obs 'German_Vault')  + '  as a vault.')
Write-Host ('AI agent: give it the folder ' + $ai + ' and the file 1_Words_to_learn\ORDER_FOR_ME_AND_MY_AGENT.md')
