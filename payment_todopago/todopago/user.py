# -*- coding: utf-8 -*-
class User:
    def __init__(self, user, password):
        self.user = user
        self.password = password

    def getData(self):
        return {"USUARIO": self.user, "PASSWORD": self.password}
