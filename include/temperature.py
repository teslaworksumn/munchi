import time
import RPi.GPIO as GPIO
import Adafruit_ADS1x15

R25 = 100000 #originally named THERMISORVALUE in arduino code, value from spec sheet (unsure if correct value, sheet says 10k ohms for 7002)
SERIESRESISTOR = 100000 #series resistor to thermistor
BCOEFFICIENT = 4072
Vref = 3.3 #reference voltage across thermistor and 100k

#the following dictionary maps the resistor value to the temperature according to the thermistor spec sheet for the 7002
thermistorR2Temp = {
	3.2575:0,
	2.5348:5, 
	1.9876:10,
	1.5699:15,
	1.2488:20, 
	1.0000:25, 
	0.80594:30, 
	0.65355:35, 
	0.53312:40, 
	0.43735:45, 
	0.36074:50, 
	0.29911:55, 
	0.24925:60, 
	0.20872:65, 
	0.17558:70, 
	0.14837:75, 
	0.12592:80, 
	0.10731:85, 
	0.091816:90, 
	0.078862:95, 
	0.067988:100, 
	0.058824:105, 
	0.051071:110, 
	0.044489:115, 
	0.03888:120, 
	0.034084:125, 
	0.02997:130, 
	0.02643:135, 
	0.023373:140, 
	0.020727:145, 
	0.018429:150, 
	0.016427:155, 
	0.014679:160, 
	0.013149:165, 
	0.011806:170, 
	0.010623:175, 
	0.0095804:180, 
	0.0086582:185, 
	0.0078408:190, 
	0.0071148:195, 
	0.0064685:200
}

#the resistor values are the RT/R25 value specified on the spec sheet
#the below list is used to round the resistor reading down so it can be mapped to the dictionary temperatures
thermistorR = [3.2575, 2.5348, 1.9876, 1.5699, 1.2488, 1.0000, 0.80594, 0.65355, 0.53312, 0.43735, 0.36074, 0.29911, 0.24925, 0.20872, 0.17558, 0.14837, 0.12592, 0.10731, 0.091816, 0.078862, 0.067988, 0.058824, 0.051071, 0.044489, 0.03888, 0.034084, 0.02997, 0.02643, 0.023373, 0.020727, 0.018429, 0.016427, 0.014679, 0.013149, 0.011806, 0.010623, 0.0095804, 0.0086582, 0.0078408, 0.0071148, 0.0064685]

def roundR(Rval): #round RT/R25 to value that can be mapped to temperature
	if Rval > thermistorR[0]: #if outside of first boundary of list
		return thermistorR[0]
	for i, r in enumerate(thermistorR):
		if Rval > r:
			return thermistorR[i-1]
	return thermistorR[len(thermistorR)-1] #if outside second boundary of list

def getTemp(Rval): #converts RT/R25 to associated temperature
	Rval2 = roundR(Rval) #rounded RT/R25 value that can be mapped to temperature
	print("rounded RT/R25: %s" %Rval2)
	return thermistorR2Temp[Rval2]

GPIO.setmode(GPIO.BOARD) #pin numbering scheme uses board header pins
GPIO.setup(19,GPIO.OUT) #pin 19, GPIO12 output
GPIO.setup(26,GPIO.OUT) #pin 26, GPIO07 output

adc = Adafruit_ADS1x15.ADS1015() #create an ADS1015 ADC (12-bit) instance.
# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
GAIN = 1

while True:
	reading = adc.read_adc(0, gain=GAIN) #read A0, 12 bit signed integer, -2048 to 2047 (0=GND, 2047=4.096*gain)
	voltReading = reading * 4.096 / 2047 #convert adc to voltage
	RT = SERIESRESISTOR * voltReading / (Vref - voltReading) #convert voltage to thermoster resistance
	Rval = RT/R25
	temp = getTemp(Rval)
	print("analog reading: %s" %reading)
	print("voltage: %s" %voltReading)
	print("RT: %s" %RT)
	print("RT/R25: %s" %Rval)
	print("temp: %s" %temp)
	print("")
	time.sleep(2)
