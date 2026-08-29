def is_admin(user):
    return bool(user and user.get("role") == "Admin")


def require_admin(user, messagebox, action):
    if is_admin(user):
        return True
    messagebox.showwarning("Admin Required", f"{action} করতে Admin permission প্রয়োজন।")
    return False
