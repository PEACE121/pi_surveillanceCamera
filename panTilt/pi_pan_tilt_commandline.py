#!/usr/bin/env python
import time
import os
import sys
import RPIO
import RPIO.PWM

PWM_FREQUENCY = 50    # Hz

PWM_DMA_CHANNEL = 0
PWM_SUBCYLCLE_TIME_US = 1000/PWM_FREQUENCY * 1000
PWM_PULSE_INCREMENT_US = 10

PAN_PWM_PIN = 23
TILT_PWM_PIN = 24

ABSOLUTE_MIN_PULSE_WIDTH_US = 500
ABSOLUTE_MAX_PULSE_WIDTH_US = 2500

EXPLORE_PAN_START_ANGLE = 45.0;
EXPLORE_PAN_END_ANGLE = 135.0;
EXPLORE_TILT_START_ANGLE = 130.0;
EXPLORE_TILT_END_ANGLE = 50.0;

EXPLORE_ABS_PAN_STEP = 1;
EXPLORE_ABS_TILT_STEP = 5;

#-------------------------------------------------------------------------------
class ServoPWM:
    
    #---------------------------------------------------------------------------
    def __init__( self, pwmPin, minAnglePulseWidthPair, 
        midAnglePulseWidthPair, maxAnglePulseWidthPair ):
        
        # Check that the given angles are valid
        assert( minAnglePulseWidthPair[ 0 ] >= 0 )
        assert( midAnglePulseWidthPair[ 0 ] > minAnglePulseWidthPair[ 0 ] )
        assert( midAnglePulseWidthPair[ 0 ] < maxAnglePulseWidthPair[ 0 ] )
        assert( maxAnglePulseWidthPair[ 0 ] <= 180 )
        
        self.pwmPin = pwmPin
        self.minAnglePulseWidthPair = minAnglePulseWidthPair
        self.midAnglePulseWidthPair = midAnglePulseWidthPair
        self.maxAnglePulseWidthPair = maxAnglePulseWidthPair
        self.lastPulseWidthSet = None
    
    #---------------------------------------------------------------------------
    def setCommand( self, command ):
        
        # Work out whether the command is an angle, or a pulse width
        if command >= ABSOLUTE_MIN_PULSE_WIDTH_US:
            self.setPulseWidth( command )
        else:
            self.setAngle( command )
    
    #---------------------------------------------------------------------------
    def setPulseWidth( self, pulseWidth ):
        
        # Constrain the pulse width
        if pulseWidth < ABSOLUTE_MIN_PULSE_WIDTH_US:
            pulseWidth = ABSOLUTE_MIN_PULSE_WIDTH_US
        if pulseWidth > ABSOLUTE_MAX_PULSE_WIDTH_US:
            pulseWidth = ABSOLUTE_MAX_PULSE_WIDTH_US
        
        # Ensure that the pulse width is an integer multiple of the smallest 
        # possible pulse increment
        pulseIncrementUS = RPIO.PWM.get_pulse_incr_us()
        numPulsesNeeded = int( pulseWidth/pulseIncrementUS )
        pulseWidth = numPulsesNeeded * pulseIncrementUS
    
        if pulseWidth != self.lastPulseWidthSet:
        
            RPIO.PWM.add_channel_pulse( PWM_DMA_CHANNEL, self.pwmPin, 0, numPulsesNeeded )
            self.lastPulseWidthSet = pulseWidth
    
    #---------------------------------------------------------------------------
    def setAngle( self, angle ):
        
        # Constrain the angle
        if angle < self.minAnglePulseWidthPair[ 0 ]:
            angle = self.minAnglePulseWidthPair[ 0 ]
        if angle > self.maxAnglePulseWidthPair[ 0 ]:
            angle = self.maxAnglePulseWidthPair[ 0 ]
            
        # Convert the angle to a pulse width using linear interpolation
        if angle < self.midAnglePulseWidthPair[ 0 ]:
            
            angleDiff = self.midAnglePulseWidthPair[ 0 ] - self.minAnglePulseWidthPair[ 0 ]
            startPulseWidth = self.minAnglePulseWidthPair[ 1 ]
            pulseWidthDiff = self.midAnglePulseWidthPair[ 1 ] - self.minAnglePulseWidthPair[ 1 ]
            
            interpolation = float( angle - self.minAnglePulseWidthPair[ 0 ] ) / angleDiff
            
            pulseWidth = startPulseWidth + interpolation*pulseWidthDiff
            
        else:
            
            angleDiff = self.maxAnglePulseWidthPair[ 0 ] - self.midAnglePulseWidthPair[ 0 ]
            startPulseWidth = self.midAnglePulseWidthPair[ 1 ]
            pulseWidthDiff = self.maxAnglePulseWidthPair[ 1 ] - self.midAnglePulseWidthPair[ 1 ]
            
            interpolation = float( angle - self.midAnglePulseWidthPair[ 0 ] ) / angleDiff
            
            pulseWidth = startPulseWidth + interpolation*pulseWidthDiff
        
        print "Converted angle {0} to pulse width {1}".format( angle, pulseWidth )
        
        # Now set the pulse width
        self.setPulseWidth( pulseWidth )

#-------------------------------------------------------------------------------
def finishedPanningForward( curPanAngle ):
        
    if EXPLORE_PAN_START_ANGLE < EXPLORE_PAN_END_ANGLE:
        return curPanAngle >= EXPLORE_PAN_END_ANGLE
    else:
        return curPanAngle <= EXPLORE_PAN_END_ANGLE
        
#-------------------------------------------------------------------------------
def finishedPanningBackward( curPanAngle ):
        
    if EXPLORE_PAN_START_ANGLE < EXPLORE_PAN_END_ANGLE:
        return curPanAngle <= EXPLORE_PAN_START_ANGLE
    else:
        return curPanAngle >= EXPLORE_PAN_START_ANGLE
        
#-------------------------------------------------------------------------------
def finishedTiltingForward( curTiltAngle ):
        
    if EXPLORE_TILT_START_ANGLE < EXPLORE_TILT_END_ANGLE:
        return curTiltAngle >= EXPLORE_TILT_END_ANGLE
    else:
        return curTiltAngle <= EXPLORE_TILT_END_ANGLE
        
#-------------------------------------------------------------------------------
def finishedTiltingBackward( curTiltAngle ):
        
    if EXPLORE_TILT_START_ANGLE < EXPLORE_TILT_END_ANGLE:
        return curTiltAngle <= EXPLORE_TILT_START_ANGLE
    else:
        return curTiltAngle >= EXPLORE_TILT_START_ANGLE
        
#-------------------------------------------------------------------------------
# Create ServoPWM instances to control the servos
panServoPWM = ServoPWM( PAN_PWM_PIN, 
    minAnglePulseWidthPair=( 45.0, 1850 ), 
    midAnglePulseWidthPair=( 90.0, 1400 ), 
    maxAnglePulseWidthPair=( 135.0, 1000.0 ) )
tiltServoPWM = ServoPWM( TILT_PWM_PIN, 
    minAnglePulseWidthPair=( 45.0, 1850 ), 
    midAnglePulseWidthPair=( 90.0, 1500 ), 
    maxAnglePulseWidthPair=( 180.0, 500.0 ) )

# Setup RPIO, and prepare for PWM signals
RPIO.setmode( RPIO.BCM )

RPIO.PWM.setup( pulse_incr_us=PWM_PULSE_INCREMENT_US )
RPIO.PWM.init_channel( PWM_DMA_CHANNEL, PWM_SUBCYLCLE_TIME_US )
    
try:
        print sys.argv[1]
	panServoPWM.setAngle( int( sys.argv[1] ) )
	tiltServoPWM.setAngle( int( sys.argv[2] ) )

	time.sleep( 0.5 )

except Exception as e:
    
    print "Got exception", e
    
finally:
    RPIO.PWM.clear_channel_gpio( PWM_DMA_CHANNEL, panServoPWM.pwmPin )
    RPIO.PWM.clear_channel_gpio( PWM_DMA_CHANNEL, tiltServoPWM.pwmPin )
    
    RPIO.PWM.cleanup()
    RPIO.cleanup()
