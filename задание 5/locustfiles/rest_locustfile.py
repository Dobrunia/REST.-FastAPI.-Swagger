"""Locust load test for REST API."""
import random
import string
from locust import HttpUser, task, between, events
import psutil
import time
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Sample terms for testing
SAMPLE_TERMS = [
    "API", "REST", "gRPC", "HTTP", "JSON", "XML", "SQL", "NoSQL",
    "TCP", "UDP", "DNS", "SSL", "TLS", "OAuth", "JWT", "CORS",
    "CDN", "Docker", "Kubernetes", "Microservices", "Protobuf", "GraphQL",
    "WebSocket", "MQTT", "Redis", "PostgreSQL", "MongoDB", "Elasticsearch"
]


def generate_unique_term():
    """Generate unique term name for creation tests."""
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"TestTerm_{suffix}"


class GlossaryRESTUser(HttpUser):
    """Simulates user behavior for REST API load testing."""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when user starts."""
        self.created_terms = []
    
    def on_stop(self):
        """Cleanup created terms on stop."""
        for term in self.created_terms:
            try:
                self.client.delete(f"/terms/{term}")
            except Exception:
                pass

    @task(40)
    def get_all_terms(self):
        """GET /terms - List all terms (40% of requests)."""
        with self.client.get("/terms", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status {response.status_code}")

    @task(30)
    def get_single_term(self):
        """GET /terms/{term} - Get single term (30% of requests)."""
        term = random.choice(SAMPLE_TERMS)
        with self.client.get(f"/terms/{term}", catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Status {response.status_code}")

    @task(20)
    def create_term(self):
        """POST /terms - Create new term (20% of requests)."""
        term_name = generate_unique_term()
        data = {
            "term": term_name,
            "definition": f"Test definition for {term_name}"
        }
        try:
            with self.client.post(
                "/terms", 
                json=data, 
                catch_response=True,
                timeout=30  # Increased to 30 seconds
            ) as response:
                if response.status_code == 201:
                    self.created_terms.append(term_name)
                    response.success()
                elif response.status_code == 409:
                    response.success()  # Term exists, acceptable
                elif response.status_code == 0:
                    response.failure("Connection dropped, skipping")
                else:
                    response.failure(f"Status {response.status_code}")
        except Exception as e:
            pass

    @task(5)
    def update_term(self):
        """PUT /terms/{term} - Update term (5% of requests)."""
        term = random.choice(SAMPLE_TERMS)
        data = {"definition": f"Updated definition at {time.time()}"}
        try:
            with self.client.put(
                f"/terms/{term}", 
                json=data, 
                catch_response=True,
                timeout=30  # Increased to 30 seconds
            ) as response:
                if response.status_code in [200, 404]:
                    response.success()
                elif response.status_code == 0:
                    response.failure("Connection dropped, skipping")
                else:
                    response.failure(f"Status {response.status_code}")
        except Exception as e:
            pass

    @task(5)
    def delete_term(self):
        """DELETE /terms/{term} - Delete term (5% of requests)."""
        if self.created_terms:
            term = self.created_terms.pop()
            with self.client.delete(f"/terms/{term}", catch_response=True) as response:
                if response.status_code in [200, 404]:
                    response.success()
                else:
                    response.failure(f"Status {response.status_code}")


# System metrics collection
process_metrics = {"cpu": [], "memory": []}


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Log test start."""
    logger.info("REST load test started")
    process_metrics["cpu"].clear()
    process_metrics["memory"].clear()


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Log test results summary."""
    logger.info("REST load test stopped")
    if process_metrics["cpu"]:
        avg_cpu = sum(process_metrics["cpu"]) / len(process_metrics["cpu"])
        avg_mem = sum(process_metrics["memory"]) / len(process_metrics["memory"])
        logger.info(f"Avg CPU: {avg_cpu:.1f}%, Avg Memory: {avg_mem:.1f} MB")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Collect system metrics on each request."""
    try:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.Process().memory_info().rss / 1024 / 1024
        process_metrics["cpu"].append(cpu)
        process_metrics["memory"].append(mem)
    except Exception:
        pass

