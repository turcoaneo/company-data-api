import asyncio
import aiohttp
import csv
import socket
from aiohttp import ClientConnectorError, ClientSSLError

from app.utils.timing_util import elapsed_time

PARALLEL_LIMIT = 50   # good for 1000+ domains


async def try_fetch(session, url, timeout=8):
    """
    Try to fetch a URL and return (ok, reason, html_snippet).
    """
    try:
        async with session.get(url, ssl=False, timeout=timeout) as resp:
            text = await resp.text(errors="ignore")
            snippet = text[:2000]

            if resp.status < 400:
                return True, f"HTTP {resp.status}", snippet

            # Suspicious 403 detection
            if resp.status == 403:
                if "cloudflare" in text.lower():
                    return False, "403 Forbidden (Cloudflare bot protection)", snippet
                if "access denied" in text.lower():
                    return False, "403 Forbidden (Access Denied)", snippet
                return False, "403 Forbidden (Unknown)", snippet

            return False, f"HTTP {resp.status}", snippet

    except ClientSSLError as e:
        return False, f"SSL error: {e}", None
    except ClientConnectorError as e:
        return False, f"Connection error: {e}", None
    except asyncio.TimeoutError:
        return False, "Timeout", None
    except socket.gaierror:
        return False, "DNS resolution failed", None
    except Exception as e:
        return False, f"Other error: {type(e).__name__}: {e}", None


async def domain_test(domain: str, sem: asyncio.Semaphore):
    """
    Test HTTPS first, then HTTP, with detailed diagnostics.
    """
    async with sem:
        domain = domain.replace("https://", "").replace("http://", "").rstrip("/")
        https_url = f"https://{domain}"
        http_url = f"http://{domain}"

        async with aiohttp.ClientSession() as session:
            ok_https, reason_https, snippet_https = await try_fetch(session, https_url)
            if ok_https:
                return {
                    "domain": domain,
                    "status": "reachable",
                    "protocol": "https",
                    "reason": reason_https,
                    "snippet": snippet_https,
                }

            ok_http, reason_http, snippet_http = await try_fetch(session, http_url)
            if ok_http:
                return {
                    "domain": domain,
                    "status": "reachable",
                    "protocol": "http",
                    "reason": reason_http,
                    "snippet": snippet_http,
                }

            return {
                "domain": domain,
                "status": "unreachable",
                "protocol": None,
                "reason": f"HTTPS: {reason_https} | HTTP: {reason_http}",
                "snippet": snippet_https or snippet_http,
            }


@elapsed_time("qa_bad_urls")
async def run_bad_urls_check(path="../bad_urls.txt", csv_out="bad_urls_report.csv"):
    with open(path, "r", encoding="utf-8") as f:
        domains = [line.strip() for line in f if line.strip()]

    print(f"\nTesting {len(domains)} domains from bad_urls.txt...\n")

    sem = asyncio.Semaphore(PARALLEL_LIMIT)
    tasks = [domain_test(d, sem) for d in domains]
    results = await asyncio.gather(*tasks)

    # CSV export
    with open(csv_out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["domain", "status", "protocol", "reason"])
        writer.writeheader()
        for r in results:
            writer.writerow({
                "domain": r["domain"],
                "status": r["status"],
                "protocol": r["protocol"],
                "reason": r["reason"],
            })

    print(f"CSV report written to {csv_out}")

    return results


if __name__ == "__main__":
    asyncio.run(run_bad_urls_check())
