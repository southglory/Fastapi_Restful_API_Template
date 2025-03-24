# 캐시 클린 PowerShell 스크립트

Write-Host "▶ .pyc 파일 및 __pycache__ 디렉토리 제거 중..."
Get-ChildItem -Recurse -Include *.pyc,__pycache__ -Path .\ -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "▶ pytest 캐시 제거 중..."
Remove-Item -Recurse -Force .pytest_cache -ErrorAction SilentlyContinue

Write-Host "▶ pip 캐시 정리 중..."
pip cache purge

Write-Host "`n✅ 완료되었습니다."
