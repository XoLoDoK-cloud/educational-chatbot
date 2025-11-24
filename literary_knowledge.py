"""
Literary Knowledge Module - Functions for literature search and analysis
"""

def search_literature(query):
    """Search literature database by query"""
    from coprehensive_knowledge import knowledge
    return knowledge.search_by_name(query)


def get_works(writer_key):
    """Get works of a specific writer"""
    from coprehensive_knowledge import knowledge
    if writer_key in knowledge.writers_db:
        writer = knowledge.writers_db[writer_key]
        return {
            "name": writer.get("name"),
            "key_works": writer.get("key_works", []),
            "works_with_dates": writer.get("works_with_dates", {})
        }
    return None


def answer_question(question, writer_key="default"):
    """Answer question about literature/writer"""
    from coprehensive_knowledge import knowledge
    
    if writer_key == "default":
        writer_key = knowledge.search_by_name(question)
    
    if not writer_key or writer_key not in knowledge.writers_db:
        return None
    
    return knowledge.get_expert_text(writer_key, question)
