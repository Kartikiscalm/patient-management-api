import asyncio
import httpx
import time

# URL of your service (use load balancer IP or local port if port-forwarded)
# If running inside Kubernetes, use the service name
URL = "http://localhost:8000" 
CONCURRENT_REQUESTS = 50  # Number of parallel tasks
TOTAL_SECONDS = 60        # Duration of the test

async def send_request(client):
    try:
        response = await client.get(URL)
        return response.status_code
    except Exception as e:
        return str(e)

async def stress_test():
    print(f"Starting stress test on {URL}...")
    print(f"Concurrent requests: {CONCURRENT_REQUESTS}")
    
    timeout = httpx.Timeout(10.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < TOTAL_SECONDS:
            tasks = [send_request(client) for _ in range(CONCURRENT_REQUESTS)]
            results = await asyncio.gather(*tasks)
            request_count += len(results)
            
            if request_count % 500 == 0:
                elapsed = time.time() - start_time
                rps = request_count / elapsed
                print(f"Sent {request_count} requests... ({rps:.2f} req/s)")
            
            # Small sleep to prevent local socket exhaustion
            await asyncio.sleep(0.01)

    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nFinished! Sent {request_count} requests in {total_time:.2f} seconds.")
    print(f"Average throughput: {request_count / total_time:.2f} req/s")

if __name__ == "__main__":
    try:
        asyncio.run(stress_test())
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
