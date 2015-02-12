import RPi.GPIO as GPIO
import smbus
import time
from time import strftime
import serial
import os.path
import thread
from multiprocessing.pool import ThreadPool

GPIO.setmode(GPIO.BCM)

GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18

# Define some device constants
LCD_WIDTH = 20    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line 

# Timing constants
E_PULSE = 0.00005
E_DELAY = 0.00005

# for RPI version 1, use "bus = smbus.SMBus(0)"
bus = smbus.SMBus(1)

# This is the address we setup in the Arduino Program
address = 0x04

def main():
    # Main program block
    
    #  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LCD_E, GPIO.OUT)  # E
    GPIO.setup(LCD_RS, GPIO.OUT) # RS
    GPIO.setup(LCD_D4, GPIO.OUT) # DB4
    GPIO.setup(LCD_D5, GPIO.OUT) # DB5
    GPIO.setup(LCD_D6, GPIO.OUT) # DB6
    GPIO.setup(LCD_D7, GPIO.OUT) # DB7
    
    # Initialise display
    lcd_init()
    


def lcd_init():
    # Initialise display
    lcd_byte(0x33,LCD_CMD)
    lcd_byte(0x32,LCD_CMD)
    lcd_byte(0x28,LCD_CMD)
    lcd_byte(0x0C,LCD_CMD)
    lcd_byte(0x06,LCD_CMD)
    lcd_byte(0x01,LCD_CMD)
    while True:
        time.sleep(0.01)
        lcd_byte(LCD_LINE_1, LCD_CMD)
        lcd_string("Press Start")
        lcd_byte(LCD_LINE_2, LCD_CMD)
        lcd_string("to start connection")
        lcd_byte(LCD_LINE_3, LCD_CMD)
        lcd_string("...")
        lcd_byte(LCD_LINE_4, LCD_CMD)
        lcd_string("")  
        input_start = GPIO.input(4)
        if input_start == False:
            driverCode()
        reset_r = GPIO.input(22)
        if reset_r == False:
                while True:
                    if os.path.isfile("record.txt"):
                        time.sleep(0.01)
                        lcd_byte(LCD_LINE_1, LCD_CMD)
                        lcd_string("Are you sure to")
                        lcd_byte(LCD_LINE_2, LCD_CMD)
                        lcd_string(" clear RECORD file?")
                        lcd_byte(LCD_LINE_3, LCD_CMD)
                        lcd_string(">OK< to confirm")
                        lcd_byte(LCD_LINE_4, LCD_CMD)
                        lcd_string(">BACK< to cancel")
                        input_ok = GPIO.input(4)
                        if input_ok == False:
                            #delete file
                            os.remove("record.txt")
                            lcd_byte(LCD_LINE_1, LCD_CMD)
                            lcd_string("RECORD cleared !")
                            lcd_byte(LCD_LINE_2, LCD_CMD)
                            lcd_string("")
                            lcd_byte(LCD_LINE_3, LCD_CMD)
                            lcd_string("")
                            lcd_byte(LCD_LINE_4, LCD_CMD)
                            lcd_string("")
                            time.sleep(1.5)
                            main()
                        input_cancel = GPIO.input(22)
                        if input_cancel == False:
                            lcd_byte(LCD_LINE_1, LCD_CMD)
                            lcd_string("Canceling...")
                            lcd_byte(LCD_LINE_2, LCD_CMD)
                            lcd_string("")
                            lcd_byte(LCD_LINE_3, LCD_CMD)
                            lcd_string("")
                            lcd_byte(LCD_LINE_4, LCD_CMD)
                            lcd_string("")
                            time.sleep(1.5)
                            main()
                    else:
                        lcd_byte(LCD_LINE_1, LCD_CMD)
                        lcd_string("Not found any RECORD")
                        lcd_byte(LCD_LINE_2, LCD_CMD)
                        lcd_string(" ! ! !")
                        lcd_byte(LCD_LINE_3, LCD_CMD)
                        lcd_string("")
                        lcd_byte(LCD_LINE_4, LCD_CMD)
                        lcd_string("")
                        time.sleep(1.5)
                        main()

def lcd_string(message):
    # Send string to display
    
    message = message.ljust(LCD_WIDTH," ")
    
    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]),LCD_CHR)

def lcd_byte(bits, mode):
    # Send byte to data pins
    # bits = data
    # mode = True  for character
    #        False for command
    
    GPIO.output(LCD_RS, mode) # RS
    
    # High bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    
    
    GPIO.output(LCD_D7, False)
    if bits&0x10==0x10:
        GPIO.output(LCD_D4, True)
    if bits&0x20==0x20:
        GPIO.output(LCD_D5, True)
    if bits&0x40==0x40:
        GPIO.output(LCD_D6, True)
    if bits&0x80==0x80:
        GPIO.output(LCD_D7, True)
    
    # Toggle 'Enable' pin
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, False)
    time.sleep(E_DELAY)
    
    # Low bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits&0x01==0x01:
        GPIO.output(LCD_D4, True)
    if bits&0x02==0x02:
        GPIO.output(LCD_D5, True)
    if bits&0x04==0x04:
        GPIO.output(LCD_D6, True)
    if bits&0x08==0x08:
        GPIO.output(LCD_D7, True)
    
    # Toggle 'Enable' pin
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, False)
    time.sleep(E_DELAY) 

def speed(serialIO):
    #time.sleep(0.01)
    try:
        serialIO.write("01 0D \r")
        line_speed = serialIO.readline().split(" ")
	print "speed: ",line_speed
        speed = int("0x"+line_speed[4], 16)
        return speed
    except:
        return 0

def rpm(serialIO):
    #time.sleep(0.03)
    try:
        serialIO.write("01 0C \r") 
        line_rpm = serialIO.readline().split(" ")
        print "rpm: ",line_rpm
	rpm = int("0x"+line_rpm[4]+line_rpm[5], 16)/4
        return rpm
    except:
        return 0

def maf(serialIO):
    #time.sleep(0.05)
    try:
        serialIO.write("01 10 \r")
        line_maf = serialIO.readline().split(" ")
        print "maf: ",line_maf
	maf = int("0x"+line_maf[4]+line_maf[5], 16)
        return maf
    except:
        return 0

def tp(serialIO):
    #time.sleep(0.07)
    try:
        serialIO.write("01 11 \r")
        line_tp = serialIO.readline().split(" ")
        print "tp: ", line_tp
	tp = int("0x"+line_tp[4], 16)*100/255
        return tp
    except:
        return 0
def kpl(maf,speed):
    try:
        x = speed*1000/maf
        MPG = (710.7*x)/1000
        KPL = int(MPG*0.425143707)
        return KPL
    except:
        return 0 
def startRecord(str_driverID,str_vehicleID):
	#try:
          serialIO = serial.Serial("/dev/ttyUSB0", 38400, timeout=0.24)
          with open('record.txt', 'a') as f:
		while True:
	  		r_speed = speed(serialIO)
                	r_rpm = rpm(serialIO)
               	 	r_maf = maf(serialIO)
                	r_tp = tp(serialIO)
			KPL = kpl(r_maf,r_speed) 
                	driverID = int(str_driverID)
			DID = str('%04d' % driverID)
			vehicleID = int(str_vehicleID)
			VID = str('%04d' % vehicleID) 
                	lcd_byte(LCD_LINE_1, LCD_CMD)
                	lcd_string("DID:"+DID+"    "+"VID:"+VID)
                	lcd_byte(LCD_LINE_2, LCD_CMD)
                	lcd_string(strftime("%d-%m-%Y")+"  "+strftime("%H:%M:%S"))
                	lcd_byte(LCD_LINE_3, LCD_CMD)
                	lcd_string("RPM:"+str('% 5d' % r_rpm)+ "   TP:" + str('% 3d' % r_tp)+" %")
                	lcd_byte(LCD_LINE_4, LCD_CMD)
                	lcd_string(str('% 3d'%r_speed)+" km/hr  "+str('% 2d' % KPL)+" km/l")
                	f.write("[did:"+DID+"],[vid:"+VID+"],<"+repr(strftime("%d-%m-%Y_%H:%M:%S"))+">, Speed:"+repr(r_speed)+ ", MAF:" +repr(r_maf)+ ", RPM:" +repr(r_rpm)+ ", TP:"+repr(r_tp)+", KPL:"+ repr(KPL)+"\n" )
			input_back = GPIO.input(22)
                	if input_back == False:
                			os.system("sudo halt")
	#except: 
          #main()
			
def driverCode():
    	d1=0
    	d2=0
    	d3=0
    	d4=0
    	while True: 
                lcd_byte(LCD_LINE_1, LCD_CMD)
                lcd_string("Enter Driver ID:")
                lcd_byte(LCD_LINE_2, LCD_CMD)
                lcd_string("")
                lcd_byte(LCD_LINE_3, LCD_CMD)
                lcd_string("     "+str(d1)+" _ _ _")
                lcd_byte(LCD_LINE_4, LCD_CMD)
                lcd_string("     ^")
                time.sleep(0.05) 
                input_up = GPIO.input(17)
                if input_up == False:
                        if d1>=9:
                            d1=9
                        else:
                            d1=d1+1
		time.sleep(0.05)   
                input_down = GPIO.input(27)
                if input_down == False:
                        if d1<=0:
                            d1=0
                        else:
                            d1=d1-1
		time.sleep(0.05)    
                input_back = GPIO.input(22)
                if input_back == False:
                    driverCode()
		time.sleep(0.05)       
                input_ok = GPIO.input(4)
                if input_ok == False:
                        while True: 
                            lcd_byte(LCD_LINE_1, LCD_CMD)
                            lcd_string("Enter Driver ID:")
                            lcd_byte(LCD_LINE_2, LCD_CMD)
                            lcd_string("")
                            lcd_byte(LCD_LINE_3, LCD_CMD)
                            lcd_string("     "+str(d1)+" "+str(d2)+" _ _")
                            lcd_byte(LCD_LINE_4, LCD_CMD)
                            lcd_string("       ^")
                            time.sleep(0.05)  
                            input_up = GPIO.input(17)
                            if input_up == False:
                                if d2>=9:
                                    d2=9
                                else:
                                    d2=d2+1
			    time.sleep(0.05) 
                            input_down = GPIO.input(27)
                            if input_down == False:
                                if d2<=0:
                                    d2=0
                                else:
                                    d2=d2-1
                            time.sleep(0.05) 
			    input_back = GPIO.input(22)
                            if input_back == False:
                                driverCode()              
                            time.sleep(0.05) 
			    input_ok = GPIO.input(4)
                            if input_ok == False:
                                    while True: 
                                        lcd_byte(LCD_LINE_1, LCD_CMD)
                                        lcd_string("Enter Driver ID:")
                                        lcd_byte(LCD_LINE_2, LCD_CMD)
                                        lcd_string("")
                                        lcd_byte(LCD_LINE_3, LCD_CMD)
                                        lcd_string("     "+str(d1)+" "+str(d2)+" "+str(d3)+" _")
                                        lcd_byte(LCD_LINE_4, LCD_CMD)
                                        lcd_string("         ^")
                                        time.sleep(0.05)  
                                        input_up = GPIO.input(17)
                                        if input_up == False:
                                            if d3>=9:
                                                d3=9
                                            else:
                                                d3=d3+1
					time.sleep(0.05)   
                                        input_down = GPIO.input(27)
                                        if input_down == False:
                                                if d3<=0:
                                                    d3=0
                                                else:
                                                    d3=d3-1
					time.sleep(0.05)  
                                        input_back = GPIO.input(22)
                                        if input_back == False:
                                            driverCode()
					time.sleep(0.05)       
                                        input_ok = GPIO.input(4)
                                        if input_ok == False:
                                                while True: 
                                                    lcd_byte(LCD_LINE_1, LCD_CMD)
                                                    lcd_string("Enter Driver ID:")
                                                    lcd_byte(LCD_LINE_2, LCD_CMD)
                                                    lcd_string("")
                                                    lcd_byte(LCD_LINE_3, LCD_CMD)
                                                    lcd_string("     "+str(d1)+" "+str(d2)+" "+str(d3)+" "+str(d4)+"")
                                                    lcd_byte(LCD_LINE_4, LCD_CMD)
                                                    lcd_string("           ^")
                                                    time.sleep(0.05)  
                                                    input_up = GPIO.input(17)
                                                    if input_up == False:
                                                        if d4>=9:
                                                            d4=9
                                                        else:
                                                            d4=d4+1
						    time.sleep(0.05)   
                                                    input_down = GPIO.input(27)
                                                    if input_down == False:
                                                        if d4<=0:
                                                            d4=0
                                                        else:
                                                            d4=d4-1
						    time.sleep(0.05) 
                                                    input_back = GPIO.input(22)
                                                    if input_back == False:
                                                        driverCode()
						    time.sleep(0.05) 
						    input_ok = GPIO.input(4)
                                                    if input_ok == False:
							str_driverID = ""+str(d1)+""+str(d2)+""+str(d3)+""+str(d4)+""
							vehicleCode(str_driverID)

def vehicleCode(str_driverID):
	vid1=0
    	vid2=0
   	vid3=0
    	vid4=0                                                        
	while True: 
                lcd_byte(LCD_LINE_1, LCD_CMD)
                lcd_string("Enter Vehicle ID:")
                lcd_byte(LCD_LINE_2, LCD_CMD)
                lcd_string("")
                lcd_byte(LCD_LINE_3, LCD_CMD)
                lcd_string("     "+str(vid1)+" _ _ _")
                lcd_byte(LCD_LINE_4, LCD_CMD)
                lcd_string("     ^")
                time.sleep(0.05) 
                input_up = GPIO.input(17)
                if input_up == False:
                        if vid1>=9:
                            vid1=9
                        else:
                            vid1=vid1+1
  		time.sleep(0.05) 
                input_down = GPIO.input(27)
                if input_down == False:
                        if vid1<=0:
                            vid1=0
                        else:
                            vid1=vid1-1
		time.sleep(0.05)    
                input_back = GPIO.input(22)
                if input_back == False:
                    driverCode()
		time.sleep(0.05)       
                input_ok = GPIO.input(4)
                if input_ok == False:
                        while True: 
                            lcd_byte(LCD_LINE_1, LCD_CMD)
                            lcd_string("Enter Vehicle ID:")
                            lcd_byte(LCD_LINE_2, LCD_CMD)
                            lcd_string("")
                            lcd_byte(LCD_LINE_3, LCD_CMD)
                            lcd_string("     "+str(vid1)+" "+str(vid2)+" _ _")
                            lcd_byte(LCD_LINE_4, LCD_CMD)
                            lcd_string("       ^")
                            time.sleep(0.05) 
                            input_up = GPIO.input(17)
                            if input_up == False:
                                if vid2>=9:
                                    vid2=9
                                else:
                                    vid2=vid2+1
			    time.sleep(0.05)   
                            input_down = GPIO.input(27)
                            if input_down == False:
                                if vid2<=0:
                                    vid2=0
                                else:
                                    vid2=vid2-1
			    time.sleep(0.05) 
                            input_back = GPIO.input(22)
                            if input_back == False:
                                driverCode()
			    time.sleep(0.05)               
                            input_ok = GPIO.input(4)
                            if input_ok == False:
                                    while True: 
                                        lcd_byte(LCD_LINE_1, LCD_CMD)
                                        lcd_string("Enter Vehicle ID:")
                                        lcd_byte(LCD_LINE_2, LCD_CMD)
                                        lcd_string("")
                                        lcd_byte(LCD_LINE_3, LCD_CMD)
                                        lcd_string("     "+str(vid1)+" "+str(vid2)+" "+str(vid3)+" _")
                                        lcd_byte(LCD_LINE_4, LCD_CMD)
                                        lcd_string("         ^")
                                        time.sleep(0.05)  
                                        input_up = GPIO.input(17)
                                        if input_up == False:
                                            if vid3>=9:
                                                vid3=9
                                            else:
                                                vid3=vid3+1
					time.sleep(0.05)   
                                        input_down = GPIO.input(27)
                                        if input_down == False:
                                                if vid3<=0:
                                                    vid3=0
                                                else:
                                                    vid3=vid3-1
					time.sleep(0.05)  
                                        input_back = GPIO.input(22)
                                        if input_back == False:
                                            driverCode()
					time.sleep(0.05)       
                                        input_ok = GPIO.input(4)
                                        if input_ok == False:
                                                while True: 
                                                    lcd_byte(LCD_LINE_1, LCD_CMD)
                                                    lcd_string("Enter Vehicle ID:")
                                                    lcd_byte(LCD_LINE_2, LCD_CMD)
                                                    lcd_string("")
                                                    lcd_byte(LCD_LINE_3, LCD_CMD)
                                                    lcd_string("     "+str(vid1)+" "+str(vid2)+" "+str(vid3)+" "+str(vid4)+"")
                                                    lcd_byte(LCD_LINE_4, LCD_CMD)
                                                    lcd_string("           ^")
                                                    time.sleep(0.05)  
                                                    input_up = GPIO.input(17)
                                                    if input_up == False:
                                                        if vid4>=9:
                                                            vid4=9
                                                        else:
                                                            vid4=vid4+1
						    time.sleep(0.05)   
                                                    input_down = GPIO.input(27)
                                                    if input_down == False:
                                                        if vid4<=0:
                                                            vid4=0
                                                        else:
                                                            vid4=vid4-1
						    time.sleep(0.05) 
                                                    input_back = GPIO.input(22)
                                                    if input_back == False:
                                                        driverCode()
						    time.sleep(0.05) 
						    input_ok = GPIO.input(4)
                                                    if input_ok == False:
							str_vehicleID = ""+str(vid1)+""+str(vid2)+""+str(vid3)+""+str(vid4)+""
							startRecord(str_driverID,str_vehicleID)

if __name__ == '__main__':
    main()
