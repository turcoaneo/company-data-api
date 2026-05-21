#.\check-api.ps1 -Domain "company-data-api.<your-domain>"

param(
    [string]$Domain = "company-data-api.cassis.solutions",
    [string]$Bucket = "company-api-bucket"
)

Write-Host "🔍 Checking DNS..."
Resolve-DnsName $Domain -ErrorAction Stop | Out-Null
Write-Host "✅ DNS OK"

Write-Host "🔍 Checking HTTPS..."
Invoke-WebRequest -Uri "https://$Domain" -UseBasicParsing -TimeoutSec 10 | Out-Null
Write-Host "✅ HTTPS reachable"

Write-Host "🔍 Checking /health..."
Invoke-WebRequest -Uri "https://$Domain/health" -UseBasicParsing -TimeoutSec 10 | Out-Null
Write-Host "✅ Health OK"

Write-Host "🔍 Checking ALB target health..."
$tgArn = (aws elbv2 describe-target-groups --names tg-company-api --query "TargetGroups[0].TargetGroupArn" --output text)
$health = (aws elbv2 describe-target-health --target-group-arn $tgArn --query "TargetHealthDescriptions[*].TargetHealth.State" --output text)
if ($health -eq "healthy") { Write-Host "✅ ALB target healthy" } else { Write-Host "❌ ALB unhealthy"; exit 1 }

Write-Host "🔍 Checking ECS task count..."
$running = (aws ecs describe-services --cluster company-data-api-cluster --services company-data-api-service --query "services[0].runningCount" --output text)
if ($running -eq 1) { Write-Host "✅ ECS task running" } else { Write-Host "❌ ECS task count incorrect: $running"; exit 1 }

Write-Host "🔍 Testing S3 write/read..."
$tmp = "C:\Windows\Temp\s3test.txt"
"test $(Get-Date)" | Out-File $tmp
aws s3 cp $tmp "s3://$Bucket/test-object.txt" | Out-Null
aws s3 cp "s3://$Bucket/test-object.txt" - | Out-Null
Write-Host "✅ S3 read/write OK"
Remove-Item $tmp

Write-Host "🔍 Checking MeiliSearch..."
$meili = Invoke-WebRequest -Uri "https://$Domain/meili/health" -UseBasicParsing -TimeoutSec 10
if ($meili.Content -match '"status":"available"') { Write-Host "✅ MeiliSearch OK" } else { Write-Host "❌ MeiliSearch FAILED"; exit 1 }

Write-Host "🎉 All checks passed!"
