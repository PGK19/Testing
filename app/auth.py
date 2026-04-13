def get_role_prompt(role):
    if role == "admin":
        return "You are an admin assistant with full access."
    return "You are a student assistant with restricted access."