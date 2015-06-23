// ######## CONST ########
const int BUTTON_PIN = 3;           // the number of the pushbutton pin
const int LED_PIN =  2;             // the number of the LED pin
const String CONST_ID = "01";       // the main Id
const String CONST_TYPE = "01";     // the id of press button

// ######## VAR ########
int buttonState = 0;                // variable for reading the pushbutton status
int ledState = 0;                   // variable for the led state
int currenteState = 0;              // temp variable
int button_pressed_counter;         // press running duration
boolean button_was_pressed;         // previous state

// ######## ENUM ########
enum {
    EV_NONE=0,
    EV_SHORTPRESS=1,
    EV_LONGPRESS=2
};

// ######## SETUP ########
void setup() {
    Serial.begin(9600);
    pinMode(ledPin, OUTPUT);          // initialize the LED pin as an output:
    pinMode(buttonPin, INPUT);        // initialize the pushbutton pin as an input:
    button_was_pressed = false;       // initialize the pushbutton to false (not pressed)
    button_pressed_counter = 0;       // initialize the pusbutton counter
}

// ######## LOOP ########
void loop(){
    boolean eventResult = eventButton();

    switch(eventResult){
        case EV_NONE:               // if nothing append
            //TODO : Ne rien faire de particulier, ou attendre la fin d'une synchronisation
            break;
        case EV_SHORTPRESS:         // if short press
            //TODO : Allumer ou éteindre la LED (a check)
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
            break;
        case EV_LONGPRESS:          // if long press
            //TODO : Faire clignoter la LED et attendre la fin d'une synchronisation.
            break;
    }
}

// ####### Function ########
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


// ######## METHODES ########
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
