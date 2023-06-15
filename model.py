from peewee import *

db = SqliteDatabase('events.db')


class Place(Model):
    id = AutoField()
    name = CharField()

    class Meta:
        database = db
        db_table = 'places'


class Event(Model):
    id = AutoField()
    name = CharField()
    description = TextField()
    max_count = IntegerField()
    min_count = IntegerField()
    place = ForeignKeyField(Place, backref='events')
    date_time = DateTimeField()
    poster_url = CharField()
    discord_role_id = IntegerField()

    class Meta:
        database = db
        db_table = 'events'


class User(Model):
    id = AutoField()
    event_id = ForeignKeyField(Event, backref='users')
    discord_id = IntegerField()
    reg_date = DateTimeField()

    class Meta:
        database = db
        db_table = 'users'
