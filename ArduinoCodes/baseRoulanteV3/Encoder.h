 #ifndef __ENCODER_H__
#define __ENCODER_H__

#include "arduino.h"

class Encoder {
    /*
      wraps encoder setup and update functions in a class

      !!! NOTE : user must call the encoders update method from an
      interrupt function himself! i.e. user must attach an interrupt to the
      encoder pin A and call the encoder update method from within the
      interrupt

      uses Arduino pull-ups on A & B channel outputs
      turning on the pull-ups saves having to hook up resistors
      to the A & B channel outputs

      // ------------------------------------------------------------------------------------------------
      // Example usage :
      // ------------------------------------------------------------------------------------------------
          #include "Encoder.h"

          Encoder encoder(2, 4);

          void setup() {
              attachInterrupt(0, doEncoder, CHANGE);
              Serial.begin (115200);
              Serial.println("start");
          }

          void loop(){
              // do some stuff here - the joy of interrupts is that they take care of themselves
          }

          void doEncoder(){
              encoder.update();
              Serial.println( encoder.getPosition() );
          }
      // ------------------------------------------------------------------------------------------------
      // Example usage end
      // ------------------------------------------------------------------------------------------------
    */
  public:

    // constructor : sets pins as inputs and turns on pullup resistors

    Encoder( int8_t PinA, int8_t PinB, bool _reversed) : pin_a ( PinA), pin_b( PinB ), reversed(_reversed) {
      // set pin a and b to be input
      pinMode(pin_a, INPUT);
      pinMode(pin_b, INPUT);
      // and turn on pull-up resistors
      digitalWrite(pin_a, HIGH);
      digitalWrite(pin_b, HIGH);
    };

    // call this from your interrupt function

    void update () {
      if (digitalRead(pin_a)) digitalRead(pin_b) ? position++ : position--;
      else digitalRead(pin_b) ? position-- : position++;
    };

    // returns current position

    long int getPosition () {
      return reversed?(-position):position;
    };

    // set the position value

    void setPosition ( const long int p) {
      position = p;
    };

  private:

    long int position;

    int8_t pin_a;

    int8_t pin_b;

    bool reversed;
};

#endif // __ENCODER_H__
