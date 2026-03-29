class ResponseContract:
    def __init__(self, success: bool, message: str, data=None, errors=None, total: int = None):
        self.success = success
        self.message = message
        self.data = data
        self.errors = errors
        self.total = total

    def to_dict(self):
        result = {
            "success": self.success,
            "message": self.message,
            "data": self.data,
        }
        if self.errors is not None:
            result["errors"] = self.errors
        if self.total is not None:
            result["total"] = self.total
        return result
