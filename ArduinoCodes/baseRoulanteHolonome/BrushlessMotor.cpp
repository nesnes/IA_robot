#include "BrushlessMotor.h"

BrushlessMotor::BrushlessMotor(int motorId, float wheelPerimeter, bool invert)
	: m_motorId(motorId)
  , m_wheelPerimeter(wheelPerimeter) //mm
  , m_inverted(invert)
{
	
}

BrushlessMotor::~BrushlessMotor(){
	
}
  
void BrushlessMotor::begin(){
  /* https://playground.arduino.cc/Main/TimerPWMCheatsheet/
   * For Arduino Mega: (tested on Arduino Mega 2560)
  timer 0 (controls pin 13, 4) If you change TCCR0B, it affects millis() and delay().
  timer 1 (controls pin 12, 11)
  timer 2 (controls pin 10, 9)
  timer 3 (controls pin 5, 3, 2)
  timer 4 (controls pin 8, 7, 6)
  TCCRnB, where 'n' is the number for the timer*/
  
  /*For Arduino pRO mINI:
  timer 0 (controls pin 5, 6) If you change TCCR0B, it affects millis() and delay().
  timer 1 (controls pin 9, 10)
  timer 2 (controls pin 11, 3)
  TCCRnB, where 'n' is the number for the timer*/
  if(m_motorId == 0){
    m_pinA = 9;
    m_pinB = 10;
    m_pinC = 11;
    
  	TCCR1B = TCCR1B & 0b11111000 | 0x01; // set PWM frequency @ 31250 Hz for Pins 9 and 10
  	TCCR2B = TCCR2B & 0b11111000 | 0x01; // set PWM frequency @ 31250 Hz for Pins 11 and 3 (3 not used)
  	ICR1 = 255 ; // 8 bit resolution, required?
    //  ICR1 = 1023 ; // 10 bit resolution
  }
  if(m_motorId == 1){
    m_pinA = 5;
    m_pinB = 3;
    m_pinC = 2;
    
    TCCR3B = TCCR3B & 0b11111000 | 0x01; // set PWM frequency @ 31250 Hz for Pins 5, 3 and 2
    ICR3 = 255 ; // 8 bit resolution, required?
    //  ICR1 = 1023 ; // 10 bit resolution
  }
  if(m_motorId == 2){
    m_pinA = 8;
    m_pinB = 7;
    m_pinC = 6;
    
    TCCR4B = TCCR4B & 0b11111000 | 0x01; // set PWM frequency @ 31250 Hz for Pins 8, 7 and 6
    ICR4 = 255 ; // 8 bit resolution, required?
    //  ICR1 = 1023 ; // 10 bit resolution
  }


	m_currentStepA = (int)(((float)(BRUSHLESS_STEPCOUNT)/3.0f)*0.0f);
	m_currentStepB = (int)(((float)(BRUSHLESS_STEPCOUNT)/3.0f)*1.0f);
	m_currentStepC = (int)(((float)(BRUSHLESS_STEPCOUNT)/3.0f)*2.0f);

	for(int i=0;i<BRUSHLESS_STEPCOUNT;i++){
		m_pwmSin[i] = 127.0f + 127.0f*sin( ((2.0f*PI)/(float)(BRUSHLESS_STEPCOUNT)) *(float)(i) );
	}

	pinMode(m_pinA, OUTPUT);
	pinMode(m_pinB, OUTPUT);
	pinMode(m_pinC, OUTPUT);
}

double BrushlessMotor::getAndResetDistanceDone(){
  double stepsDone = m_stepsDone;
  m_stepsDone = 0;
  if(stepsDone==0) return 0;
  double revolutions = (1.0d/double(BRUSHLESS_STEP_PER_REVOLUTION))*stepsDone;
  double distance = (revolutions*m_wheelPerimeter)/1000.0d; //meters
  if(m_inverted) distance *= -1;
  return distance;
}

void BrushlessMotor::setSpeed(double speed){ // m/s
  m_requestedSpeed = speed;
}

double BrushlessMotor::getSpeed(){ // m/s
  return m_currSpeed;  
}

float BrushlessMotor::getPower(){ // m/s
  return m_power;  
}

void BrushlessMotor::computeSpeed(){
  //Acceleration
  double speedStep = 0.001;
  double absCurrSpeed = fabs(m_currSpeed);
  //if(absCurrSpeed<0.01) speedStep = 0.00001;
  double absRequestedSpeed = fabs(m_requestedSpeed);
  if(m_requestedSpeed == 0 && fabs(m_currSpeed)<=speedStep){
    m_currSpeed = m_requestedSpeed;
    absCurrSpeed = absRequestedSpeed;
  }
  else if(m_requestedSpeed>m_currSpeed) m_currSpeed += speedStep;
  else if (m_requestedSpeed<m_currSpeed) m_currSpeed -= speedStep;
  absCurrSpeed = fabs(m_currSpeed);

  //Power
  m_powerCount++;
  /*if(m_powerCount==30){
    m_powerCount=0;
    float speedDiff = abs(abs(m_oldSpeed) - absCurrSpeed)*50;
    m_oldSpeed = m_currSpeed;
    m_power = speedDiff;
  }*/
  /*if(absRequestedSpeed != absCurrSpeed){
    m_power = m_requestedSpeed;//fabs(absCurrSpeed - absRequestedSpeed)*100;
  }
  else m_power = BRUSHLESS_MIN_POWER;*/
  if(m_power>BRUSHLESS_MAX_POWER) m_power = BRUSHLESS_MAX_POWER;
  if(m_power<BRUSHLESS_MIN_POWER) m_power = BRUSHLESS_MIN_POWER;
  //m_currSpeed = m_requestedSpeed;
  
  //Compute timers
  if(m_inverted) m_direction = m_currSpeed>0.0d?-1:1;
  else  m_direction = m_currSpeed>0.0d?1:-1;
  //if(m_currSpeed==0) m_direction = 0;
  double revPerMeter = (absCurrSpeed*1000.0d)/m_wheelPerimeter; //speed*1000 -> m to mm
  double stepCount = double(BRUSHLESS_STEP_PER_REVOLUTION) * revPerMeter;
  if(stepCount>=1)
    m_currSleep = 1000000.0d/stepCount;
  else
    m_currSleep = 0;
 
}

void BrushlessMotor::spin(){
  unsigned long currMicro = micros();
  unsigned long diffMicro = currMicro - m_lastMicro;
  if(currMicro < m_lastMicro){ //handle overflow (~every hours)
    diffMicro = 0;
  }

  computeSpeed();
  
  if(m_currSleep == 0 || diffMicro < m_currSleep) return; //Nothing to do
  m_lastMicro = currMicro;


  m_currentStepA = m_currentStepA + m_direction;
  if(m_currentStepA > BRUSHLESS_STEPCOUNT-1) m_currentStepA = 0;
  if(m_currentStepA<0) m_currentStepA = BRUSHLESS_STEPCOUNT-1;
   
  m_currentStepB = m_currentStepB + m_direction;
  if(m_currentStepB > BRUSHLESS_STEPCOUNT-1) m_currentStepB = 0;
  if(m_currentStepB<0) m_currentStepB = BRUSHLESS_STEPCOUNT-1;
   
  m_currentStepC = m_currentStepC + m_direction;
  if(m_currentStepC > BRUSHLESS_STEPCOUNT-1) m_currentStepC = 0;
  if(m_currentStepC<0) m_currentStepC = BRUSHLESS_STEPCOUNT-1;

  analogWrite(m_pinA, m_pwmSin[m_currentStepA]*m_power);
  analogWrite(m_pinB, m_pwmSin[m_currentStepB]*m_power);
  analogWrite(m_pinC, m_pwmSin[m_currentStepC]*m_power);
  m_stepsDone += m_direction;
}

void BrushlessMotor::spinDegrees(float degrees)
{
  int sleep = 1500;//400
  float currDegrees=0;
  unsigned long now = micros();
  
	while((degrees>0 && currDegrees < degrees) || (degrees<=0 && currDegrees > degrees)){
  
		//if((now - lastMotorDelayTime) >  motorDelayActual){ // delay time passed, move one step 
		int increment;
		if (degrees>0) increment = 1;
		else increment = -1;  
    
		m_currentStepA = m_currentStepA + increment;
		if(m_currentStepA > BRUSHLESS_STEPCOUNT-1) m_currentStepA = 0;
		if(m_currentStepA<0) m_currentStepA = BRUSHLESS_STEPCOUNT-1;
		 
		m_currentStepB = m_currentStepB + increment;
		if(m_currentStepB > BRUSHLESS_STEPCOUNT-1) m_currentStepB = 0;
		if(m_currentStepB<0) m_currentStepB = BRUSHLESS_STEPCOUNT-1;
		 
		m_currentStepC = m_currentStepC + increment;
		if(m_currentStepC > BRUSHLESS_STEPCOUNT-1) m_currentStepC = 0;
		if(m_currentStepC<0) m_currentStepC = BRUSHLESS_STEPCOUNT-1;
	   
		//lastMotorDelayTime = now;
		//}  
		analogWrite(m_pinA, m_pwmSin[m_currentStepA]/4);
		analogWrite(m_pinB, m_pwmSin[m_currentStepB]/4);
		analogWrite(m_pinC, m_pwmSin[m_currentStepC]/4);
		if(sleep>0)
			delayMicroseconds(sleep);
		//currDegrees += (degrees>0)?0.275:-0.275;
    currDegrees += (degrees>0)?1:-1;
	}
}

