import grpc
from concurrent import futures
import logging
import sys
from pathlib import Path

# Add proto path for imports
sys.path.insert(0, str(Path(__file__).parent))

import glossary_pb2
import glossary_pb2_grpc
import database

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class GlossaryServicer(glossary_pb2_grpc.GlossaryServiceServicer):
    
    def GetTerms(self, request, context):
        logger.info("GetTerms: fetching all terms")
        terms = database.get_all_terms()
        term_messages = [
            glossary_pb2.Term(
                id=t["id"],
                term=t["term"],
                definition=t["definition"],
                created_at=t["created_at"] or "",
                updated_at=t["updated_at"] or ""
            )
            for t in terms
        ]
        logger.info(f"GetTerms: found {len(terms)} terms")
        return glossary_pb2.TermList(terms=term_messages)

    def GetTerm(self, request, context):
        term_name = request.term
        logger.info(f"GetTerm: looking for '{term_name}'")
        
        if not term_name:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Term name required")
            return glossary_pb2.Term()

        result = database.get_term_by_name(term_name)
        if not result:
            logger.info(f"GetTerm: '{term_name}' not found")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Term '{term_name}' not found")
            return glossary_pb2.Term()

        logger.info(f"GetTerm: found '{term_name}' (id={result['id']})")
        return glossary_pb2.Term(
            id=result["id"],
            term=result["term"],
            definition=result["definition"],
            created_at=result["created_at"] or "",
            updated_at=result["updated_at"] or ""
        )

    def CreateTerm(self, request, context):
        term_name = request.term
        definition = request.definition
        logger.info(f"CreateTerm: creating '{term_name}'")

        if not term_name or not definition:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Term and definition required")
            return glossary_pb2.Term()

        result = database.create_term(term_name, definition)
        if not result:
            logger.info(f"CreateTerm: '{term_name}' already exists")
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(f"Term '{term_name}' already exists")
            return glossary_pb2.Term()

        logger.info(f"CreateTerm: created '{term_name}' (id={result['id']})")
        return glossary_pb2.Term(
            id=result["id"],
            term=result["term"],
            definition=result["definition"],
            created_at=result["created_at"] or "",
            updated_at=result["updated_at"] or ""
        )

    def UpdateTerm(self, request, context):
        term_name = request.term
        definition = request.definition
        logger.info(f"UpdateTerm: updating '{term_name}'")

        if not term_name or not definition:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Term and definition required")
            return glossary_pb2.Term()

        result = database.update_term(term_name, definition)
        if not result:
            logger.info(f"UpdateTerm: '{term_name}' not found")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Term '{term_name}' not found")
            return glossary_pb2.Term()

        logger.info(f"UpdateTerm: updated '{term_name}'")
        return glossary_pb2.Term(
            id=result["id"],
            term=result["term"],
            definition=result["definition"],
            created_at=result["created_at"] or "",
            updated_at=result["updated_at"] or ""
        )

    def DeleteTerm(self, request, context):
        term_name = request.term
        logger.info(f"DeleteTerm: deleting '{term_name}'")

        if not term_name:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Term name required")
            return glossary_pb2.OperationResult(success=False, message="Term name required")

        success = database.delete_term(term_name)
        if not success:
            logger.info(f"DeleteTerm: '{term_name}' not found")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Term '{term_name}' not found")
            return glossary_pb2.OperationResult(success=False, message=f"Term '{term_name}' not found")

        logger.info(f"DeleteTerm: deleted '{term_name}'")
        return glossary_pb2.OperationResult(success=True, message=f"Term '{term_name}' deleted")


def serve(host: str = "0.0.0.0", port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    glossary_pb2_grpc.add_GlossaryServiceServicer_to_server(GlossaryServicer(), server)
    
    address = f"{host}:{port}"
    server.add_insecure_port(address)
    server.start()
    
    logger.info("=" * 50)
    logger.info("gRPC Glossary Server started")
    logger.info(f"Address: {address}")
    logger.info("Methods: GetTerms, GetTerm, CreateTerm, UpdateTerm, DeleteTerm")
    logger.info("=" * 50)
    
    server.wait_for_termination()


if __name__ == "__main__":
    serve()

