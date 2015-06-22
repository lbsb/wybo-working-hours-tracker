
// constants won't change. They're used here to
// set pin numbers:
const int buttonPin = 3;     // the number of the pushbutton pin
const int ledPin =  2;      // the number of the LED pin



// variables will change:
int buttonState = 0;         // variable for reading the pushbutton status
int ledState = 0;
int currenteState = 0;

void setup() {
  // initialize the LED pin as an output:
  pinMode(ledPin, OUTPUT);     
  // initialize the pushbutton pin as an input:
  pinMode(buttonPin, INPUT);
  Serial.print("By SB & LB");     
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
   Serial.println("LED ON");
}

// turn LED Off:
void turnOff(){
  digitalWrite(ledPin, LOW);
  Serial.println("LED OFF");
}
