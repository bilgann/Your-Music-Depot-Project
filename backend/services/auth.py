import jwt
from datetime import datetime, timedelta, timezone

# We use classes to keep services stateful be default because services have a lifecycle(the execution window of an api call in this case). - Zach
class auth_service:
    # TODO: extract into a config/env file
    secret_key = "your-very-secure-secret-key"
    algorithm = ["HS256"] # use RS256 if you wanna get asymmetrical with the tokens(useful for larger scope/scale)

    def __init__(self):
