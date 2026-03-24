import dns.resolver
import csv
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dns.resolver import NoAnswer, NXDOMAIN, Timeout

def get_mx_records(domain: str):
    """Query MX records for a single domain"""
    domain = domain.strip().lower()
    if not domain or domain.startswith('#'):  # Skip empty lines and comments
        return None
    
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 4
        resolver.lifetime = 10
        
        # Optional: Use public DNS servers for better stability
        # resolver.nameservers = ['8.8.8.8', '1.1.1.1']
        
        answers = resolver.resolve(domain, 'MX')
        
        mx_list = []
        for rdata in answers:
            pref = rdata.preference
            server = str(rdata.exchange).rstrip('.')
            mx_list.append((pref, server))
        
        mx_list.sort()  # Sort by priority
        return domain, mx_list, None
    
    except NXDOMAIN:
        return domain, None, "Domain does not exist (NXDOMAIN)"
    except NoAnswer:
        return domain, None, "No MX records found"
    except Timeout:
        return domain, None, "Query timeout"
    except Exception as e:
        return domain, None, f"Error: {e}"


def batch_query_mx_from_file(file_path: str, max_workers: int = 40, output_csv: str = "mx_results.csv"):
    """Read domains from text file and query MX records in batch"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            domains = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    print(f"✅ Loaded {len(domains)} domains, starting concurrent query...\n")
    
    start_time = time.time()
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_domain = {executor.submit(get_mx_records, d): d for d in domains}
        
        for future in as_completed(future_to_domain):
            result = future.result()
            if result:
                domain, mx_list, error = result
                if mx_list:
                    mx_str = " | ".join([f"{pref}:{server}" for pref, server in mx_list])
                    print(f"✅ {domain:30} → {mx_str}")
                else:
                    print(f"⚠️  {domain:30} → {error}")
                results.append((domain, mx_list, error))
    
    # Save results to CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Domain', 'MX Records', 'Status/Error'])
        
        for domain, mx_list, error in results:
            if mx_list:
                mx_str = " | ".join([f"{pref}:{server}" for pref, server in mx_list])
                writer.writerow([domain, mx_str, "Success"])
            else:
                writer.writerow([domain, "", error])
    
    elapsed = time.time() - start_time
    print(f"\n🎉 Query completed! Processed {len(domains)} domains in {elapsed:.2f} seconds")
    print(f"📁 Results saved to: {output_csv}")


# ====================== Main Program ======================
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Support command line: python mx_batch.py domains.txt
        file_path = sys.argv[1]
    else:
        file_path = input("Please enter the domain list file path (e.g. domains.txt): ").strip()
        if not file_path:
            file_path = "domains.txt"   # Default filename
    
    # You can adjust the number of concurrent workers based on your network
    batch_query_mx_from_file(
        file_path=file_path,
        max_workers=40,
        output_csv="mx_results.csv"
    )
