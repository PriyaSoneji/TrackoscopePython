#include <ezButton.h>

#define EN        8      //Stepper Motor Enable, Active Low Level 
#define X_DIR    5      //X-Axis Stepper Motor Direction Control 
#define Y_DIR    6     //Y-Axis Stepper Motor Direction Control 
#define X_STP    2    //X-Axis Stepper Control 
#define Y_STP   3    //Y-Axis Stepper Control

#define VRX_PIN  A0 // Arduino pin connected to VRX pin
#define VRY_PIN  A1 // Arduino pin connected to VRY pin
#define SW_PIN   13  // Arduino pin connected to SW  pin

ezButton button(SW_PIN);

int dirx =0;
int stepss = 50;
int stepsl = 10;
char chardir;
int diry = 0;

int xValue = 0; // To store value of the X axis
int yValue = 0; // To store value of the Y axis
int bValue = 0; // To store value of the button

boolean joymove = false;

void step(boolean dir, byte dirPin, byte stepperPin, int steps)
{
  digitalWrite(dirPin, dir);
  for (int i = 0; i < steps; i++) {
    digitalWrite(stepperPin, HIGH);
    delayMicroseconds(800);
    digitalWrite(stepperPin, LOW);
    delayMicroseconds(800);
  }
  delayMicroseconds(100);
}


void setup() {
  pinMode(X_DIR, OUTPUT);
  pinMode(X_STP, OUTPUT);
  pinMode(Y_DIR, OUTPUT); 
  pinMode(Y_STP, OUTPUT);
  pinMode(EN, OUTPUT);
  digitalWrite(EN, HIGH);
  Serial.begin(115200);
  button.setDebounceTime(100); 

}

void loop() {
  bValue = button.getState();
  
  if (button.isPressed()) {
    joymove = !joymove;
  }

  if(joymove) {
    xValue = analogRead(VRX_PIN);
    yValue = analogRead(VRY_PIN);

    if (yValue > 750) {
      digitalWrite(EN, LOW);
      diry = 1;
    } else if (yValue < 250) {
      digitalWrite(EN, LOW);
      diry = -1;
    } else {
      diry = 0;
      digitalWrite(EN, HIGH);
    }

    if (xValue > 750) {
      digitalWrite(EN, LOW);
      dirx = 1;
    } else if (xValue < 250) {
      digitalWrite(EN, LOW);
      dirx = -1;
    } else {
      dirx = 0;
      digitalWrite(EN, HIGH);
    }
    
  }

  // Moving the platform
  if (dirx == -1) {
    step(false, X_DIR, X_STP, stepsl);
  }
  if (dirx == 1) {
    step(true, X_DIR, X_STP, stepsl);
  }
  if (diry == -1) {
    step(false, Y_DIR, Y_STP, stepsl);
  }
  if (diry == 1) {
    step(true, Y_DIR, Y_STP, stepsl);
  }
}
