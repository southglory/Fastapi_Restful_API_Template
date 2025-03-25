param (
    [string]$Title,
    [string]$Content,
    [string[]]$List,
    [int]$Recent = 0,
    [switch]$MarkCommitted,
    [switch]$ShowUncommitted
)

$logPath = "$PSScriptRoot\..\log.txt"

function Show-RecentLogs($count) {
    if (Test-Path $logPath) {
        $lines = Get-Content -Path $logPath -Encoding utf8
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

# 🔹 커밋 마크 모드 (단순히 마지막에 추가)
if ($MarkCommitted) {
    if (Test-Path $logPath) {
        Add-Content -Path $logPath -Value '----------- committed -----------' -Encoding utf8
        Write-Output "✅ 마지막에 커밋 마크를 추가했습니다."
    } else {
        Write-Output "⚠️ 로그 파일이 존재하지 않습니다."
    }
    exit 0
}
 elseif ($PSBoundParameters.ContainsKey("ShowUncommitted")) {
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

# Content 파라미터가 있으면 내용 추가
if (-not [string]::IsNullOrWhiteSpace($Content)) {
    $logEntry += $Content
}

if ($List) {
    foreach ($item in $List) {
        $logEntry += "- $item"
    }
}

# UTF-8 인코딩으로 로그 파일에 저장
Add-Content -Path $logPath -Value $logEntry -Encoding utf8

# 콘솔 출력 인코딩 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Write-Output "📌 로그 작성 완료:"
Write-Output ($logEntry -join "`n")
