"""Seed both REST and gRPC databases with identical test data."""
import sqlite3
from pathlib import Path
from datetime import datetime
import random

# Database paths
BASE_DIR = Path(__file__).parent.parent
REST_DB = BASE_DIR / "rest_app" / "app" / "db" / "glossary.db"
GRPC_DB = BASE_DIR / "grpc_app" / "glossary.db"

# Test terms for seeding
TEST_TERMS = [
    ("API", "Application Programming Interface - set of protocols for building software"),
    ("REST", "Representational State Transfer - architectural style for distributed systems"),
    ("gRPC", "Google Remote Procedure Call - high performance RPC framework"),
    ("HTTP", "HyperText Transfer Protocol - application layer protocol for data transfer"),
    ("JSON", "JavaScript Object Notation - lightweight data interchange format"),
    ("XML", "eXtensible Markup Language - markup language for encoding documents"),
    ("SQL", "Structured Query Language - language for managing relational databases"),
    ("NoSQL", "Non-relational database systems - flexible schema data storage"),
    ("TCP", "Transmission Control Protocol - reliable connection-oriented protocol"),
    ("UDP", "User Datagram Protocol - connectionless transport protocol"),
    ("DNS", "Domain Name System - hierarchical naming system for computers"),
    ("SSL", "Secure Sockets Layer - cryptographic protocol for secure communication"),
    ("TLS", "Transport Layer Security - successor to SSL for encryption"),
    ("OAuth", "Open Authorization - open standard for access delegation"),
    ("JWT", "JSON Web Token - compact URL-safe means of representing claims"),
    ("CORS", "Cross-Origin Resource Sharing - mechanism for cross-domain requests"),
    ("CDN", "Content Delivery Network - distributed server system for content"),
    ("Docker", "Platform for containerized application deployment"),
    ("Kubernetes", "Container orchestration system for automating deployment"),
    ("Microservices", "Architectural style structuring app as collection of services"),
    ("Protobuf", "Protocol Buffers - language-neutral data serialization format"),
    ("GraphQL", "Query language for APIs and runtime for executing queries"),
    ("WebSocket", "Protocol providing full-duplex communication channels"),
    ("MQTT", "Message Queuing Telemetry Transport - lightweight messaging protocol"),
    ("Redis", "In-memory data structure store used as database and cache"),
    ("PostgreSQL", "Open source object-relational database system"),
    ("MongoDB", "Document-oriented NoSQL database program"),
    ("Elasticsearch", "Distributed search and analytics engine"),
    ("RabbitMQ", "Open source message broker software"),
    ("Kafka", "Distributed event streaming platform"),
    ("Nginx", "Web server and reverse proxy server"),
    ("Load Balancer", "Device distributing network traffic across servers"),
    ("Cache", "Hardware or software component storing data for faster access"),
    ("Latency", "Time delay between cause and effect in a system"),
    ("Throughput", "Amount of data processed in a given time period"),
    ("Scalability", "Capability to handle growing amount of work"),
    ("Availability", "Proportion of time system is operational"),
    ("Fault Tolerance", "System ability to continue operating after failures"),
    ("Replication", "Sharing information across redundant resources"),
    ("Sharding", "Database partitioning separating large databases"),
    ("CI/CD", "Continuous Integration and Continuous Deployment practices"),
    ("DevOps", "Practices combining software development and IT operations"),
    ("Agile", "Iterative approach to software delivery"),
    ("Scrum", "Framework for managing and completing complex projects"),
    ("Kanban", "Visual workflow management method"),
    ("Git", "Distributed version control system"),
    ("Terraform", "Infrastructure as code software tool"),
    ("Ansible", "Open source automation platform"),
    ("Prometheus", "Open source monitoring and alerting toolkit"),
    ("Grafana", "Open source analytics and monitoring solution"),
]


def create_table(conn: sqlite3.Connection):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS terms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT UNIQUE NOT NULL,
            definition TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()


def clear_table(conn: sqlite3.Connection):
    conn.execute("DELETE FROM terms")
    conn.commit()


def seed_terms(conn: sqlite3.Connection, terms: list):
    for term, definition in terms:
        try:
            conn.execute(
                "INSERT INTO terms (term, definition) VALUES (?, ?)",
                (term, definition)
            )
        except sqlite3.IntegrityError:
            pass  # Term already exists
    conn.commit()


def seed_database(db_path: Path, count: int = None):
    """Seed a single database with test terms."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    create_table(conn)
    clear_table(conn)
    
    terms_to_seed = TEST_TERMS
    if count and count < len(TEST_TERMS):
        terms_to_seed = random.sample(TEST_TERMS, count)
    
    seed_terms(conn, terms_to_seed)
    
    cursor = conn.execute("SELECT COUNT(*) FROM terms")
    total = cursor.fetchone()[0]
    conn.close()
    
    return total


def main():
    print("Seeding databases...")
    print("-" * 40)
    
    # Seed REST database
    rest_count = seed_database(REST_DB)
    print(f"REST DB ({REST_DB}): {rest_count} terms")
    
    # Seed gRPC database
    grpc_count = seed_database(GRPC_DB)
    print(f"gRPC DB ({GRPC_DB}): {grpc_count} terms")
    
    print("-" * 40)
    print("Done")


if __name__ == "__main__":
    main()

