"""gRPC Glossary Client - for testing and demonstration."""
import grpc
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import glossary_pb2
import glossary_pb2_grpc


def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = glossary_pb2_grpc.GlossaryServiceStub(channel)
    
    print("=" * 50)
    print("gRPC Glossary Client")
    print("=" * 50)
    
    # 1. Create terms
    print("\n1. Creating terms...")
    print("-" * 40)
    test_terms = [
        ("TestAPI", "Test API description"),
        ("TestRPC", "Test RPC description"),
    ]
    
    for term, definition in test_terms:
        try:
            response = stub.CreateTerm(
                glossary_pb2.CreateTermRequest(term=term, definition=definition)
            )
            print(f"Created: {response.term} (id={response.id})")
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.ALREADY_EXISTS:
                print(f"Exists: {term}")
            else:
                print(f"Error: {e.details()}")
    
    # 2. Get all terms
    print("\n2. Getting all terms...")
    print("-" * 40)
    response = stub.GetTerms(glossary_pb2.Empty())
    print(f"Total terms: {len(response.terms)}")
    for t in response.terms[:5]:
        print(f"  - {t.term}: {t.definition[:50]}...")
    
    # 3. Get single term
    print("\n3. Getting term 'TestAPI'...")
    print("-" * 40)
    try:
        response = stub.GetTerm(glossary_pb2.TermRequest(term="TestAPI"))
        print(f"Found: {response.term}")
        print(f"Definition: {response.definition}")
    except grpc.RpcError as e:
        print(f"Error: {e.details()}")
    
    # 4. Update term
    print("\n4. Updating term 'TestAPI'...")
    print("-" * 40)
    try:
        response = stub.UpdateTerm(
            glossary_pb2.UpdateTermRequest(term="TestAPI", definition="Updated definition")
        )
        print(f"Updated: {response.term}")
        print(f"New definition: {response.definition}")
    except grpc.RpcError as e:
        print(f"Error: {e.details()}")
    
    # 5. Delete terms
    print("\n5. Deleting test terms...")
    print("-" * 40)
    for term, _ in test_terms:
        try:
            response = stub.DeleteTerm(glossary_pb2.TermRequest(term=term))
            print(f"Deleted: {term} - {response.message}")
        except grpc.RpcError as e:
            print(f"Error deleting {term}: {e.details()}")
    
    print("\n" + "=" * 50)
    print("Done")
    print("=" * 50)
    
    channel.close()


if __name__ == "__main__":
    run()

