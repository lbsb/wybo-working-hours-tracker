// #### Constantes ###
const int buttonPin = 3;        // the number of the pushbutton pin
const int ledPin =  2;          // the number of the LED pin
const String CONST_ID = "01";   // the main Id
const String CONST_TYPE = "01"; // the id of press button


// variables will change:
int buttonState = 0;            // variable for reading the pushbutton status
int ledState = 0;
int currenteState = 0;

enum {
  EV_NONE=0,
  EV_SHORTPRESS,
  EV_LONGPRESS
};

boolean button_was_pressed;     // previous state
int button_pressed_counter;     // press running duration

// ############## SETUP ############################

void setup() {
  Serial.begin(9600);
  pinMode(ledPin, OUTPUT);        // initialize the LED pin as an output:
  pinMode(buttonPin, INPUT);      // initialize the pushbutton pin as an input:
  button_was_pressed = false;     // initialize the pushbutton to false (not pressed)
  button_pressed_counter = 0;     // initialize the pusbutton counter
}

// ############## LOOP ############################
void loop(){
  boolean eventResult = eventButton();

  switch(eventResult){
    case EV_NONE:
      //TODO
      break;
    case EV_SHORTPRESS:
      //TODO
      break;
    case EV_LONGPRESS:
      //TODO
      break;
  }
}

void loop(){
  buttonState = digitalRead(buttonPin);     // read the state of the pushbutton value:
  ledState = digitalRead(ledPin);

  // Wait until the button be pushed
  while (buttonState == digitalRead(buttonPin)) { };

  if(ledState == HIGH){
    if (buttonState == LOW) {
      turnOff();
    }
  }
  else{
    if (buttonState == LOW) {
      turnOn();
    }
  }
}

// ############## METHODES ############################

// turn LED on:
void turnOn(){
   digitalWrite(ledPin, HIGH);
   Serial.println(CONST_ID+":"+CONST_TYPE+":1");
}

// turn LED Off:
void turnOff(){
  digitalWrite(ledPin, LOW);
  Serial.println(CONST_ID+":"+CONST_TYPE+":0");
}
