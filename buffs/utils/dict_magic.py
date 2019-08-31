from collections import defaultdict


class defaultdictlist(defaultdict):
    def __init__(self):
        super(defaultdictlist, self).__init__(list)

    def remove_from_list(self, key, value):
        if value in self[key]:
            self[key].remove(value)
            if len(self[key]) == 0:
                del self[key]