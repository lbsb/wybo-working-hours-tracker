// #### Constantes ###
const int BUTTON_PIN = 3;        // the number of the pushbutton pin
const int LED_PIN =  2;          // the number of the LED pin
const String CONST_ID = "01";   // the main Id
const String CONST_TYPE = "01"; // the id of press button


// variables will change:
int buttonState = 0;            // variable for reading the pushbutton status
int ledState = 0;
int currenteState = 0;

enum {
  EV_NONE=0,
  EV_SHORTPRESS=1,
  EV_LONGPRESS=2
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

int handle_button(){
    int event;
    int button_now_pressed = !digitalRead(BUTTON_PIN); // pin low -> pressed

    if (!button_now_pressed && button_was_pressed) {
        if (button_pressed_counter < LONGPRESS_LEN){
            event = EV_SHORTPRESS;
        }
        else{
            event = EV_LONGPRESS;
        }
    }
    else{
            event = EV_NONE;
    }

    if (button_now_pressed)
        ++button_pressed_counter;
    else
        button_pressed_counter = 0;

    button_was_pressed = button_now_pressed;
    return event;
}

// ############ END LOOP #####################"""
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
   digitalWrite(LED_PIN, HIGH);
   Serial.println(CONST_ID+":"+CONST_TYPE+":1");
}

// turn LED Off:
void turnOff(){
  digitalWrite(LED_PIN, LOW);
  Serial.println(CONST_ID+":"+CONST_TYPE+":0");
}
