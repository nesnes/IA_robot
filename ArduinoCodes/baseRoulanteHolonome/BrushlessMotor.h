#ifndef BrushlessMotor_h
#define BrushlessMotor_h

#include <Arduino.h>
//#define BRUSHLESS_STEPCOUNT 30
//#define BRUSHLESS_STEP_PER_REVOLUTION 210
#define BRUSHLESS_STEPCOUNT 60
#define BRUSHLESS_STEP_PER_REVOLUTION 420
//#define BRUSHLESS_STEPCOUNT 120
//#define BRUSHLESS_STEP_PER_REVOLUTION 840


#define BRUSHLESS_MIN_POWER 0.25
#define BRUSHLESS_MAX_POWER 0.70

class BrushlessMotor
{
public:
  BrushlessMotor(int motorId=0, float wheelPerimeter=100, bool invert=false); //mm
  ~BrushlessMotor();
  
  void begin();

  void setSpeed(double speed); //m/s
  double getSpeed(); //m/s
  float getPower(); //m/s
  void spin();
  void spinDegrees(float degrees);
  void computeSpeed();
  double getAndResetDistanceDone();


//private:
  int m_motorId;
  uint8_t m_pinA;
  uint8_t m_pinB;
  uint8_t m_pinC;
  
  float m_pwmSin[BRUSHLESS_STEPCOUNT];
  
  int m_currentStepA;
  int m_currentStepB;
  int m_currentStepC;

  bool m_inverted = false;
  unsigned long m_lastMicro = 0;
  unsigned int m_currSleep = 0;
  int m_direction = 1; //1 or -1
  float m_power = 0.15; //0 weak, 0.5 middle, 1 strong
  float m_wheelPerimeter = 100; //mm
  double m_currSpeed = 0;
  double m_requestedSpeed = 0;

  int m_powerCount = 0;
  double m_oldSpeed = 0;

  int m_stepsDone = 0;
};

#endif // BrushlessMotor_h

