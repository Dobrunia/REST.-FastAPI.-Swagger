"""Locust load test for gRPC API."""
import random
import string
import time
import grpc
import sys
from pathlib import Path
from locust import User, task, between, events
from locust.exception import StopUser
import psutil
import logging

# Add grpc_app to path for imports
GRPC_APP_PATH = Path(__file__).parent.parent / "grpc_app"
sys.path.insert(0, str(GRPC_APP_PATH))

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Import generated protobuf modules
try:
    import glossary_pb2
    import glossary_pb2_grpc
except ImportError:
    logger.error("Proto files not generated. Run: python grpc_app/generate_proto.py")
    raise

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


class GrpcClient:
    """gRPC client wrapper with timing."""
    
    def __init__(self, host: str):
        self.host = host
        self.channel = grpc.insecure_channel(host)
        self.stub = glossary_pb2_grpc.GlossaryServiceStub(self.channel)
    
    def get_terms(self):
        """Get all terms."""
        return self.stub.GetTerms(glossary_pb2.Empty())
    
    def get_term(self, term_name: str):
        """Get single term."""
        return self.stub.GetTerm(glossary_pb2.TermRequest(term=term_name))
    
    def create_term(self, term_name: str, definition: str):
        """Create new term."""
        return self.stub.CreateTerm(
            glossary_pb2.CreateTermRequest(term=term_name, definition=definition)
        )
    
    def update_term(self, term_name: str, definition: str):
        """Update term."""
        return self.stub.UpdateTerm(
            glossary_pb2.UpdateTermRequest(term=term_name, definition=definition)
        )
    
    def delete_term(self, term_name: str):
        """Delete term."""
        return self.stub.DeleteTerm(glossary_pb2.TermRequest(term=term_name))
    
    def close(self):
        """Close channel."""
        self.channel.close()


class GlossaryGrpcUser(User):
    """Simulates user behavior for gRPC API load testing."""
    
    wait_time = between(1, 3)
    abstract = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = None
        self.created_terms = []
    
    def on_start(self):
        """Connect to gRPC server."""
        host = self.host or "localhost:50051"
        self.client = GrpcClient(host)
        self.created_terms = []
    
    def on_stop(self):
        """Cleanup and disconnect."""
        for term in self.created_terms:
            try:
                self.client.delete_term(term)
            except Exception:
                pass
        if self.client:
            self.client.close()
    
    def _timed_call(self, name: str, func, *args, **kwargs):
        """Execute gRPC call with timing and reporting."""
        start_time = time.perf_counter()
        exception = None
        try:
            result = func(*args, **kwargs)
            response_time = (time.perf_counter() - start_time) * 1000
            events.request.fire(
                request_type="gRPC",
                name=name,
                response_time=response_time,
                response_length=0,
                exception=None,
                context=None
            )
            return result
        except grpc.RpcError as e:
            response_time = (time.perf_counter() - start_time) * 1000
            status_code = e.code()
            if status_code in [grpc.StatusCode.NOT_FOUND, grpc.StatusCode.ALREADY_EXISTS]:
                # Expected errors, don't report as failures
                events.request.fire(
                    request_type="gRPC",
                    name=name,
                    response_time=response_time,
                    response_length=0,
                    exception=None,
                    context=None
                )
            else:
                events.request.fire(
                    request_type="gRPC",
                    name=name,
                    response_time=response_time,
                    response_length=0,
                    exception=e,
                    context=None
                )
            return None
        except Exception as e:
            response_time = (time.perf_counter() - start_time) * 1000
            events.request.fire(
                request_type="gRPC",
                name=name,
                response_time=response_time,
                response_length=0,
                exception=e,
                context=None
            )
            return None

    @task(40)
    def get_all_terms(self):
        """GetTerms - List all terms (40% of requests)."""
        self._timed_call("GetTerms", self.client.get_terms)

    @task(30)
    def get_single_term(self):
        """GetTerm - Get single term (30% of requests)."""
        term = random.choice(SAMPLE_TERMS)
        self._timed_call("GetTerm", self.client.get_term, term)

    @task(20)
    def create_term(self):
        """CreateTerm - Create new term (20% of requests)."""
        term_name = generate_unique_term()
        result = self._timed_call(
            "CreateTerm",
            self.client.create_term,
            term_name,
            f"Test definition for {term_name}"
        )
        if result and result.id:
            self.created_terms.append(term_name)

    @task(5)
    def update_term(self):
        """UpdateTerm - Update term (5% of requests)."""
        term = random.choice(SAMPLE_TERMS)
        self._timed_call(
            "UpdateTerm",
            self.client.update_term,
            term,
            f"Updated definition at {time.time()}"
        )

    @task(5)
    def delete_term(self):
        """DeleteTerm - Delete term (5% of requests)."""
        if self.created_terms:
            term = self.created_terms.pop()
            self._timed_call("DeleteTerm", self.client.delete_term, term)


class GlossaryGrpcUserConcrete(GlossaryGrpcUser):
    """Concrete implementation of GlossaryGrpcUser."""
    abstract = False
    host = "localhost:50051"


# System metrics collection
process_metrics = {"cpu": [], "memory": []}


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Log test start."""
    logger.info("gRPC load test started")
    process_metrics["cpu"].clear()
    process_metrics["memory"].clear()


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Log test results summary."""
    logger.info("gRPC load test stopped")
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

