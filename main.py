import machine
import time
import random
import ustruct

from machine import Pin, ADC
#customize behavior below
#=====================1====2====3====4====5====6====7====8====9===10#
midiOut1Note     = [ 48,  49,  50,  51,  52,  53,  54,  55,  56,  57] #MidiNote for each digital input. If you put 128 then it is ignored
midiOut2Note     = [ 48,  49,  50,  51,  52,  53,  54,  55,  56,  57] #MidiNote for each digital input
midiOut1Channel  = [ 10,  10,  10,  10,  10,  10,  10,  10,  10,  10]
midiOut2Channel  = [ 10,  10,  10,  10,  10,  10,  10,  10,  10,  10]
midiOut1Velocity = [127, 127, 127, 127, 127, 127, 127, 127, 127, 127]
midiOut2Velocity = [127, 127, 127, 127, 127, 127, 127, 127, 127, 127]
#=====================================================================

midiStart    = 0xFA
midiStop     = 0xFC
midiContinue = 0xFB
midiProg     = 0xC0
uart0 = machine.UART(0,31250)
uart1 = machine.UART(1,31250)

#digital pin debounce period in ms
debounceDigital = 20

# array that holds the last time a note was sent for each part. Used for debounce
lastNoteSent = [ 0,0,0,0,0,0,0,0,0,0]
lastStartStopSent = 0

parts = [Pin(22, Pin.IN), Pin(1, Pin.IN), Pin(2, Pin.IN), Pin(3, Pin.IN), Pin(16, Pin.IN),
         Pin(7, Pin.IN), Pin(8, Pin.IN), Pin(9, Pin.IN), Pin(10, Pin.IN), Pin(11, Pin.IN)]

startStop = Pin(12, Pin.IN)
SW1 = Pin(13, Pin.IN)
SW1Value = 0;
SW2 = Pin(14, Pin.IN)
SW2Value = 0;
isPlaying = 0             
knob = machine.ADC(26)
aIn = machine.ADC(27)
         

def sendNoteOnMidi1(channel, note, vol):
    uart0.write(ustruct.pack("bbb",(0x90 | channel),note,vol))
def sendNoteOnMidi2(channel, note, vol):
    uart1.write(ustruct.pack("bbb",(0x90 | channel),note,vol))
def sendNoteOffMidi1(channel, note, vol):
    uart0.write(ustruct.pack("bbb",(0x80 | channel),note,vol))
def sendNoteOffMidi2(channel, note, vol):    
    uart1.write(ustruct.pack("bbb",(0x90 | channel),note,vol))
def sendStart():
    uart0.write(ustruct.pack("b",midiStart))
    uart1.write(ustruct.pack("b",midiStart))
def sendStop():
    uart0.write(ustruct.pack("b",midiStop))
    uart1.write(ustruct.pack("b",midiStop))
def sendContinue():
    uart0.write(ustruct.pack("b",midiContinue))
    uart1.write(ustruct.pack("b",midiContinue))  
def sendChange():
    uart0.write(ustruct.pack("bb",midiProg,0x00))
    uart1.write(ustruct.pack("bb",midiProg,0x00))
def sendCC(channel, cc, aValue):
    uart0.write(ustruct.pack("bbb",0xB0 + channel, cc, aValue))
    uart1.write(ustruct.pack("bbb",0xB0 + channel, cc, aValue))

loopCounter = 0
aNote = 0
currentTime = 0
def processDigitalInputs():
    global isPlaying
    global parts
    global lastNoteSent
    global lastStartStopSent
    for a in range(10):
        currentTime = time.ticks_ms()    
        if parts[a].value() == 0 and (currentTime-lastNoteSent[a] > debounceDigital):
            lastNoteSent[a] = currentTime
            if midiOut1Note[a] != 128:
                sendNoteOnMidi1 (midiOut1Channel[a]-1,midiOut1Note[a],midiOut1Velocity[a])
                sendNoteOffMidi1(midiOut1Channel[a]-1,midiOut1Note[a],midiOut1Velocity[a])
            if midiOut2Note[a] != 128:
                sendNoteOnMidi2 (midiOut2Channel[a]-1,midiOut2Note[a],midiOut2Velocity[a])
                sendNoteOffMidi2(midiOut2Channel[a]-1,midiOut2Note[a],midiOut2Velocity[a])
            
    if startStop.value() == 0 and (currentTime-lastStartStopSent > (debounceDigital*3)):
        lastStartStopSent = currentTime
        if isPlaying == 1:
            sendStop()
            isPlaying = 0
        else:
            if SW2Value == 1:
                sendStart()
            else:
                sendContinue()
            isPlaying = 1
            
def processAnalogInputs():
    reading = knob.read_u16()
    reading2 = aIn.read_u16()
    #print("ADC: ",reading2)
    SW1Value = SW1.value()
    SW2Value = SW2.value()
    
### MAIN LOOP
while True:
    loopCounter +=1
    processDigitalInputs()
    if loopCounter > 1000:
       processAnalogInputs()
       loopCounter = 0

    
                           

            
        
        
    
    
    

        