param (
    [string]$Title,
    [string[]]$List,
    [int]$Recent = 0,
    [switch]$MarkCommitted,
    [switch]$ShowUncommitted
)

$logPath = "$PSScriptRoot\..\log.txt"

function Show-RecentLogs($count) {
    if (Test-Path $logPath) {
        $lines = Get-Content -Path $logPath
        $entries = @()
        $entry = @()

        foreach ($line in $lines) {
            if ($line -match '^\d{4}-\d{2}-\d{2} \(\d{2}:\d{2}\)') {
                if ($entry.Count -gt 0) {
                    $entries += ,@($entry)
                    $entry = @()
                }
            }
            $entry += $line
        }
        if ($entry.Count -gt 0) {
            $entries += ,@($entry)
        }

        if ($entries.Count -eq 0) {
            Write-Output "⚠️ 로그 항목이 없습니다."
        } else {
            Write-Output "📄 최근 로그 ${count}개:"
            $entries | Select-Object -Last $count | ForEach-Object {
                "`n" + ($_ -join "`n")
            }
        }
    } else {
        Write-Output "⚠️ 로그 파일이 존재하지 않습니다: $logPath"
    }
}

# 🔹 커밋 마크 모드
if ($MarkCommitted) {
    if (Test-Path $logPath) {
        $lines = Get-Content $logPath
        $lastLogStart = -1

        # 1. 마지막 로그 블럭 시작 위치 찾기
        for ($i = $lines.Count - 1; $i -ge 0; $i--) {
            if ($lines[$i] -match '^\d{4}-\d{2}-\d{2} \(\d{2}:\d{2}\)') {
                $lastLogStart = $i
                break
            }
        }

        if ($lastLogStart -eq -1) {
            Write-Output "❌ 로그 블럭을 찾을 수 없습니다."
            exit 1
        }

        # 2. 해당 블럭 안에 이미 committed 라인이 있는지 검사
        for ($i = $lastLogStart; $i -lt $lines.Count; $i++) {
            if ($lines[$i] -eq '----------- committed -----------') {
                Write-Output "✅ 이미 커밋됨 표시가 있습니다."
                exit 0
            }
            if ($lines[$i] -match '^\d{4}-\d{2}-\d{2} \(\d{2}:\d{2}\)' -and $i -ne $lastLogStart) {
                break  # 다음 로그 시작되면 종료
            }
        }

        # 3. 커밋 마크를 블럭 끝에 삽입
        $insertIndex = $lines.Count
        for ($i = $lastLogStart + 1; $i -lt $lines.Count; $i++) {
            if ($lines[$i] -match '^\d{4}-\d{2}-\d{2} \(\d{2}:\d{2}\)') {
                $insertIndex = $i
                break
            }
        }

        $before = $lines[0..($insertIndex - 1)]
        $after = if ($insertIndex -lt $lines.Count) { $lines[$insertIndex..($lines.Count - 1)] } else { @() }

        $newLines = $before + '----------- committed -----------' + $after
        Set-Content -Path $logPath -Value $newLines
        Write-Output "✅ 커밋 표시 추가 완료."
    } else {
        Write-Output "⚠️ 로그 파일이 존재하지 않습니다."
    }
    exit 0
} elseif ($PSBoundParameters.ContainsKey("ShowUncommitted")) {
    if (-not (Test-Path $logPath)) {
        Write-Output "⚠️ 로그 파일이 존재하지 않습니다."
        exit 0
    }

    $lines = Get-Content $logPath
    $entries = @()
    $entry = @()
    $seenCommitted = $false

    for ($i = $lines.Count - 1; $i -ge 0; $i--) {
        $line = $lines[$i]

        if ($line -eq '----------- committed -----------') {
            $seenCommitted = $true
            continue
        }

        if ($line -match '^\d{4}-\d{2}-\d{2} \(\d{2}:\d{2}\)') {
            $entry = ,$line + $entry  # 앞에 추가
            if (-not $seenCommitted) {
                $entries = ,$entry + $entries  # entries도 앞에 추가
            }
            $entry = @()
        } else {
            $entry = ,$line + $entry
        }
    }

    if ($entry.Count -gt 0 -and -not $seenCommitted) {
        $entries = ,$entry + $entries
    }

    if ($entries.Count -eq 0) {
        Write-Output "✅ 커밋 안된 로그가 없습니다."
    } else {
        Write-Output "📄 커밋 안된 로그 블럭들:"
        $entries | ForEach-Object {
            "`n" + ($_ -join "`n")
        }
    }

    exit 0
}




# 🔹 최근 로그 조회 모드
if ([string]::IsNullOrWhiteSpace($Title) -and $Recent -gt 0) {
    Show-RecentLogs -count $Recent
    exit 0
}
if ([string]::IsNullOrWhiteSpace($Title)) {
    Show-RecentLogs -count 2
    exit 0
}

# 🔹 로그 작성 모드
$timestamp = Get-Date -Format "yyyy-MM-dd (HH:mm)"
$logEntry = @("$timestamp $Title")

if ($List) {
    foreach ($item in $List) {
        $logEntry += "- $item"
    }
}

Add-Content -Path $logPath -Value $logEntry
Write-Output "📌 로그 작성 완료:"
Write-Output ($logEntry -join "`n")
