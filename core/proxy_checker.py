import concurrent.futures
import requests
import os
from typing import List, Tuple
from core.platforms import ProxyManager

DEFAULT_TEST_URL = "https://httpbin.org/ip"


def load_proxies(path: str = "proxies.txt") -> List[str]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]


def build_proxies(proxy: str) -> dict:
    p = proxy.strip()
    if p.startswith("http://") or p.startswith("https://") or p.startswith("socks"):
        scheme_host = p
    else:
        scheme_host = f"http://{p}"
    return {"http": scheme_host, "https": scheme_host}


def check_proxy(proxy: str, test_url: str = DEFAULT_TEST_URL, timeout: int = 8) -> Tuple[str, bool, str]:
    proxies = build_proxies(proxy)
    try:
        resp = requests.get(test_url, proxies=proxies, timeout=timeout)
        if resp.status_code == 200:
            return proxy, True, resp.text.strip()
        return proxy, False, f"status:{resp.status_code}"
    except Exception as e:
        return proxy, False, str(e)


def check_proxies(proxies: List[str], workers: int = 10, test_url: str = DEFAULT_TEST_URL, timeout: int = 8) -> List[Tuple[str, bool, str]]:
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(workers, max(1, len(proxies)))) as ex:
        futures = {ex.submit(check_proxy, p, test_url, timeout): p for p in proxies}
        for fut in concurrent.futures.as_completed(futures):
            try:
                results.append(fut.result())
            except Exception as e:
                p = futures.get(fut, "unknown")
                results.append((p, False, str(e)))
    pm = ProxyManager()
    for proxy, ok, _ in results:
        if ok:
            if pm.is_blacklisted(proxy):
                pm.unmark_bad_proxy(proxy)
        else:
            pm.mark_bad_proxy(proxy)
    return results


def save_results(results: List[Tuple[str, bool, str]], good_path: str = "good_proxies.txt", bad_path: str = "bad_proxies.txt"):
    good = [p for p, ok, _ in results if ok]
    bad = [p for p, ok, _ in results if not ok]
    if good:
        with open(good_path, "w", encoding="utf-8") as f:
            f.write("\n".join(good))
    if bad:
        with open(bad_path, "w", encoding="utf-8") as f:
            f.write("\n".join(bad))


def print_summary(results: List[Tuple[str, bool, str]]):
    ok = [r for r in results if r[1]]
    fail = [r for r in results if not r[1]]
    print(f"Checked: {len(results)} - OK: {len(ok)} - FAIL: {len(fail)}")
    if ok:
        print("\nGood proxies:")
        for p, _, info in ok:
            print(f"  {p} -> {info}")
    if fail:
        print("\nBad proxies:")
        for p, _, info in fail:
            print(f"  {p} -> {info}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Check proxies listed in proxies.txt")
    parser.add_argument("--file", "-f", default="proxies.txt", help="Path to proxies file (one per line)")
    parser.add_argument("--workers", "-w", type=int, default=20, help="Number of concurrent workers")
    parser.add_argument("--test-url", "-u", default=DEFAULT_TEST_URL, help="URL to test through proxy")
    parser.add_argument("--timeout", "-t", type=int, default=8, help="Timeout seconds for each test")
    args = parser.parse_args()

    proxies = load_proxies(args.file)
    if not proxies:
        print(f"No proxies found in {args.file}")
        raise SystemExit(1)

    print(f"Testing {len(proxies)} proxies against {args.test_url} with {args.workers} workers...")
    results = check_proxies(proxies, workers=args.workers, test_url=args.test_url, timeout=args.timeout)
    print_summary(results)
    save_results(results)
    print("Saved good_proxies.txt and bad_proxies.txt")

    print(f"Testing {len(proxies)} proxies against {args.test_url} with {args.workers} workers...")
    results = check_proxies(proxies, workers=args.workers, test_url=args.test_url, timeout=args.timeout)
    print_summary(results)
    save_results(results)
    print("Saved good_proxies.txt and bad_proxies.txt")
