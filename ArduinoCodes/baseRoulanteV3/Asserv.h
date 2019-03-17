#ifdef MOTOR_ENCODER
double wheelDiameter=6.07; //cm
double pulsePerRevolution=1600;//pulse par revolution
double entraxe=16.8;//cm
#else
double wheelDiameter=9.5; //cm
double pulsePerRevolution=1200;//pulse par revolution
double entraxe=29.8;//cm
#endif

double pulsePerDegree = (2.0f*((entraxe / wheelDiameter) * pulsePerRevolution)/360.0f);// * 1.0308;  // Ok pour 90°    * 1.0308 
double pulsePerCm =  pulsePerRevolution / ( PI * wheelDiameter);

long int lastNbTickLeft = 0;
long int lastNbTickRight = 0;

double absoluteX=0;
double absoluteY=0;
double absoluteAngle = 0;

int staticCount = 0;
int staticMax = 5;//10

bool movementEnabaled = false;
bool PIDEnabled = false;
bool xyMove = false;
bool xyMoveStop = false;
float xTarget=0;
float yTarget=0;
float angleTarget=0;
float startX = 0;
float startY = 0;

float accelerationDistance = 15; //cm
float accelerationAngle = 15; //degree
float startSpeed = 0.01;
float targetSpeed = 0.5;
float targetCloseSpeed = 0.3;
float targetSpeedRotation = 0.3;
float maxRotationSpeed = 0.5;
float distance = 0;
float angle = 0;

float lastDistanceError = 0;
float lastAngleError = 0;
float lastSpeed = 0;

float sumDistanceError = 0;
float sumAngleError = 0;

float coefficientDistanceP = 0.02;
float coefficientDistanceI = 0.0000;
float coefficientDistanceD = 0.001;

float coefficientAngleP = 0.08;//0.03
float coefficientAngleI = 0.0000;
float coefficientAngleD = 0.051;//0.051

bool mouvmentFinished = false;
long int errorDistance = 0;
long int errorAngle = 0;
long int nbTickObjectif = 0;
long int nbTickAngleObjectif = 0;
long int endStability = 0;
int endStabilityTarget = 10;
long int distancePrecision = 0.2f*pulsePerCm;
long int anglePrecision = 0.2f*pulsePerDegree;
float leftCommand = 0;
float rightCommand = 0;
float leftCommandRaw = 0;
float rightCommandRaw = 0;
float robotSpeed = 0;
float speed = 0;
float precisionSpeed = 0.005f;
float currentDistance = 0;
float currentAngle = 0;
volatile bool emergencyStop = false;
int rotationSide = 0;

void updatePosition();
void Encodeurs_Reset() {
    updatePosition();
    encoder_left.setPosition(0);
    encoder_right.setPosition(0);
    lastNbTickLeft = 0;
    lastNbTickRight = 0;
}

void computePID()
{
    errorDistance = nbTickObjectif - (encoder_left.getPosition() + encoder_right.getPosition())/2;
    errorAngle = (nbTickAngleObjectif) - (encoder_left.getPosition()-encoder_right.getPosition());
    if(xyMove)
    {
        errorDistance = nbTickObjectif;
        errorAngle = nbTickAngleObjectif;
    }
    currentDistance = ((encoder_left.getPosition() + encoder_right.getPosition()) /2) /pulsePerRevolution * wheelDiameter * PI;
    currentAngle = (encoder_left.getPosition()/pulsePerDegree - encoder_right.getPosition()/pulsePerDegree)*-1;
    speed = startSpeed;
    
    //Compute speed
    if(!xyMove && fabs(distance) > 0) //distance acceleration
    {
        float vmax = targetSpeed;
        float accDist = accelerationDistance;
        float decelDist = accelerationDistance*2;
        if(fabs(distance) < (accDist+decelDist)){
            vmax = targetSpeed* (fabs(distance) / (accDist+decelDist));
            accDist = fabs(distance)*(accDist/(accDist+decelDist));
            decelDist = fabs(distance)*(decelDist/(accDist+decelDist));
        }
        bool speedSet=false;
        if(fabs(currentDistance) <= accDist){
            speed = startSpeed + (vmax - startSpeed)*((1.f/accDist)*fabs(currentDistance));
            speedSet=true;
        }
        else if(fabs(currentDistance) >= (fabs(distance) - decelDist)){
            speed = vmax - (vmax - startSpeed)*((1.f/(decelDist))*(fabs(currentDistance)-(fabs(distance)-decelDist)));
            speedSet = true;
        }
        if(!speedSet)
            speed = vmax;
    }
    else if(!xyMove && distance == 0 && fabs(angle) > 0) //angle acceleration
    {
        if(maxRotationSpeed<targetSpeedRotation)
            targetSpeedRotation = maxRotationSpeed;
        float vmax = targetSpeedRotation;
        float accAng = accelerationAngle;
        if(fabs(angle) < accAng * 2){
            vmax = targetSpeedRotation* (fabs(angle) / (accAng*2));
            accAng = fabs(angle)/2.0f;
        }
        bool speedSet=false;
        if(fabs(currentAngle) <= accAng){
            speed = startSpeed + (vmax - startSpeed)*((1.f/accAng)*fabs(currentAngle));
            speedSet = true;
        }
        else if(fabs(currentAngle) >= (fabs(angle) - accAng)){
            speed = vmax - (vmax - startSpeed)*((1.f/(accAng))*(fabs(currentAngle)-(fabs(angle)-accAng)));
            speedSet = true;
        }
        if(!speedSet)
            speed = vmax;
    }
    else if(xyMove && distance != 0){
        float currDist = sqrtf(powf(absoluteX-startX,2)+powf(absoluteY-startY,2));
        float fullDist = sqrtf(powf(startX-xTarget,2)+powf(startY-yTarget,2));
        
        float vmax = targetSpeed;
        float accDist = accelerationDistance;
        if(fabs(fullDist) < accelerationDistance * 2){
            vmax = targetSpeed* (fabs(fullDist) / (accelerationDistance*2));
            accDist = fabs(fullDist)/2.0f;
        }
        bool speedSet=false;
        if(fabs(currDist) <= accDist){
            speed = startSpeed + (vmax - startSpeed)*((1.f/accDist)*fabs(currDist));
            speedSet = true;
        }
        else if(fabs(currDist) > (fabs(fullDist) - accDist)){
            speed = vmax - (vmax - startSpeed)*((1.f/(accDist))*(fabs(currDist)-(fabs(fullDist)-accDist)));
            speedSet = true;
        }
        if(!speedSet)
            speed = vmax;
    }
    else if(xyMove && distance == 0){
          if(maxRotationSpeed<targetSpeedRotation)
            targetSpeedRotation = maxRotationSpeed;
          float vmax = targetSpeedRotation;
          float accAng = accelerationAngle;
          float currentAngleOrder = nbTickAngleObjectif*pulsePerDegree;
          if(fabs(currentAngleOrder) < accAng * 2){
              vmax = targetSpeedRotation* (fabs(currentAngleOrder) / (accAng*2));
              accAng = fabs(currentAngleOrder)/2.0f;
          }
          bool speedSet=false;
          if(fabs(angle)<accelerationAngle){
            speed = startSpeed + (vmax - startSpeed)*((1.f/accelerationAngle)*fabs(angle));
            speedSet = true;
          }
          else if(fabs(currentAngle) <= accAng){
              speed = startSpeed + (vmax - startSpeed)*((1.f/accAng)*fabs(currentAngle));
              speedSet = true;
          }
          else if(fabs(currentAngle) >= (fabs(currentAngleOrder) - accAng)){
              speed = vmax - (vmax - startSpeed)*((1.f/(accAng))*(fabs(currentAngle)-(fabs(currentAngleOrder)-accAng)));
              speedSet = true;
          }
          if(!speedSet)
              speed = vmax;
    }
    speed = abs(speed);

    #ifndef MOTOR_ENCODER
      //Correct speed
      if(fabs(robotSpeed)<0.15f && speed>0.4f)
          speed = startSpeed;
          
      if(fabs(robotSpeed)>0.3f && fabs(robotSpeed)<speed)
          speed = fabs(robotSpeed)-0.2f;
    #endif
    if(speed>targetSpeed)
        speed = targetSpeed;
    
        
    //Left
    float leftCommandP = coefficientDistanceP * (float)errorDistance
                         + coefficientAngleP * (float)errorAngle;
                         
    float leftCommandI = coefficientDistanceI * (float)sumDistanceError
                         + coefficientAngleI * (float)sumAngleError;
                         
    float leftCommandD = coefficientDistanceD * (float)(lastDistanceError - errorDistance)
                         + coefficientAngleD * (float)(lastAngleError - errorAngle);
    
    //Right
    float rightCommandP = coefficientDistanceP * (float)errorDistance
                          - coefficientAngleP * (float)errorAngle;
                         
    float rightCommandI = coefficientDistanceI * (float)sumDistanceError
                          - coefficientAngleI * (float)sumAngleError;
                         
    float rightCommandD = coefficientDistanceD * (float)(lastDistanceError - errorDistance)
                          - coefficientAngleD * (float)(lastAngleError - errorAngle);
    
    leftCommand = leftCommandP + leftCommandI + leftCommandD;
    rightCommand = rightCommandP + rightCommandI + rightCommandD;
    
    leftCommandRaw = leftCommand;
    rightCommandRaw = rightCommand;
    
    //Correct command
    if(abs(leftCommand)>abs(rightCommand)){
      if(leftCommand>0){
          rightCommand = rightCommand/leftCommand;
          leftCommand = 1;
      }
      else{
          rightCommand = -1*(rightCommand/leftCommand);
          leftCommand = -1;
      }
    }
    else if(abs(leftCommand)<abs(rightCommand)){
      if(rightCommand>0){
          leftCommand = leftCommand/rightCommand;
          rightCommand = 1;
      }
      else{
          leftCommand = -1*(leftCommand/rightCommand);
          rightCommand = -1;
      }
    }
    else{
      leftCommand=leftCommand>0?1:-1;
      rightCommand=rightCommand>0?1:-1;
    }
    /*if(leftCommand>1 || rightCommand>1){
        if(leftCommand>rightCommand){
            rightCommand = rightCommand/leftCommand;
            leftCommand = 1;
        }
        else{
            leftCommand = leftCommand/rightCommand;
            rightCommand = 1;
        }
    }
    if(leftCommand<-1 || rightCommand<-1){
        if(leftCommand<rightCommand){
            rightCommand = rightCommand/leftCommand*-1;
            leftCommand = -1;
        }
        else{
            leftCommand = leftCommand/rightCommand*-1;
            rightCommand = -1;
        }
    }*/
    
    //reduce speed at angle end to avoid ocilations and higher precision
    if(fabs(errorDistance) < 0.5f*pulsePerCm && fabs(errorAngle) < 6.0f*pulsePerDegree){
        speed = precisionSpeed;
    }
    
    if(distance!=0 && (fabs(speed-lastSpeed)>0.1f || speed>precisionSpeed)){//0.02 || 0.03
        speed = lastSpeed*0.99f + speed*0.01f; 
        //speed = lastSpeed*0.5f + speed*0.5f;  
    }
    
    /*if(
    (!xyMove && (float)(abs(errorDistance)) < 0.2f*pulsePerCm && (float)(abs(errorAngle)) < 0.2f*pulsePerDegree)
    ||
    (xyMove && abs(nbTickObjectif) < abs(0.2f*pulsePerCm) && abs(nbTickAngleObjectif) < abs(0.2f*pulsePerDegree))
    ){*/
    if( ((float)(abs(errorDistance)) < distancePrecision && (float)(abs(errorAngle)) < anglePrecision)
      || (xyMove && xyMoveStop)
      ){
        endStability++;
        speed = precisionSpeed;
        if(endStability > endStabilityTarget ){
            mouvmentFinished = true;
            angle = 0;
            distance = 0;
            PIDEnabled = false;
            endStability = 0;
        }
    }
    else
        endStability = 0;
    if(PIDEnabled && movementEnabaled && !emergencyStop){
        motor_left.speed(leftCommand*speed, fabs(targetSpeed)>1.f);
        motor_right.speed(rightCommand*speed, fabs(targetSpeed)>1.f);            
    }
    else{
        motor_left.speed(0);
        motor_right.speed(0);
        speed = 0;
    }
    lastSpeed = speed;
    
    if(!mouvmentFinished){
        lastDistanceError = errorDistance;
        lastAngleError = errorAngle;
        sumDistanceError += errorDistance;
        sumAngleError +=errorAngle;
    }

    if(emergencyStop){
        mouvmentFinished = true;
        angle = 0;
        distance = 0;
        PIDEnabled = false;
        endStability = 0;
    }
}

float distDiffSum = 0;
float angleDiffSum = 0;
int staticSumCount = 0;
void updatePosition()
{
    long int currEncoderLeft = encoder_left.getPosition();
    long int currEncoderRight = encoder_right.getPosition();
    //Update Absolute Position
    double angleDiff = (double)(lastNbTickLeft-currEncoderLeft)/pulsePerDegree - (double)(lastNbTickRight-currEncoderRight)/pulsePerDegree;
    absoluteAngle -= angleDiff;
    double distDiff = double((lastNbTickLeft-currEncoderLeft)+(lastNbTickRight-currEncoderRight))/2.f/pulsePerCm;
    robotSpeed = robotSpeed*0.8f+ (fabs(distDiff)*14.f + fabs(angleDiff)*0.9f)*0.2f;
    double radAngle=absoluteAngle*((2.f*PI)/360.f); //degree to radian
    absoluteX -= distDiff*cosf(radAngle);
    absoluteY -= distDiff*sinf(radAngle);
    lastNbTickLeft = currEncoderLeft;
    lastNbTickRight = currEncoderRight;
    if(PIDEnabled){
        if(staticSumCount >= staticMax){
            if(fabs(angleDiffSum) < 0.5f && fabs(distDiffSum) < 0.1f)
                staticCount ++;
            else
                staticCount = 0;
            distDiffSum = 0;
            angleDiffSum = 0;
            staticSumCount=0;
        }
        else{
            distDiffSum += distDiff;
            angleDiffSum += angleDiff;
            staticSumCount++;
        }
    }
    else
        staticCount = 0;
}

int dbgCount=0;
void printDebugPositon(){
  if(dbgCount++ != 50)
    return;
  dbgCount = 0;
  char bufferOut[300];
  /*sprintf(bufferOut, "#PID=%i \t X=%i \t Y=%i \t A=%i \t LE=%i \t RE=%i \t LC=%i  \t RC=%i \t LCR=%i  \t RCR=%i \t ObjD=%i \t ErrD=%i  \t ObjA=%i \t ErrA=%i\r\n"
  , (int)PIDEnabled, (int)absoluteX, (int)absoluteY, (int)absoluteAngle
  , (int)encoder_left.getPosition(), (int)encoder_right.getPosition()
  , (int)(leftCommand*speed), (int)(rightCommand*speed), (int)leftCommandRaw
  , (int)rightCommandRaw, (int)((float)(nbTickObjectif)/pulsePerCm)
  , (int)((float)(errorDistance)/pulsePerCm), (int)((float)(nbTickAngleObjectif)/pulsePerDegree)
  , (int)((float)(errorAngle)/pulsePerDegree));*/
  sprintf(bufferOut, "%i %i %i %i %i %i %i %i %i %i %i %i %i\r\n",
    (int)encoder_left.getPosition(),
    (int)encoder_right.getPosition(),
    (int)(motor_left.getSpeed()*3000.0f),
    (int)(motor_right.getSpeed()*3000.0f),
    (int)nbTickObjectif,
    (int)(encoder_left.getPosition() + encoder_right.getPosition())/2,
    (int)nbTickAngleObjectif,
    (int)(encoder_left.getPosition()-encoder_right.getPosition()),
    (int)(speed*1000),
    (int)absoluteX*10,
    (int)absoluteY*10,
    (int)absoluteAngle,
    (int)currentAngle
  );
  Serial.print(bufferOut);
}

void computeXYCommand(float x, float y, float _angle);
void PIDLoop() {
    updatePosition();
    if(PIDEnabled){
        if(xyMove)
            computeXYCommand(xTarget, yTarget, angleTarget);
        computePID();
    }
    #ifdef SERIAL_DEBUG
      printDebugPositon();
    #endif
}

void executionLoop(bool launchBlocking);
void waitForMouvmentFinished(){
    while(!mouvmentFinished) {
        executionLoop(false);
    }
}

void move(float distanceInCm){
    mouvmentFinished = false;
    angle = 0;
    distance = distanceInCm;
    nbTickObjectif = pulsePerCm*distance;
    nbTickAngleObjectif = pulsePerDegree*angle;
    PIDEnabled = true;
    waitForMouvmentFinished();
    Encodeurs_Reset();
}

void turn(float angleInDegree){
    
    mouvmentFinished = false;
    angle = angleInDegree;
    distance = 0;
    nbTickObjectif = pulsePerCm*distance;
    nbTickAngleObjectif = pulsePerDegree*angle;
    PIDEnabled = true;
    waitForMouvmentFinished();
    Encodeurs_Reset();
}

float startAngle = 0;
bool angleCommandComputed = false;
int distStabilityCount = 0;
bool xyRotation = false;
void computeXYCommand(float x, float y, float _angle){
    float x1= absoluteX;
    float y1= absoluteY;
    float x2= x;
    float y2= y;
    
    //Get Angle
    float dx = x2 - x1;
    float dy = y2 - y1;
    float rads = atan2(dy,dx);
    rads = fmod(rads,(float)2.0*PI);
    float newAngle = rads*180.0f/PI; // to degree
    newAngle -= absoluteAngle ;
    float direction = 1;
    if(newAngle>180) newAngle = -360.0f + newAngle;
    if(newAngle<-180) newAngle = 360.0f + newAngle;
    if(abs(newAngle)>100){
        if(newAngle>90) newAngle = 180.0f - newAngle;
        else newAngle = -180.0f - newAngle;
        direction = -1;
    }
    
    //Get Distance
    float newX= fmax(x1,x2)-fmin(x1,x2);
    float newY= fmax(y1,y2)-fmin(y1,y2);
    float newDistance = sqrtf(powf(newX,2)+powf(newY,2));
    
    //UC.printf("\n ToAngle:%g Dist:%g",newAngle, newDistance);
    angle=0;
    nbTickObjectif = direction * pulsePerCm*newDistance;
    if(abs(nbTickObjectif) < distancePrecision)
      distStabilityCount++;
    else if(distStabilityCount < endStabilityTarget/2){
      distStabilityCount=0;
      xyRotation=false;
    }
    if(distStabilityCount >= endStabilityTarget/2){ //final rotation
      if(!xyRotation){
        Encodeurs_Reset();
        xyRotation = true;
      }
      
      float finalAngle = _angle - absoluteAngle;
      if(finalAngle>360) finalAngle -= 360.f;
      if(finalAngle<-360) finalAngle += 360.f;
      if(finalAngle>180) finalAngle = -360.f + finalAngle;
      if(finalAngle<-180) finalAngle = 360.f + finalAngle;
      angle = finalAngle;
      distance=0;
      nbTickObjectif = pulsePerCm*distance;
      nbTickAngleObjectif = pulsePerDegree*finalAngle;
      
      if(abs(nbTickAngleObjectif) < anglePrecision){
        xyMoveStop=true;
      }
    }
    else{
      xyMove=true;
      nbTickAngleObjectif = direction * pulsePerDegree*newAngle;
      distance = newDistance;
    }
}

void goTo(float x, float y, float angle){
    /*bool needToMove = false;
    if(abs(x-absoluteX)>0.5f)
        needToMove = true;
    if(abs(y-absoluteY)>0.5f)
        needToMove = true;
    if(needToMove){*/
        xyMove = true;
        xTarget = x;
        yTarget = y;
        angleTarget = angle;
        startX = absoluteX;
        startY = absoluteY;
        startAngle = absoluteAngle;
        angleCommandComputed = false;
        mouvmentFinished = false;
        distStabilityCount=0;
        xyMoveStop=false;
        PIDEnabled = true;
        waitForMouvmentFinished();
        xyMove = false;
        Encodeurs_Reset();
    /*}
    float finalAngle = angle - absoluteAngle;
    if(finalAngle>360) finalAngle -= 360.f;
    if(finalAngle<-360) finalAngle += 360.f;
    if(finalAngle>180) finalAngle = -360.f + finalAngle;
    if(finalAngle<-180) finalAngle = 360.f + finalAngle;
    turn(finalAngle);*/
}

struct PathPoint{
    float x,y,angle,speed;
    PathPoint(float _x, float _y, float _angle, float _speed){
        x = _x;
        y = _y;
        angle = _angle;
        speed = _speed;
    }    
};

void followPath(PathPoint* path, int length){
    float angle = 0;
    for(int i=0; i<length;i++){
        float x = path[i].x;
        float y = path[i].y;
        angle = path[i].angle;
        float _speed = path[i].speed;
        //if(_speed>0.9f)
        //_speed = 0.9f;
        xyMove = true;
        xTarget = x;
        yTarget = y;
        if(i==0){
            startX = absoluteX;
            startY = absoluteY;
        }
        startAngle = absoluteAngle;
        if(_speed != 0) targetSpeed = _speed;
        if(_speed != 0) targetSpeedRotation = _speed;
        angleCommandComputed = false;
        mouvmentFinished = false;
        distStabilityCount=0;
        xyMoveStop=false;
        PIDEnabled = true;
        float remainingDist = 0;
        //UC.printf("# %i/%i xTarget: %.2f yTarget: %.2f angle: %.2f\r\n", i+1, length, xTarget, yTarget, angle);
        do{
            remainingDist = sqrt(pow(absoluteX-xTarget,2)+pow(absoluteY-yTarget,2));
            executionLoop(false);
            //wait_ms(5);
        }while(!mouvmentFinished && remainingDist > accelerationDistance+2);
    }
    waitForMouvmentFinished();
    xyMove = false;
    Encodeurs_Reset();
    float finalAngle = angle - absoluteAngle;
    if(finalAngle>360) finalAngle -= 360;
    if(finalAngle<-360) finalAngle += 360;
    if(finalAngle>180) finalAngle = -360 + finalAngle;
    if(finalAngle<-180) finalAngle = 360 + finalAngle;
    turn(finalAngle);    
}

float getSpeed(){
    if(staticCount < staticMax)
        return (motor_right.getSpeed() + motor_left.getSpeed())/2.0f * speed;
    else
        return 0.f;
}
float getAngularSpeed(){
    if(staticCount < staticMax)
        return (motor_right.getSpeed() - motor_left.getSpeed())/2.0f * speed;
    else
        return 0.f;
}
