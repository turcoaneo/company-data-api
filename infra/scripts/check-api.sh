#!/bin/bash
set -e

DOMAIN="company-data-api.cassis.solutions"
BUCKET="company-api-bucket"
MEILI_URL="https://$DOMAIN/meili/health"
TMPFILE="/tmp/s3_test_$$.txt"

echo "🔍 Checking DNS..."
dig +short "$DOMAIN" > /dev/null && echo "✅ DNS OK"

echo "🔍 Checking HTTPS..."
curl -s --head "https://$DOMAIN" | grep "200" > /dev/null && echo "✅ HTTPS reachable"

echo "🔍 Checking /health..."
curl -s --head "https://$DOMAIN/health" | grep "200" > /dev/null && echo "✅ Health OK"

echo "🔍 Checking ALB target health..."
aws elbv2 describe-target-health \
  --target-group-arn "$(aws elbv2 describe-target-groups --names tg-company-api --query 'TargetGroups[0].TargetGroupArn' --output text)" \
  --query 'TargetHealthDescriptions[*].TargetHealth.State' \
  --output text | grep "healthy" > /dev/null && echo "✅ ALB target healthy"

echo "🔍 Checking ECS task count..."
RUNNING=$(aws ecs describe-services \
  --cluster company-data-api-cluster \
  --services company-data-api-service \
  --query 'services[0].runningCount' \
  --output text)

if [[ "$RUNNING" -eq 1 ]]; then
  echo "✅ ECS task running"
else
  echo "❌ ECS task count incorrect: $RUNNING"
  exit 1
fi

echo "🔍 Testing S3 write/read..."
echo "test-$(date)" > "$TMPFILE"
aws s3 cp "$TMPFILE" "s3://$BUCKET/test-object.txt" > /dev/null
aws s3 cp "s3://$BUCKET/test-object.txt" - > /dev/null && echo "✅ S3 read/write OK"
rm "$TMPFILE"

echo "🔍 Checking MeiliSearch..."
curl -s "$MEILI_URL" | grep '"status":"available"' > /dev/null && echo "✅ MeiliSearch OK"

echo "🎉 All checks passed!"
