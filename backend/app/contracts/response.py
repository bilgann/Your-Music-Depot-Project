class ResponseContract:
    def __init__(self, success: bool, message: str, data=None, errors=None):
        self.success = success
        self.message = message
        self.data = data
        self.errors = errors  # list of {"field": ..., "message": ...} for validation failures

    def to_dict(self):
        result = {
            "success": self.success,
            "message": self.message,
            "data": self.data,
        }
        if self.errors is not None:
            result["errors"] = self.errors
        return result