from locust import HttpUser, task, between, events
import random
import string
import time

class URLShortenerUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://159.223.136.60"  # Replace with your server IP
    
    # Initialize at class level to prevent AttributeError
    token = None
    headers = {}
    short_codes = []
    
    def on_start(self):
        """Register and login before starting tasks"""
        # Reset instance variables
        self.token = None
        self.headers = {}
        self.short_codes = []
        
        # Generate unique user data
        username = f"user{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
        email = f"{username}@test.com"
        password = "TestPass123!"
        
        try:
            # 1. REGISTER (JSON format)
            register_response = self.client.post(
                ":8001/auth/register",
                json={
                    "email": email,
                    "password": password
                },
                name="/auth/register",
                timeout=15  # Add timeout
            )
            
            if register_response.status_code != 200:
                print(f"❌ Registration failed: {register_response.status_code}")
                return
            
            # 2. LOGIN (Form data, username field = EMAIL)
            login_response = self.client.post(
                ":8001/auth/login",
                data={
                    "username": email,
                    "password": password
                },
                name="/auth/login",
                timeout=15  # Add timeout
            )
            
            if login_response.status_code == 200:
                self.token = login_response.json()["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
                print(f"✅ User logged in: {email}")
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            self.token = None
            self.headers = {}
    
    @task(5)
    def create_short_url(self):
        """Create a shortened URL (requires auth)"""
        if not self.token:
            return
        
        original_url = f"https://example.com/page/{random.randint(1, 10000)}"
        
        try:
            response = self.client.post(
                ":8000/shorten",
                json={"original_url": original_url},
                headers=self.headers,
                name="/shorten",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                short_url = data.get("short_url", "")
                short_code = short_url.split("/")[-1]
                if short_code:
                    self.short_codes.append(short_code)
        except Exception as e:
            print(f"❌ Shorten failed: {e}")
    
    @task(10)
    def redirect_short_url(self):
        """Access a shortened URL - redirect (no auth required)"""
        # Safe check with getattr
        if not getattr(self, 'short_codes', None):
            return
        
        if not self.short_codes:
            return
        
        try:
            short_code = random.choice(self.short_codes)
            
            self.client.get(
                f":8000/{short_code}",
                name="/{short_code} (redirect)",
                allow_redirects=False,
                timeout=10
            )
        except Exception as e:
            pass  # Expected to fail if short_codes is empty
    
    @task(2)
    def verify_token(self):
        """Verify JWT token"""
        if not self.token:
            return
        
        try:
            self.client.get(
                ":8001/auth/me",
                headers=self.headers,
                name="/auth/me",
                timeout=10
            )
        except Exception as e:
            pass


# Event listeners for detailed reporting
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Log requests - only errors and slow requests"""
    if exception:
        print(f"❌ {request_type} {name} failed: {exception}")
    elif response_time > 5000:  # Log very slow requests (>5s)
        print(f"⚠️  SLOW: {request_type} {name}: {response_time:.0f}ms")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts"""
    print("\n" + "="*60)
    print("🚀 LOAD TEST STARTED")
    print("="*60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Generate performance report when test stops"""
    print("\n" + "="*60)
    print("📊 PERFORMANCE REPORT")
    print("="*60)
    
    stats = environment.stats
    
    print("\n📈 Response Time Statistics:")
    print(f"{'Endpoint':<40} {'# Reqs':<10} {'Failures':<10} {'Avg (ms)':<12} {'Min (ms)':<12} {'Max (ms)':<12} {'P95':<10}")
    print("-" * 120)
    
    for entry in stats.entries.values():
        fail_pct = (entry.num_failures / entry.num_requests * 100) if entry.num_requests > 0 else 0
        print(f"{entry.name:<40} {entry.num_requests:<10} {entry.num_failures} ({fail_pct:.1f}%){'':<3} "
              f"{entry.avg_response_time:<12.2f} "
              f"{entry.min_response_time:<12.2f} "
              f"{entry.max_response_time:<12.2f} "
              f"{entry.get_response_time_percentile(0.95):<10.2f}")
    
    print("\n📊 Overall Statistics:")
    if stats.total.num_requests > 0:
        success_rate = ((stats.total.num_requests - stats.total.num_failures) / stats.total.num_requests * 100)
        print(f"Total Requests: {stats.total.num_requests}")
        print(f"Failed Requests: {stats.total.num_failures}")
        print(f"Success Rate: {success_rate:.2f}%")
        print(f"Requests/sec: {stats.total.current_rps:.2f}")
        print(f"Average Response Time: {stats.total.avg_response_time:.2f}ms")
        print(f"Median Response Time: {stats.total.get_response_time_percentile(0.5):.2f}ms")
        print(f"95th Percentile: {stats.total.get_response_time_percentile(0.95):.2f}ms")
        
        # Performance insights
        print("\n🎯 Performance Insights:")
        if success_rate >= 99:
            print("   ✅ Excellent success rate!")
        elif success_rate >= 95:
            print("   ⚠️  Good success rate, but some failures under load")
        else:
            print("   ❌ High failure rate - system may be overloaded")
        
        avg_latency = stats.total.avg_response_time
        if avg_latency < 500:
            print(f"   ✅ Fast response times ({avg_latency:.0f}ms avg)")
        elif avg_latency < 2000:
            print(f"   ⚠️  Acceptable response times ({avg_latency:.0f}ms avg)")
        else:
            print(f"   ❌ Slow response times ({avg_latency:.0f}ms avg)")
    
    print("\n" + "="*60 + "\n")