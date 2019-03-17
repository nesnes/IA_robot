#ifndef MBED_MOTOR_STEPPER_H
#define MBED_MOTOR_STEPPER_H

#define PERIOD_MIN 2000//0.020f
#define PERIOD_MAX 200//0.00055f //0.00055f

/** Interface to control a standard Stepper motor 
 *
 * with an A4988 controller using a PwmOut for speed and a DigitalOut for direction
 */
class Motor {
public:

    /** Create a motor control interface    
     *
     * @param pwm A PwmOut pin, driving the controller steps
     * @param dir A DigitalOut, set high when the motor should go forward
     */
    inline Motor(int pwm, int dir, float minSpeed=0, bool inverted=false):
        _pwm(pwm), _dir(dir), _minSpeed(minSpeed), _speed(0.f), _inverted(1), _period(0) {
        if(inverted)
            _inverted = -1;
        pinMode(pwm, OUTPUT);
        pinMode(dir, OUTPUT);
    }
    
    /** Set the speed of the motor
     * 
     * @param speed The speed of the motor as a normalised value between -1.0 and 1.0
     */
    inline void speed(float speed, bool allowOverRange=false) {
        //if(fabs(speed)<0.001) speed=0;
        if(speed != 0){
            _direction = speed>0? 1 : -1 ;
            if(!allowOverRange){
                if(speed<-1.0f) speed = -1.0f;
                if(speed>1.0f) speed = 1.0f;
            }
            _speed = _inverted * (_minSpeed + fabs(speed)*(1.0f-_minSpeed)) * (float)(1.0f+(speed<0)*-2.0f);
            digitalWrite(_dir, _speed > 0.0f);
            //float period = fabs(PERIOD_MIN - fabs(PERIOD_MIN - PERIOD_MAX) * sin(fabs(speed)*0.5*3.14156));
            //float period = fabs(PERIOD_MIN - fabs(PERIOD_MIN - PERIOD_MAX) * sqrt(fabs(speed)));
            float period = 0;
            if(fabs(speed)<=1)
                period = fabs(PERIOD_MIN - fabs(PERIOD_MIN - PERIOD_MAX) *  ( 2.0f*(sqrt(fabs(_speed)) - 0.5f*fabs(_speed)) )  ); //best curve for now f(x)=2*(sqrt(x)-0.5x)
            else
                period = fabs(PERIOD_MAX / _speed);
            _period = period;
        }
        else{
            _period = 0;
            _speed = 0;
        }
    }
    
    inline float getSpeed() {
        return _inverted * _speed;
    }

    inline void spinUpdate(){
        unsigned long currTime = micros();
        if(_period == 0 || currTime<last_call_time){ //handle micros overflow
            last_call_time = currTime;
        }
        if(_period > 0 && _speed != 0 && currTime-last_call_time>_period){
            pinState = !pinState;
            digitalWrite(_pwm, pinState);
            last_call_time = currTime;
            _direction<0.0f?position++:position--;
        }
    }
    
    inline long int getPosition () {
      return _inverted?(-position):position;
    };

    // set the position value

    inline void setPosition ( const long int p) {
      position = p;
    };

protected:
    long int position;
    int _direction;
    int _pwm;
    int _period;
    int _dir;
    float _speed;
    float _minSpeed;
    float _inverted;
    bool pinState = 0;
    unsigned long last_call_time = 0;

};

#endif

