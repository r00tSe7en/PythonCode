#!/usr/bin/env python
#coding=utf-8
users = {
    'aeinstein': {
        'first': 'albert',
        'last': 'einstein',
        'location': 'princeton',
    },

    'mcurie': {
        'first': 'marie',
        'last': 'curie',
        'location': 'paris',
    },
}
#print(users.items())
for username,userinfo in users.items():
    print("\nusername:"+username)
    print(userinfo['first']+" "+userinfo['last'])
    print(userinfo['location'])