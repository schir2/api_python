from .result import Result
from .error import TSheetsError


class Bridge(object):

    def __init__(self, config):
        self.config = config
        self.auth_options = {"Authorization" : "Bearer {}".format(self.config.access_token)}

    def items_from_data(self, data, name, is_singleton, mode):
        if mode == "report":
            objects = list(data["results"].values())[0]
            return [] if not objects else list(objects.values())

        if is_singleton or (not isinstance(data['results'][name], dict)):
            return data['results'][name]
        else:
            return list(data['results'][name].values())

    def next_batch(self, url, name, options, is_singleton = False, mode="list"):
        method = "get" if mode == "list" else "post"

        if mode == "report":
            options = {"data": 0 if not options else options}

        if method == "get":
            response = self.config.adapter.get((self.config.base_url+url), options, self.auth_options)
        else:
            response = self.config.adapter.post((self.config.base_url+url), options, self.auth_options)

        data = response.json()
        if response.status_code == 200:
            if not data:
                return {"items": [], "has_more": False, "supplemental": {} }
            else:
                s_dict = {}
                if 'supplemental_data' in data:
                    for key, value in data['supplemental_data'].items():
                        s_dict[key] = list(value.values())
                has_more = data.get('more', None)
                result = {"items": self.items_from_data(data, name, is_singleton, mode),
                          "has_more": (has_more == 'true'),
                          "supplemental": s_dict}
                return result
        else:
            raise TSheetsError("Expectation Failed")

    def insert(self, url, raw_entity):
        response = self.config.adapter.post((self.config.base_url + url), {'data': [raw_entity]}, self.auth_options)
        return Result(response.status_code, response.json())

    def update(self, url, raw_entity):
        response = self.config.adapter.put((self.config.base_url+url), {'data': [raw_entity]}, self.auth_options)
        return Result(response.status_code, response.json())

    def delete(self, url, id):
        response = self.config.adapter.delete((self.config.base_url+url), {'ids': [id]}, self.auth_options)
        return Result(response.status_code, response.json())
