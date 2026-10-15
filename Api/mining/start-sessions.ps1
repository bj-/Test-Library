# Opens a Claude Code session per bug-mining source, one Windows Terminal tab each (mining/sessions.md).
#   start-sessions.ps1 keycloak ghsa-pip ghsa-maven     # collection sessions, one batch each
#   start-sessions.ps1 -Internal                        # internal session
param(
    [Parameter(ValueFromRemainingArguments = $true)][string[]]$Sources,
    [switch]$Internal
)

$root = (Resolve-Path "$PSScriptRoot\..\..").Path
$known = Select-String -Path "$PSScriptRoot\sources.yaml" -Pattern '^\s*- id: (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value }

$jobs = @()
if ($Internal) {
    $jobs += @{ Title = 'внутренняя'; Name = 'Выгрузка багов — внутренняя'
        Prompt = 'Внутренняя сессия выгрузки багов: работай по Api/mining/sessions.md, раздел «Внутренняя сессия». Начни с пункта 1.' }
}
foreach ($id in $Sources) {
    if ($known -notcontains $id) { Write-Warning "нет источника '$id' в sources.yaml — пропуск"; continue }
    $jobs += @{ Title = $id; Name = "Выгрузка багов — $id"
        Prompt = "Выгрузка багов, источник ${id}: обработай очередную пачку по Api/mining/sessions.md, раздел «Сессия сбора»." }
}
if (-not $jobs) { Write-Host 'Укажите источники (id из mining/sources.yaml) или -Internal'; exit 1 }

$wt = Get-Command wt -ErrorAction SilentlyContinue
foreach ($j in $jobs) {
    $claude = "claude -n `"$($j.Name)`" --permission-mode auto `"$($j.Prompt)`""
    if ($wt) {
        Start-Process wt -ArgumentList "-w mining new-tab -d `"$root`" --title `"$($j.Title)`" $claude"
    } else {
        Start-Process powershell -WorkingDirectory $root -ArgumentList '-NoExit', '-Command', $claude
    }
    Start-Sleep -Seconds 2
}
Write-Host "Запущено сессий: $($jobs.Count)"
