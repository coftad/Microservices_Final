import csv
from pathlib import Path
from collections import defaultdict

def analyze_load_test_results():
    """Analyze CSV results from Locust tests without pandas"""
    
    reports_dir = Path("reports")
    test_scenarios = ["light_load", "medium_load", "high_load"]
    
    print("\n" + "="*80)
    print("📊 LOAD TEST PERFORMANCE ANALYSIS")
    print("="*80 + "\n")
    
    all_stats = []
    
    for scenario in test_scenarios:
        stats_file = reports_dir / f"{scenario}_stats.csv"
        
        if not stats_file.exists():
            print(f"⚠️  {scenario} results not found, skipping...")
            continue
        
        # Read stats
        with open(stats_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        print(f"\n{'='*60}")
        print(f"📈 {scenario.upper().replace('_', ' ')}")
        print(f"{'='*60}")
        
        # Find aggregated row
        agg_row = None
        endpoint_rows = []
        
        for row in rows:
            if row['Name'] == 'Aggregated':
                agg_row = row
            else:
                endpoint_rows.append(row)
        
        # Print endpoint stats
        if endpoint_rows:
            print(f"\n{'Endpoint':<40} {'Requests':<12} {'Avg (ms)':<12} {'P95 (ms)':<12} {'Fail %':<10}")
            print("-" * 90)
            
            for row in endpoint_rows:
                try:
                    req_count = int(row['Request Count'])
                    fail_count = int(row['Failure Count'])
                    fail_rate = (fail_count / req_count * 100) if req_count > 0 else 0
                    avg_time = float(row['Average Response Time'])
                    p95_time = float(row['95%'])
                    
                    print(f"{row['Name']:<40} {req_count:<12} "
                          f"{avg_time:<12.2f} "
                          f"{p95_time:<12.2f} "
                          f"{fail_rate:<10.2f}%")
                except (ValueError, KeyError) as e:
                    continue
        
        # Print aggregated summary
        if agg_row:
            try:
                total_req = int(agg_row['Request Count'])
                total_fail = int(agg_row['Failure Count'])
                rps = float(agg_row['Requests/s'])
                avg_time = float(agg_row['Average Response Time'])
                p95_time = float(agg_row['95%'])
                p99_time = float(agg_row['99%'])
                success_rate = ((total_req - total_fail) / total_req * 100) if total_req > 0 else 0
                
                print(f"\n📊 Summary:")
                print(f"   Total Requests: {total_req}")
                print(f"   Failed Requests: {total_fail}")
                print(f"   Success Rate: {success_rate:.2f}%")
                print(f"   Requests/sec: {rps:.2f}")
                print(f"   Avg Response Time: {avg_time:.2f}ms")
                print(f"   P95 Response Time: {p95_time:.2f}ms")
                print(f"   P99 Response Time: {p99_time:.2f}ms")
                
                all_stats.append({
                    'scenario': scenario,
                    'total_requests': total_req,
                    'rps': rps,
                    'avg_latency': avg_time,
                    'p95_latency': p95_time,
                    'p99_latency': p99_time,
                    'success_rate': success_rate
                })
            except (ValueError, KeyError) as e:
                print(f"⚠️  Could not parse aggregated stats: {e}")
    
    # Print comparison
    if len(all_stats) > 1:
        print("\n" + "="*80)
        print("📊 SCALABILITY COMPARISON")
        print("="*80 + "\n")
        
        print(f"{'Scenario':<20} {'Requests':<12} {'RPS':<12} {'Avg (ms)':<12} {'P95 (ms)':<12} {'Success %':<12}")
        print("-" * 90)
        
        for stat in all_stats:
            print(f"{stat['scenario']:<20} {stat['total_requests']:<12} "
                  f"{stat['rps']:<12.2f} "
                  f"{stat['avg_latency']:<12.2f} "
                  f"{stat['p95_latency']:<12.2f} "
                  f"{stat['success_rate']:<12.2f}")
        
        # Scalability insights
        print(f"\n🎯 Scalability Insights:")
        light = all_stats[0]
        heavy = all_stats[2] if len(all_stats) > 2 else all_stats[-1]
        
        print(f"   • Light Load: {light['rps']:.2f} req/s @ {light['avg_latency']:.2f}ms avg")
        print(f"   • Heavy Load: {heavy['rps']:.2f} req/s @ {heavy['avg_latency']:.2f}ms avg")
        
        throughput_increase = ((heavy['rps'] / light['rps']) - 1) * 100
        latency_increase = ((heavy['avg_latency'] / light['avg_latency']) - 1) * 100
        
        print(f"   • Throughput increased by {throughput_increase:.1f}%")
        print(f"   • Latency increased by {latency_increase:.1f}%")
        
        if throughput_increase > 50 and latency_increase < 100:
            print(f"   ✅ System demonstrates good horizontal scalability!")
        elif latency_increase > 200:
            print(f"   ⚠️  System shows signs of bottlenecks under heavy load")
        else:
            print(f"   ℹ️  System scales linearly with load")

if __name__ == "__main__":
    analyze_load_test_results()