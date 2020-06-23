import pymongo

client = pymongo.MongoClient('localhost',27017)
database = client.people
collection = database.residential

