import datetime
import random
from peewee import *

dbFile = "test.db"

#instance of a Database
db = SqliteDatabase(dbFile)  

#base model class
class BaseModel(Model): 
    class Meta:
        database = db

class Temps(BaseModel):
    id = PrimaryKeyField()
    date = DateTimeField(default=datetime.datetime.now)
    outdoor = DecimalField()
    indoor = DecimalField()
    hwcWater = DecimalField()
    flowActual = DecimalField()
    flowReqired = DecimalField()
    flowReturn = DecimalField()


class Params(BaseModel):
    flame = BooleanField()
    power = SmallIntegerField()
    waterpressure = DecimalField()
    blockTime = SmallIntegerField()
    valvePosition = DecimalField()
    hwcPump = BooleanField()


class Energy(BaseModel):
    date = DateTimeField(default=datetime.datetime.now)
    hcEnergySum= IntegerField()
    hcEnergyCnt= IntegerField()
    hwcEnergySum= IntegerField()
    hwcEnergyCnt= IntegerField()




db.connect()
db.create_tables([Temps, Params, Energy])


def sqlTestData():
    entry1 = Temps(
                outdoor=random.randrange(100,400)/(1* 8.0),
                indoor=random.randrange(100,400)/8.0,
                hwcWater=random.randrange(100,400)/8.0,
                flowActual=random.randrange(100,400)/8.0,
                flowReqired=random.randrange(100,400)/8.0,
                flowReturn=random.randrange(100,400)/8.0
             )

    parm1 =  Params(
        flame = 1,
        power = 30,
        hwcPump = 1,
        waterpressure = random.randrange(10,20)/10.0,
        blockTime = 67,
        valvePosition = 80
    )

    energy1 = Energy(
        hcEnergySum= 1575616920,
        hcEnergyCnt= 6793961,
        hwcEnergySum= 190927441,
        hwcEnergyCnt= 559336
    )

    entry1.save()
    energy1.save()
    parm1.save()



i = 1
while i < 600:
    sqlTestData()
    i += 1

