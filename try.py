# coding=utf-8

import json
import time
import datetime
js = {
    "a": 1,
    "b": 2
}

# print(js)


print(json.dumps(js, indent=4))

print (type(datetime.datetime.now()))
a = 1
print(id(a), type(a), a)
print(id(int), type(int), int)
print(id(type), type(type), type)
