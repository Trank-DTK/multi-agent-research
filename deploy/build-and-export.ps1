# 本地构建并导出镜像，用于上传到服务器
# 用法（在项目根目录、PowerShell 里执行）：
#     .\deploy\build-and-export.ps1
#     .\deploy\build-and-export.ps1 -SkipFrontend     # 跳过前端构建
#     .\deploy\build-and-export.ps1 -SkipFrontend -SkipImage   # 只打包部署文件

param(
    [switch]$SkipFrontend,
    [switch]$SkipImage
)

$ErrorActionPreference = 'Stop'

# 切到项目根目录（脚本在 deploy/ 下，所以要往上一级）
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "=== 多智能体科研协作平台 · 构建并导出 ===" -ForegroundColor Cyan
Write-Host "项目根目录: $Root"
Write-Host ""

$DistDir = Join-Path $Root 'frontend\dist'
$OutDir  = Join-Path $Root 'deploy\dist-out'

# ---------------------------------------------------------------------------
# 1. 构建前端
# ---------------------------------------------------------------------------
if (-not $SkipFrontend) {
    Write-Host "[1/4] 构建前端..." -ForegroundColor Yellow

    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        throw "找不到 npm，请先安装 Node.js 20+ ：https://nodejs.org/"
    }

    Push-Location (Join-Path $Root 'frontend')
    try {
        if (-not (Test-Path 'node_modules')) {
            Write-Host "      首次运行，安装依赖（可能要几分钟）..."
            npm install
            if ($LASTEXITCODE -ne 0) { throw "npm install 失败" }
        }
        npm run build
        if ($LASTEXITCODE -ne 0) { throw "前端构建失败" }
    } finally {
        Pop-Location
    }

    if (-not (Test-Path (Join-Path $DistDir 'index.html'))) {
        throw "前端构建产物里没有 index.html，构建可能没有真正成功"
    }
    Write-Host "      完成：frontend\dist" -ForegroundColor Green
} else {
    Write-Host "[1/4] 跳过前端构建" -ForegroundColor DarkGray
    if (-not (Test-Path (Join-Path $DistDir 'index.html'))) {
        throw "frontend\dist 不存在或不完整，无法跳过。请先执行一次不带 -SkipFrontend 的构建。"
    }
}

# ---------------------------------------------------------------------------
# 2. 构建后端镜像
# ---------------------------------------------------------------------------
if (-not $SkipImage) {
    Write-Host "[2/4] 构建后端镜像 research-web:prod ..." -ForegroundColor Yellow
    Write-Host "      （首次构建需要下载依赖，可能 10 分钟以上）"

    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        throw "找不到 docker，请先安装并启动 Docker Desktop：https://www.docker.com/products/docker-desktop/"
    }

    docker build -f Dockerfile.prod -t research-web:prod .
    if ($LASTEXITCODE -ne 0) { throw "镜像构建失败" }

    # 顺带把数据库和 Redis 镜像也拉下来，省得在服务器上再拉（服务器拉镜像慢）
    Write-Host "      预拉取数据库与 Redis 镜像..."
    docker pull ankane/pgvector:latest
    docker pull redis:alpine
    docker pull nginx:alpine

    Write-Host "      完成：research-web:prod" -ForegroundColor Green
} else {
    Write-Host "[2/4] 跳过镜像构建" -ForegroundColor DarkGray
}

# ---------------------------------------------------------------------------
# 3. 导出镜像 + 打包部署文件
# ---------------------------------------------------------------------------
Write-Host "[3/4] 导出镜像包..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

if (-not $SkipImage) {
    $ImagesTar = Join-Path $OutDir 'research-images.tar'
    if (Test-Path $ImagesTar) { Remove-Item $ImagesTar -Force }
    docker save -o $ImagesTar research-web:prod ankane/pgvector:latest redis:alpine nginx:alpine
    if ($LASTEXITCODE -ne 0) { throw "docker save 失败" }
    $sizeGB = [math]::Round((Get-Item $ImagesTar).Length / 1GB, 2)
    Write-Host "      完成：research-images.tar（$sizeGB GB）" -ForegroundColor Green
}

# 前端静态文件单独打包，方便单独更新前端时不用重传镜像
Write-Host "      打包前端静态文件..."
$FrontendTar = Join-Path $OutDir 'frontend-dist.tar.gz'
if (Test-Path $FrontendTar) { Remove-Item $FrontendTar -Force }
tar -czf $FrontendTar -C $Root\frontend dist
if ($LASTEXITCODE -ne 0) { throw "前端打包失败" }

Write-Host "[4/4] 打包完成" -ForegroundColor Green
Write-Host ""
Write-Host "产物目录：$OutDir" -ForegroundColor Cyan
Get-ChildItem $OutDir | Select-Object Name, @{N='大小(MB)';E={[math]::Round($_.Length/1MB,1)}} | Format-Table -AutoSize

# ---------------------------------------------------------------------------
# 打印下一步命令
# ---------------------------------------------------------------------------
$ServerIp = '<你的服务器公网IP>'
Write-Host "=== 下一步：把下面 3 个文件上传到服务器 ===" -ForegroundColor Cyan
Write-Host "  deploy\dist-out\research-images.tar"
Write-Host "  deploy\dist-out\frontend-dist.tar.gz"
Write-Host "  docker-compose.prod.yml"
Write-Host ""
Write-Host "在【本机】新开一个终端执行（root 换成你的登录用户）：" -ForegroundColor Yellow
Write-Host @"
  scp deploy\dist-out\research-images.tar   root@${ServerIp}:/root/
  scp deploy\dist-out\frontend-dist.tar.gz  root@${ServerIp}:/root/
  scp docker-compose.prod.yml               root@${ServerIp}:/root/
  scp .env.production                       root@${ServerIp}:/root/
"@
Write-Host ""
Write-Host "还要传 nginx 配置目录（整个 nginx 文件夹）：" -ForegroundColor Yellow
Write-Host "  scp -r nginx root@${ServerIp}:/root/"
Write-Host ""
Write-Host "然后按 docs/DEPLOYMENT.md 第 4 章继续。" -ForegroundColor Cyan
