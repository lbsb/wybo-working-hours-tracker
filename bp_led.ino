
// constants won't change. They're used here to
// set pin numbers:
const int buttonPin = 3;        // the number of the pushbutton pin
const int ledPin =  2;          // the number of the LED pin
const String CONST_ID = "01";   // the main Id 
const String CONST_TYPE = "01"; // the id of press button



// variables will change:
int buttonState = 0;            // variable for reading the pushbutton status
int ledState = 0;
int currenteState = 0;


void setup() {
  Serial.begin(9600);
  // initialize the LED pin as an output:
  pinMode(ledPin, OUTPUT);     
  // initialize the pushbutton pin as an input:
  pinMode(buttonPin, INPUT);
}


void loop(){
  // read the state of the pushbutton value:
  buttonState = digitalRead(buttonPin);
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

// turn LED on:
void turnOn(){
   digitalWrite(ledPin, HIGH);
   Serial.println(CONST_ID+":"+CONST_TYPE+":1");
}

// turn LED Off:
void turnOff(){
  digitalWrite(ledPin, LOW);
  Serial.println(CONST_ID+":"+CONST_TYPE+":2");
}
