# .dev/.dev_utils/check_git_status.ps1

function GetSimpleStatusTag($filePath, $source) {
    if ($source -eq "untracked") {
        return "# 신규"
    }

    $args = if ($source -eq "staged") {
        @("diff", "--cached", "--name-status", "--", $filePath)
    } else {
        @("diff", "--name-status", "--", $filePath)
    }

    try {
        $output = git @args | Where-Object { $_ -match "$filePath" }
        if ($output -match "^D") {
            return "# 삭제됨"
        } else {
            return "# 변경됨"
        }
    } catch {
        return "# 상태확인 실패"
    }
}

Write-Output "Git status (uncommitted changes)"

# 변경 사항 수집
$untracked = git ls-files --others --exclude-standard
$modified  = git diff --name-only
$staged    = git diff --cached --name-only

if ($untracked) {
    Write-Output "`nUntracked:"
    foreach ($file in $untracked) {
        $summary = GetSimpleStatusTag $file "untracked"
        Write-Output (" - {0,-40} {1}" -f $file, $summary)
    }
}

if ($modified) {
    Write-Output "`nModified:"
    foreach ($file in $modified) {
        $summary = GetSimpleStatusTag $file "modified"
        Write-Output (" - {0,-40} {1}" -f $file, $summary)
    }
}

if ($staged) {
    Write-Output "`nStaged:"
    foreach ($file in $staged) {
        $summary = GetSimpleStatusTag $file "staged"
        Write-Output (" - {0,-40} {1}" -f $file, $summary)
    }
}

if (-not ($untracked -or $modified -or $staged)) {
    Write-Output "`nClean working tree."
}