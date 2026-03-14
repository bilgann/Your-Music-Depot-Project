# We use classes to keep services stateful be default because services have a lifecycle(the execution window of an api call in this case). - Zach

from backend.app.models.user import User

class auth_service:
    def __init__(self):

    def verify_user(self, user):
        if user not in User.query.all():