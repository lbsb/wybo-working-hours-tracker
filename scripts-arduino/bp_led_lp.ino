// ######## CONST ########
const int BUTTON_PIN = 3;           // the number of the pushbutton pin
const int LED_PIN =  2;             // the number of the LED pin
const String CONST_ID = "01";       // the main Id
const String CONST_TYPE = "01";     // the id of press button

// ######## DEF ########
#define LONGPRESS_LEN    40         // Min nr of loops for a long press
#define DELAY            20         // Delay per loop in ms
#define DELAY_BLINK      50000
// ######## VAR ########
int buttonState = 0;                // variable for reading the pushbutton status
int ledState = 0;                   // variable for the led state
int currenteState = 0;              // temp variable
int button_pressed_counter;         // press running duration
boolean button_was_pressed;         // previous state

boolean serialReadTemp = false;
boolean isSync = false;
// ######## ENUM ########
enum {
    EV_NONE=0,
    EV_SHORTPRESS,
    EV_LONGPRESS
};

enum {
    VAL_OFF = 0,
    VAL_ON = 1,
    VAL_DESC = 2,
    VAL_SYNC = 3,
    VAL_END_SYNC = 4,
    VAL_WAIT_SYNC = 5
};
// ######## SETUP ########
void setup() {
    Serial.begin(9600);
    pinMode(LED_PIN, OUTPUT);          // initialize the LED pin as an output:
    pinMode(BUTTON_PIN, INPUT);        // initialize the pushbutton pin as an input:
    button_was_pressed = false;        // initialize the pushbutton to false (not pressed)
    button_pressed_counter = 0;        // initialize the pusbutton counter
}

// ######## LOOP ########
void loop(){
    int eventResult = handle_button();
    int serialReadTemp = Serial.read();
    if(serialReadTemp == 51)            // 51 is Hexa symbol for 3
    {
        turnBlink();
    }
    else if(serialReadTemp == 48)       // 48 is Hexa symbol for 0
    {
      turnOff();                
    }
    switch(eventResult){
        case EV_NONE:               // if nothing append
            //TODO : Ne rien faire de particulier, ou attendre la fin d'une synchronisation
            
            break;
        case EV_SHORTPRESS:         // if short press
            //TODO : Allumer ou éteindre la LED (a check)
            if(digitalRead(LED_PIN) == HIGH)
                    turnOff();
            else
                    turnOn();
            break;
        case EV_LONGPRESS:          // if long press
            //TODO : Faire clignoter la LED et attendre la fin d'une synchronisation.
            syncArduino();
            turnBlink();
            break;
    }
    delay(DELAY);
}

// ####### Function ########
int handle_button(){
    int event;
    int button_now_pressed = !digitalRead(BUTTON_PIN); // pin low -> pressed

    if (!button_now_pressed && button_was_pressed) {
        if (button_pressed_counter < LONGPRESS_LEN)
            event = EV_SHORTPRESS;
        else
            event = EV_LONGPRESS;
    }
    else
        event = EV_NONE;

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
    Serial.println(VAL_ON);
}

// turn LED Off:
void turnOff(){
    digitalWrite(LED_PIN, LOW);
    Serial.println(VAL_OFF);
}
void syncArduino(){
    Serial.println(VAL_SYNC);
}
void turnBlink(){
    for (int i=0; i <= 255; i++){
        if(!isSync){
            if(serialReadTemp != VAL_END_SYNC){
                int serialReadTemp = Serial.read();
                
                if (serialReadTemp == 52){      // 52 is Hexa Symbol for 4
                    isSync = true;
                }
                digitalWrite(LED_PIN, HIGH);    // turn the LED on
                delay(100);                     // wait for a second
                digitalWrite(LED_PIN, LOW);     // turn the LED off
                delay(100);                     // wait for a second
            }
        }
        else{
            Serial.println(VAL_END_SYNC);
            break;  
        }
    }
    isSync = false;
}
