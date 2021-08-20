import datetime
import time
import logging
import subprocess
import 

## rrd init 
#rrdtool create ecotec-temp.rrd -s 60 DS:outsidetemp:GAUGE:180:U:U DS:roomTemperature:GAUGE:180:U:U DS:storagetemp:GAUGE:180:U:U DS:flowtemp:GAUGE:180:U:U DS:flowtempdesired:GAUGE:180:U:U DS:returntemp:GAUGE:180:U:U RRA:AVERAGE:0.5:1:44640
#rrdtool create ecotec-parm.rrd -s 60 DS:power:GAUGE:180:U:U DS:cwupump:GAUGE:180:U:U DS:pressure:GAUGE:180:U:U DS:tempdesired:GAUGE:180:U:U DS:blocktime:GAUGE:180:U:U DS:valve:GAUGE:180:U:U RRA:AVERAGE:0.5:1:44640

#configuration:  start
ip="127.0.0.1"; 
outdir="/home/pi/rrdlogs/"

rrdtempfile = outdir + "ecotec-temp.rrd"
rrdparamfile = outdir + "ecotec-parm.rrd"
counterlog = outdir + "vaillant-prenergy.log"
ecoteclog = outdir + "vaillant-ecotec.log"

logging.basicConfig(filename = ecoteclog, level=logging.INFO, format='%(asctime)s; %(message)s', datefmt='%Y-%m-%d %H:%M')
logging.basicConfig(filename = 'error.log', level=logging.ERROR, format='%(asctime)s; %(message)s', datefmt='%Y-%m-%d %H:%M')


def getRegData(regName, circuit="bai"):
    print("getRegData: " + regName)   
    try:
        result = subprocess.check_output(['/usr/bin/ebusctl','-s', ip, 'read' , '-m', '30', '-c', circuit, regName])
        if result[0:3].upper() != "ERR":
            return result.strip()
        return "ERR"
    except subprocess.CalledProcessError as grepexc:
        print("error code", grepexc.returncode, grepexc.output)
        return "ERR"    


def storeDataToRRD(logString, logFile):
    try:
        subprocess.check_output(['/usr/bin/rrdtool', 'update', logFile, logString])
    except subprocess.CalledProcessError as e:
        logging.error("RRDTool error:", e.output)  


#Flame
tmpVar = getRegData("Flame")
flame =1 if tmpVar=='on' else 0

# Outdoor temperature
outdoorTemp = getRegData("OutdoorstempSensor")
tempArr = outdoorTemp.split(";")
outsidetemp = tempArr[0] if tempArr[0] != "ERR" else 0
outsidetempstatus = tempArr[1] if len(tempArr) > 1 else "ERR"

# temperatura w pokoju
roomTemperature = getRegData("z1RoomTemp", "700");

# Flow temp
flow = getRegData("FlowTemp");
tempArr = flow.split(";")
flowtemp = tempArr[0] if tempArr[0] != "ERR" else 0
flowtempstatus = tempArr[1] if len(tempArr) > 1 else "ERR"

# Flow Temp Desired
tmpVar = getRegData("FlowTempDesired")
flowtempdesired = tmpVar if tmpVar != "ERR" else 0

# Return temperature
returnTemp = getRegData("ReturnTemp")
tempArr = returnTemp.split(";")
returntemp = tempArr[0] if tempArr[0] != "ERR" else 0
#returntempstatus = tempArr[1] if len(tempArr) > 1 else "ERR"

# Water pressure
waterPress = getRegData("WaterPressure")
tempArr = waterPress.split(";")
waterpressure = tempArr[0] if tempArr[0] != "ERR" else 0
waterpressurestatus = tempArr[1] if len(tempArr) > 1 else "ERR"

# aktualna moc palnika [%]
power=getRegData("power")

# pozostaly czas blokady czasowej ogrzewania
remainingboilerblocktime=getRegData("RemainingBoilerblocktime")

# pozycja zaworu przelaczajacego miedzy ogrzewaniem zasobnika cieplej wody a centralnym ogrzewaniem
positionvalveset=getRegData("PositionValveSet")

# Boiler
storage = getRegData("StorageTemp")
tempArr = storage.split(";")
storagetemp = tempArr[0] if tempArr[0] != "ERR" else 0
storagetempstatus = tempArr[1] if len(tempArr) > 1 else "ERR"

#pompa CWU
tmpVar = getRegData("CirPump");
cwupump = 1 if tmpVar=='on' else 0



#####################################################################################

# write temperature logs
logData = str(time.time()) + ":{outsidetemp}:{roomTemperature}:{storagetemp}:{flowtemp}:{flowtempdesired}:{returntemp}".format(**vars())
storeDataToRRD(logData, rrdtempfile)

# write other logs
logData = str(time.time()) + ":{flame}:{cwupump}:{waterpressure}:{power}:{remainingboilerblocktime}:{positionvalveset}".format(**vars())
storeDataToRRD(logData, rrdparamfile)

#store data to file
logData = "{outsidetemp}; {roomTemperature}; {storagetemp}; {flame}; {cwupump}; {waterpressure}".format(**vars())
logging.info(logData)

# Power counters
if datetime.datetime.now().minute == 0:
    prenergysumhc1=getRegData("PrEnergySumHc1")
    prenergycounterhc1=getRegData("PrEnergyCountHc1")
    prenergysumhwc1=getRegData("PrEnergySumHwc1")
    prenergycounterhwc1=getRegData("PrEnergyCountHwc1")
    logString3 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + "; {prenergysumhc1}; {prenergycounterhc1}; {prenergysumhwc1}; {prenergycounterhwc1}\n".format(**vars())
    with open(counterlog, "a") as myfile:
        myfile.write(logString3)

