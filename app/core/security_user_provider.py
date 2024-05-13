from ..schemas import user_schema

users = {}


def get_user(username: str) -> user_schema.UserInDb:
    if username in users:
        user_dict = users[username]
        return user_schema.UserInDb(**user_dict)


def get_users() -> dict:
    return users
