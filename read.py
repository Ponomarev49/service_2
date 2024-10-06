import json

class Coordinates:
    def __init__(self, coordinates_list):
        self.latitude = coordinates_list[0]
        self.longitude = coordinates_list[1]


def read_users():
    users_dict = {}
    with open("users.json", 'r') as file:
        data = json.load(file)
        users_list = data.get('users', [])
        for user in users_list:
            users_dict[user["username"]] = user["workplace_id"]
    return users_dict

def read_workplaces():
    workplaces_dict = {}
    with open("workplaces.json", 'r') as file:
        data = json.load(file)
        data = data.get('workplaces', [])
        for workplace in data:
            workplaces_dict[int(workplace["id"])] = Coordinates(workplace["coordinates"])
    return workplaces_dict
