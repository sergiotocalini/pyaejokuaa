#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' Classes to manage the Databases '''

from elixir import *
from DBConfig import DBConf

class Servers(Entity):
    using_options(tablename='servers')
    addr=Field(Unicode,required=True)
    host=Field(Unicode)
    user=Field(Unicode)
    passwd1=Field(Unicode)
    passwd2=Field(Unicode)
    passwd3=Field(Unicode)
    port=Field(Integer)
    system=Field(Unicode)
    cmds=Field(Unicode)
    comment=Field(Unicode)
    profile=ManyToOne('Profiles')

class Profiles(Entity):
    using_options(tablename='profiles')
    profile=Field(Integer,required=True)
    name=Field(Unicode)
    email=Field(Unicode)
    passwd=Field(Unicode,required=True)
    passphrase=Field(Unicode)
    status=Field(Unicode)
    last_access=Field(DateTime)
    servers=OneToMany('Servers')
    
metadata.bind = DBConf().load()
#metadata.bind.echo = True
