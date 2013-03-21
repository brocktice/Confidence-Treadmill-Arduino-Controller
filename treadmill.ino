#include "delay_x.h"

// Note: Pin 3 controls the pulses to the motor
//       Pin 2 must be on to enable the circuit via NPN transistor
//       Pin 2 should be off on boot and anytime thereafter where the treadmill is not expected to be on

float pw = 1.;
float newpw = 1.;
float mph;
int frequency = 40;
float period;
int ontime;
int offtime;
char num = -1;
char inChar = -1;
char inData[20];
byte index = 0;
int debug = 1;
int pwint = 1;
float pwmlimit = 0.65; // about 4.3 mph, lower is faster

// onMask: control pin high, transistor on
unsigned char onMask = B00001100;
// offMask: control pin low, transistor on
unsigned char offMask = B0000100;
// disabledMask: control pin high, transistor off
unsigned char disabledMask = B00001000;
char* endptr;

int loopcount = 0;
int looplimit = 40;

void setup() {    
  // for safety: very first thing is turn the transistor off
  // set output and turn pin on (turns treadmill off)
  DDRD = DDRD | B11111100;
  PORTD = disabledMask;
  period = 1000000/frequency;
  Serial.begin(115200);  
}

void loop() {
  if(pw < pwmlimit || pw > 0.99){
    PORTD = disabledMask;
  }else{
   // only break out of this loop every looplimit iterations to check serial
    while(loopcount < looplimit){
      PORTD = offMask;
      _delay_us(offtime); 
      PORTD = onMask;
      _delay_us(ontime);
      loopcount++;
    }
    loopcount = 0;
  }
  
  if(Serial.available() > 0){
     // this is meant to bridge the transistion, needs work
     // Ideally I can clock the treadmill at the board's natural pwm and just use analog full time
    pwint = (int)(pw*1.0*255);
    if(pwint > 255){
      pwint = 255;
    }
    analogWrite(3,pwint);

    // now read
    Serial.readBytesUntil('\n', inData, 19);
    // attempt to read into a temporary variable so as not to mess with current pw
    newpw = strtod(inData, &endptr);
    // if it failed, pw remains what it was before
    // I was setting it to 0 but that stops the treadmill suddenly
    // strtod sets endptr == inData if it fails to parse properly
    if(inData != endptr){
      // limit speed to pwmlimit set above
        if(newpw < pwmlimit){
           newpw = pwmlimit;
        }
        // if everything was successful we update the pw (max set), else leave it as it was
        pw=newpw;
        ontime = (int)(pw*period);
        offtime = period-ontime;  
    }
     
    // get us out of analog mode
    digitalWrite(3, HIGH);

  }


}

