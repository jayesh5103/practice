#!/usr/bin/env python3
"""
smoke_check.py

A small script that fires concurrent requests to /api/review using httpx.AsyncClient.
Measures wall-clock time, average/max latency, and checks for event loop blocking by
comparing concurrent fallback latencies against a single fallback latency.
"""

import asyncio
import time
import sys
import argparse
from typing import List, Dict, Any
import httpx

# Snippets used for tests
AI_SNIPPET = """
def calculate_sum(items):
    \"\"\"Calculate the sum of all items in a list.\"\"\"
    total = 0
    for item in items:
        total += item
    return total
"""

FALLBACK_SNIPPET = """
# TRIGGER_FALLBACK
def format_user_message(username, message):
    res = f"[{username}]: {message}"
    return res
"""

ERROR_SNIPPET = """
# TRIGGER_500
def broken_function():
    return 1 / 0
"""

async def send_request(client: httpx.AsyncClient, url: str, code: str, language: str) -> Dict[str, Any]:
    """
    Send a single POST request to /api/review and measure latency.
    """
    payload = {"code": code, "language": language}
    start_time = time.perf_counter()
    
    try:
        response = await client.post(url, json=payload, timeout=30.0)
        end_time = time.perf_counter()
        latency = end_time - start_time
        
        status_code = response.status_code
        try:
            data = response.json()
            source = data.get("source", "unknown")
            issues_count = len(data.get("issues", []))
        except Exception:
            source = "unknown"
            issues_count = 0
            
        return {
            "success": status_code == 200,
            "status_code": status_code,
            "latency": latency,
            "source": source,
            "issues_count": issues_count,
            "error": None
        }
    except Exception as e:
        end_time = time.perf_counter()
        return {
            "success": False,
            "status_code": 0,
            "latency": end_time - start_time,
            "source": "error",
            "issues_count": 0,
            "error": str(e)
        }

async def run_single_fallback(url: str) -> Dict[str, Any]:
    """
    Run a single fallback request to establish a baseline.
    """
    async with httpx.AsyncClient() as client:
        print("Running single fallback request to establish baseline...")
        result = await send_request(client, url, FALLBACK_SNIPPET, "python")
        print(f"Single fallback request completed: status={result['status_code']}, latency={result['latency']:.4f}s, source={result['source']}")
        return result

async def run_concurrent_fallback(url: str, count: int) -> List[Dict[str, Any]]:
    """
    Run several concurrent fallback requests to check for event loop blocking.
    """
    async with httpx.AsyncClient() as client:
        print(f"\nRunning {count} concurrent fallback requests...")
        start_time = time.perf_counter()
        tasks = [send_request(client, url, FALLBACK_SNIPPET, "python") for _ in range(count)]
        results = await asyncio.gather(*tasks)
        total_time = time.perf_counter() - start_time
        
        latencies = [r["latency"] for r in results]
        success_count = sum(1 for r in results if r["success"])
        sources = [r["source"] for r in results]
        
        print(f"Finished {count} concurrent fallback requests in {total_time:.4f}s")
        print(f"Success rate: {success_count}/{count}")
        print(f"Latencies: min={min(latencies):.4f}s, max={max(latencies):.4f}s, avg={sum(latencies)/len(latencies):.4f}s")
        print(f"Sources returned: {dict((x, sources.count(x)) for x in set(sources))}")
        
        return results, total_time

async def run_mixed_batch(url: str) -> List[Dict[str, Any]]:
    """
    Run a mixed batch of requests containing AI path, fallback path, and error path.
    """
    # 8 AI, 8 Fallback, 2 Error = 18 requests
    requests_to_run = (
        [(AI_SNIPPET, "python")] * 8 +
        [(FALLBACK_SNIPPET, "python")] * 8 +
        [(ERROR_SNIPPET, "python")] * 2
    )
    
    async with httpx.AsyncClient() as client:
        print(f"\nRunning mixed batch of {len(requests_to_run)} concurrent requests (8 AI, 8 Fallback, 2 Error)...")
        start_time = time.perf_counter()
        tasks = [send_request(client, url, code, lang) for code, lang in requests_to_run]
        results = await asyncio.gather(*tasks)
        total_time = time.perf_counter() - start_time
        
        latencies = [r["latency"] for r in results]
        success_count = sum(1 for r in results if r["success"])
        sources = [r["source"] for r in results]
        status_codes = [r["status_code"] for r in results]
        
        print(f"Finished mixed batch in {total_time:.4f}s")
        print(f"Success rate (should be 16/18): {success_count}/{len(results)}")
        print(f"Latencies: min={min(latencies):.4f}s, max={max(latencies):.4f}s, avg={sum(latencies)/len(latencies):.4f}s")
        print(f"Sources returned: {dict((x, sources.count(x)) for x in set(sources))}")
        print(f"Status codes returned: {dict((x, status_codes.count(x)) for x in set(status_codes))}")
        
        return results, total_time

async def main():
    parser = argparse.ArgumentParser(description="Run a concurrency smoke check against FastAPI backend.")
    parser.add_argument("--url", default="http://localhost:8000/api/review", help="Full API review URL")
    parser.add_argument("--count", type=int, default=10, help="Number of concurrent requests for fallback test")
    args = parser.parse_args()
    
    url = args.url
    print(f"Smoke Check Target: {url}")
    
    # 1. Single baseline
    single_res = await run_single_fallback(url)
    single_latency = single_res["latency"]
    
    # 2. Concurrent fallback
    _, concurrent_fallback_time = await run_concurrent_fallback(url, args.count)
    
    # Analyze blocking factor
    expected_if_serialized = single_latency * args.count
    ratio = concurrent_fallback_time / single_latency
    
    print("\n--- Concurrency / Event Loop Analysis ---")
    print(f"Single fallback latency: {single_latency:.4f}s")
    print(f"Time for {args.count} concurrent fallbacks: {concurrent_fallback_time:.4f}s")
    print(f"Theoretical serialized time: {expected_if_serialized:.4f}s")
    print(f"Speedup vs Serialized: {expected_if_serialized / concurrent_fallback_time:.2f}x")
    print(f"Ratio (Concurrent Time / Single Time): {ratio:.2f}x")
    
    if ratio > args.count * 0.8:
        print("\n[WARNING] Serialization detected! Concurrent requests took roughly N times longer than a single request.")
        print("This indicates that the FastAPI event loop is blocked on a synchronous operation.")
    else:
        print("\n[OK] Request concurrency is functioning. The event loop is NOT blocked.")
        
    # 3. Mixed batch (rate limits check, 500 checking)
    await run_mixed_batch(url)

if __name__ == "__main__":
    asyncio.run(main())
