# Opens a Claude Code session per bug-mining source, one Windows Terminal tab each (mining/sessions.md).
#   start-sessions.ps1 keycloak ghsa-pip ghsa-maven     # collection sessions, one batch each
#   start-sessions.ps1 -Here keycloak                   # in the current window
#   start-sessions.ps1 -Internal                        # internal session
# Each collection session gets its batch name (next b-NN or an unfinished one) and a session ID in the prompt:
# the session name «Выгрузка багов — <id> b-NN» names its reports, the ID is their first line.
param(
    [Parameter(ValueFromRemainingArguments = $true)][string[]]$Sources,
    [switch]$Internal,
    [switch]$Here
)

$root = (Resolve-Path "$PSScriptRoot\..\..").Path
$known = Select-String -Path "$PSScriptRoot\sources.yaml" -Pattern '^\s*- id: (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value }

function Next-Batch([string]$id) {
    $dir = Join-Path $root "Api\build\mining\$id\batches"
    $nums = @(Get-ChildItem -Path $dir -Filter 'b-*.ids' -ErrorAction SilentlyContinue |
        ForEach-Object { if ($_.BaseName -match '^b-(\d+)$') { [int]$Matches[1] } } | Sort-Object)
    if (-not $nums) { return 'b-01' }
    $last = $nums[-1]
    if (-not (Test-Path (Join-Path $dir ('b-{0:D2}.out.jsonl' -f $last)))) { return 'b-{0:D2}' -f $last }  # unfinished
    return 'b-{0:D2}' -f ($last + 1)
}

$jobs = @()
if ($Internal) {
    $sid = [guid]::NewGuid().ToString()
    $jobs += @{ Title = 'внутренняя'; Name = 'Выгрузка багов — внутренняя'; Id = $sid
        Prompt = "Внутренняя сессия выгрузки багов (ID сессии $sid): работай по Api/mining/sessions.md, раздел «Внутренняя сессия». Начни с пункта 1." }
}
foreach ($id in $Sources) {
    if ($known -notcontains $id) { Write-Warning "нет источника '$id' в sources.yaml — пропуск"; continue }
    $batch = Next-Batch $id
    $sid = [guid]::NewGuid().ToString()
    $jobs += @{ Title = "$id $batch"; Name = "Выгрузка багов — $id $batch"; Id = $sid
        Prompt = "Выгрузка багов, источник $id, пачка $batch (ID сессии ${sid}): обработай её по Api/mining/sessions.md, раздел «Сессия сбора»." }
}
if (-not $jobs) { Write-Host 'Укажите источники (id из mining/sources.yaml) или -Internal'; exit 1 }

$wt = Get-Command wt -ErrorAction SilentlyContinue
foreach ($j in $jobs) {
    $claude = "claude -n `"$($j.Name)`" --session-id $($j.Id) --permission-mode auto `"$($j.Prompt)`""
    Write-Host $claude
    if ($Here) {
        Set-Location $root
        & claude -n $j.Name --session-id $j.Id --permission-mode auto $j.Prompt
    } elseif ($wt) {
        Start-Process wt -ArgumentList "-w mining new-tab -d `"$root`" --title `"$($j.Title)`" $claude"
    } else {
        Start-Process powershell -WorkingDirectory $root -ArgumentList '-NoExit', '-Command', $claude
    }
    Start-Sleep -Seconds 2
}
Write-Host "Запущено сессий: $($jobs.Count)"
