import os
import socket
import tempfile

import boto3
import requests

DOMAIN = "company-data-api.cassis.solutions"
BUCKET = "company-api-bucket"

elb = boto3.client("elbv2")
ecs = boto3.client("ecs")
s3 = boto3.client("s3")

print("🔍 Checking DNS...")
socket.gethostbyname(DOMAIN)
print("✅ DNS OK")

print("🔍 Checking HTTPS...")
requests.get(f"https://{DOMAIN}", timeout=5)
print("✅ HTTPS reachable")

print("🔍 Checking /health...")
r = requests.get(f"https://{DOMAIN}/health", timeout=5)
assert r.status_code == 200
print("✅ Health OK")

print("🔍 Checking ALB target health...")
tg_arn = elb.describe_target_groups(Names=["tg-company-api"])["TargetGroups"][0]["TargetGroupArn"]
health = elb.describe_target_health(TargetGroupArn=tg_arn)["TargetHealthDescriptions"][0]["TargetHealth"]["State"]
assert health == "healthy"
print("✅ ALB target healthy")

print("🔍 Checking ECS task count...")
service = ecs.describe_services(cluster="company-data-api-cluster", services=["company-data-api-service"])
assert service["services"][0]["runningCount"] == 1
print("✅ ECS task running")

print("🔍 Testing S3 write/read...")
with tempfile.NamedTemporaryFile(delete=False) as tmp:
    tmp.write(b"test")
    tmp_path = tmp.name

s3.upload_file(tmp_path, BUCKET, "test-object.txt")
s3.download_file(BUCKET, "test-object.txt", tmp_path)
print("✅ S3 read/write OK")
os.remove(tmp_path)

print("🔍 Checking MeiliSearch...")
m = requests.get(f"https://{DOMAIN}/meili/health", timeout=5)
assert '"status":"available"' in m.text
print("✅ MeiliSearch OK")

print("🎉 All checks passed!")
