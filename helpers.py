import json


def pretty_print(dict):
    print(json.dumps(dict, indent=2, sort_keys=False))
