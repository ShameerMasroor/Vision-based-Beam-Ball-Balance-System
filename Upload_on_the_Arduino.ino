/* Example for MobaTools
  Moving a stepper back and forth controlled by serial monitor
*/
#include <MobaTools.h>

// Adjust pins, steps, and time as needed
const byte stepPin = 3;
const byte dirPin = 2;
const int stepsPerRev = 1600;  // Steps per Revolution ( example with 1/8 microsteps )(changed from 1600)
long targetPos = 0;            // Initial target position
long nextPos = 0;
int checker;
//int relay =4;

MoToStepper myStepper ( stepsPerRev, STEPDIR );
MoToTimer stepperPause;          // Pause between stepper moves
bool stepperRunning;

enum StepperState {
  IDLE,
  MOVING
};

StepperState stepperState = IDLE;

void setup() {
//  digitalWrite(relay,HIGH);
  myStepper.attach( stepPin, dirPin );
  myStepper.setSpeed( 5000 ); // 60 Rev/Min ( if stepsPerRev is set correctly )
  myStepper.setRampLen( 150 );
  Serial.begin(115200);
//  pinMode(relay,OUTPUT);
//  digitalWrite(relay,LOW);

  stepperRunning = true;
}

void loop() {
  // Check if there is any data available on the serial port
  if (Serial.available()) {
    // Read the next position from the serial port
    
    checker = Serial.parseInt();
    if (checker!=0)    //uncomment this in the case of erratic behavioud
    nextPos = checker;
    if (nextPos != targetPos) {
      if (nextPos>30){
        targetPos = 30;
      }
      else if (nextPos<-30){
        
        targetPos = -30;
      }
      else{
        targetPos=nextPos;
      }
      
      stepperState = IDLE; // Change state to IDLE to allow a new move
    }
  }

  // State machine to control the stepper
  switch (stepperState) {
    case IDLE:
      if (!myStepper.moving()) {
        myStepper.moveTo(targetPos);
        stepperState = MOVING;
      }
      break;
    case MOVING:
      if (!myStepper.moving()) {
        stepperState = IDLE;
      }
      break;
  }
}
