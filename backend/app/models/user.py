class User:
    def __init__(self, id, username, password=None):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def validate_user(username, password):
        if username == "barnes" and password == "password":
            return User(0, username, password)
        return None