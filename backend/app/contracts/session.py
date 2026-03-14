class ResponseContract:
    def __init__(self, token: str):
        self.token = token

    def to_dict(self):
        return {
            "token": self.token,
            "message": self.message,
            "data": self.data
        }