def create_roomname(user1, user2):
    """Create a unique room name for two users."""
    users = sorted([user1, user2])
    return f"{users[0]}_{users[1]}"
