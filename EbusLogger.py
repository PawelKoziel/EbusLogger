import datetime
import time
import logging
import subprocess
from SqlLiteLogger import *

#configuration:  start
ebusIp="127.0.0.1"; 
outdir="/home/pi/rrdlogs/"

counterlog = outdir + "vaillant-prenergy.log"
ecoteclog = outdir + "vaillant-ecotec.log"


def getRegData(regName, circuit="bai"):
    try:
        #result = subprocess.check_output(['/usr/bin/ebusctl','-s', ebusIp, 'read' , '-m', '30', '-c', circuit, regName]).strip()
        # if type(varName) == bool:result = 'on;NOK'
        # if type(varName) == float: result = '1.1;OK'
        # if type(varName) == int: result = '10;OK'
        result = '0;OK'


        result = result.upper()
        if result.startswith("ERR"): return 0
        if ';' in result: result = result.split(";")[0]
        if 'ON' in result : return 1
        if 'OFF' in result : return 0
        return result

    except subprocess.CalledProcessError as grepexc:
        print("error code", grepexc.returncode, grepexc.output)
        return 0


temp = Temps()
params = Params()


#Flame
temp.flame = getRegData("Flame")

# Outdoor temperature
temp.outdoor = getRegData("OutdoorstempSensor")

# temperatura w pokoju
temp.indoor = getRegData("z1RoomTemp", "700");

# Flow temp
temp.flow = getRegData("FlowTemp");

# Flow Temp Desired
temp.flowReqired = getRegData("FlowTempDesired")

# Return temperature
temp.flowReturn = getRegData("ReturnTemp")

# Water pressure
params.waterPress = getRegData("WaterPressure")

# aktualna moc palnika [%]
params.power = getRegData("power")

# pozostaly czas blokady czasowej ogrzewania
params.blockTime = getRegData("RemainingBoilerblocktime")

# pozycja zaworu przelaczajacego miedzy ogrzewaniem zasobnika cieplej wody a centralnym ogrzewaniem
params.valvePosition = getRegData("PositionValveSet")

# Boiler
temp.hwcWater = getRegData("StorageTemp")

#pompa CWU
hwcPump = getRegData("CirPump");



#####################################################################################

# # write temperature logs
# logData = str(time.time()) + ":{outsidetemp}:{roomTemperature}:{storagetemp}:{flowtemp}:{flowtempdesired}:{returntemp}".format(**vars())
# storeDataToRRD(logData, rrdtempfile)

# # write other logs
# logData = str(time.time()) + ":{flame}:{cwupump}:{waterpressure}:{power}:{remainingboilerblocktime}:{positionvalveset}".format(**vars())
# storeDataToRRD(logData, rrdparamfile)

# #store data to file
# logData = "{outsidetemp}; {roomTemperature}; {storagetemp}; {flame}; {cwupump}; {waterpressure}".format(**vars())
# logging.info(logData)

#insert to db
temp.save()
params.save()

# Power counters
if datetime.datetime.now().minute == 0:
    energy = Energy()
    #zoba dla hc2

    energy.hcEnergySum=getRegData("PrEnergySumHc1") 
    energy.hcEnergyCnt=getRegData("PrEnergyCountHc1")
    energy.hwcEnergySum=getRegData("PrEnergySumHwc1")
    energy.hwcEnergyCnt=getRegData("PrEnergyCountHwc1")
    
    energy.save()

    logString3 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + "; {prenergysumhc1}; {prenergycounterhc1}; {prenergysumhwc1}; {prenergycounterhwc1}\n".format(**vars())
    #with open(counterlog, "a") as myfile:
    #    myfile.write(logString3)



