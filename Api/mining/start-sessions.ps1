# Opens a Claude Code session per bug-mining source, one Windows Terminal tab each (mining/sessions.md).
#   start-sessions.ps1 keycloak ghsa-pip ghsa-maven     # collection sessions, one batch each
#   start-sessions.ps1 -Here keycloak                   # in the current window
#   start-sessions.ps1 -Loop keycloak ghsa-pip          # a tab per source runs batch after batch until it is exhausted
#   start-sessions.ps1 -Internal                        # internal session
# Each collection session gets its batch name (next b-NN or an unfinished one) and a session ID in the prompt:
# the session name «Выгрузка багов — <id> b-NN» names its reports, the ID is their first line.
# -Loop runs non-interactive sessions (claude -p) one after another; it stops when the source is exhausted,
# when a batch is left unfinished (limit, error, a question for the human) or after MaxBatches.
param(
    [Parameter(ValueFromRemainingArguments = $true)][string[]]$Sources,
    [switch]$Internal,
    [switch]$Here,
    [switch]$Loop,
    [string]$RunLoop,          # internal: the loop itself, run inside a tab
    [int]$MaxBatches = 15
)

$root = (Resolve-Path "$PSScriptRoot\..\..").Path
$known = Select-String -Path "$PSScriptRoot\sources.yaml" -Pattern '^\s*- id: (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value }

function Batch-Dir([string]$id) { Join-Path $root "Api\build\mining\$id\batches" }

function Next-Batch([string]$id) {
    $dir = Batch-Dir $id
    $nums = @(Get-ChildItem -Path $dir -Filter 'b-*.ids' -ErrorAction SilentlyContinue |
        Where-Object { (Get-Content $_.FullName -Raw) -match '\S' } |  # an empty .ids (0 bugs) is not a batch
        ForEach-Object { if ($_.BaseName -match '^b-(\d+)$') { [int]$Matches[1] } } | Sort-Object)
    if (-not $nums) { return 'b-01' }
    $last = $nums[-1]
    if (-not (Test-Path (Join-Path $dir ('b-{0:D2}.out.jsonl' -f $last)))) { return 'b-{0:D2}' -f $last }  # unfinished
    return 'b-{0:D2}' -f ($last + 1)
}

function Remaining([string]$id) {  # -1 before collection
    $env:PYTHONUTF8 = '1'
    Push-Location (Join-Path $root 'Api')
    try { return [int](python tools\mining\batch.py remaining --batch $id) } finally { Pop-Location }
}

function Collect-Prompt([string]$id, [string]$batch, [string]$sid, [bool]$auto) {
    $p = "Выгрузка багов, источник $id, пачка $batch (ID сессии ${sid}): обработай её по Api/mining/sessions.md, раздел «Сессия сбора»."
    if ($auto) { $p += ' Режим -Loop: сессия неинтерактивная, вопросов не задавать — если нужно решение человека, написать это в итоге и в отчёте и закончить.' }
    return $p
}

function Invoke-Loop([string]$id) {
    Set-Location $root
    $log = Join-Path $root "Api\build\mining\$id\loop.log"
    New-Item -ItemType Directory -Force (Split-Path $log) | Out-Null
    for ($i = 1; $i -le $MaxBatches; $i++) {
        $batch = Next-Batch $id
        $unfinished = Test-Path (Join-Path (Batch-Dir $id) "$batch.ids")
        if (-not $unfinished -and (Remaining $id) -eq 0) { Write-Host "$id`: источник исчерпан"; return }
        $sid = [guid]::NewGuid().ToString()
        $name = "Выгрузка багов — $id $batch"
        Write-Host "[$(Get-Date -Format 'HH:mm')] $name — запуск (сессия $sid), вывод — $log"
        & claude -p -n $name --session-id $sid --permission-mode auto (Collect-Prompt $id $batch $sid $true) 2>&1 |
            ForEach-Object { $_; Add-Content -Path $log -Value $_ -Encoding UTF8 }
        if (-not (Test-Path (Join-Path (Batch-Dir $id) "$batch.out.jsonl"))) {
            if ((Remaining $id) -eq 0 -and -not (Test-Path (Join-Path (Batch-Dir $id) "$batch.ids"))) {
                Write-Host "$id`: источник исчерпан"; return
            }
            Write-Warning "$id`: пачка $batch не завершена — цикл остановлен, причина — в выводе выше и в $log"
            return
        }
    }
    Write-Host "$id`: выполнено $MaxBatches пачек (MaxBatches) — запустите -Loop снова"
}

if ($RunLoop) { Invoke-Loop $RunLoop; Read-Host 'Готово, Enter — закрыть'; exit }

$jobs = @()
if ($Internal) {
    $sid = [guid]::NewGuid().ToString()
    $jobs += @{ Title = 'внутренняя'; Name = 'Выгрузка багов — внутренняя'; Id = $sid
        Prompt = "Внутренняя сессия выгрузки багов (ID сессии $sid): работай по Api/mining/sessions.md, раздел «Внутренняя сессия». Начни с пункта 1." }
}
$loopIds = @()
foreach ($id in $Sources) {
    if ($known -notcontains $id) { Write-Warning "нет источника '$id' в sources.yaml — пропуск"; continue }
    if ($Loop) { $loopIds += $id; continue }
    $batch = Next-Batch $id
    $sid = [guid]::NewGuid().ToString()
    $jobs += @{ Title = "$id $batch"; Name = "Выгрузка багов — $id $batch"; Id = $sid; Prompt = (Collect-Prompt $id $batch $sid $false) }
}
if (-not $jobs -and -not $loopIds) { Write-Host 'Укажите источники (id из mining/sources.yaml) или -Internal'; exit 1 }

$wt = Get-Command wt -ErrorAction SilentlyContinue
foreach ($id in $loopIds) {
    if ($Here) { Invoke-Loop $id; continue }  # sources one after another in this window
    $cmd = "powershell -NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -RunLoop $id -MaxBatches $MaxBatches"
    if ($wt) { Start-Process wt -ArgumentList "-w mining new-tab -d `"$root`" --title `"$id loop`" $cmd" }
    else { Start-Process powershell -WorkingDirectory $root -ArgumentList '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`"", '-RunLoop', $id }
    Start-Sleep -Seconds 2
}
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
Write-Host "Запущено: сессий $($jobs.Count), циклов $($loopIds.Count)"
