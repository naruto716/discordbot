from Config import ADMIN_DICT


class PermissionManager:
    def __init__(self):
        self.permission_dict = ADMIN_DICT.copy()

    def get_permission(self, user):
        if user not in self.permission_dict:
            return 0
        return self.permission_dict[user]

    def set_permission(self, user, permission: int):
        self.permission_dict[user] = permission

    def check_permission(self, user, permission: int):
        return self.get_permission(user) >= permission

    def check_permission_wrapper(self, user, permission: int, function, *args, **kwargs):
        if self.check_permission(user, permission):
            return function(*args, **kwargs)
        else:
            return False