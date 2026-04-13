def handle_db_query(query, role):
    if role != "admin":
        return "Unauthorized"

    if "how many students" in query.lower():
        return "There are 245 students present."

    return "Query not supported"