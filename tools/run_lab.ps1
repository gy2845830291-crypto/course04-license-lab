# 第四课靶场一键实验脚本（Windows）
# 前置: apktool / apksigner 在 PATH, JAVA_HOME 指向 JDK17

param(
    [string]$Apk = "Android逆向课程第四课_授权靶场.apk",
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
$Work = "C:\lab\course04-license-lab"
$Out  = Join-Path $Work "build\lab\out"
$Patched = Join-Path $Work "build\lab\patched.apk"

Write-Host "[1/5] 反编译" -ForegroundColor Cyan
if (Test-Path $Out) { Remove-Item $Out -Recurse -Force }
apktool d $Apk -o $Out -f
if ($LASTEXITCODE -ne 0) { throw "apktool 反编译失败" }

Write-Host "[2/5] 定位校验入口" -ForegroundColor Cyan
$smali = Join-Path $Out "smali\edu\lab\rev\course04"
Get-ChildItem $smali -Filter "*.smali" | Select-Object -ExpandProperty Name
Write-Host "--- 字符串锚点 ---" -ForegroundColor Yellow
Select-String -Path (Join-Path $smali "*") -Pattern "LAB4" | Select-Object -First 5

Write-Host "[3/5] 还原算法 -> 生成卡密" -ForegroundColor Cyan
python (Join-Path $Work "tools\keygen.py") gen 4242 365 0x5

Write-Host "[4/5] patch 判定分支" -ForegroundColor Cyan
python (Join-Path $Work "tools\patch_smali.py") $Out

Write-Host "[5/5] 回编译 + 签名" -ForegroundColor Cyan
apktool b $Out -o $Patched
if ($LASTEXITCODE -ne 0) { throw "apktool 回编译失败" }

$ks = Join-Path $Work "build\lab\lab.keystore"
if (-not (Test-Path $ks)) {
    keytool -genkeypair -v -keystore $ks -alias labkey -keyalg RSA -keysize 2048 `
        -validity 10950 -storepass labpass -keypass labpass `
        -dname "CN=Course04 Lab, OU=Lab, O=Course, L=Lab, S=Lab, C=CN"
}
apksigner sign --ks $ks --ks-key-alias labkey --ks-pass pass:labpass --key-pass pass:labpass $Patched
if ($LASTEXITCODE -ne 0) { throw "签名失败" }

Write-Host "完成: $Patched" -ForegroundColor Green
