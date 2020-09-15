#ifndef Comunication_h
#define Comunication_h

#include <Wire.h>
// Packet: ['startbyte','m','e','s','s','a','g','e','checksum','endbyte']
#define COMUNICATION_START_BYTE '^'
#define COMUNICATION_END_BYTE '\n'
#ifdef MODE_I2C
  #define COMUNICATION_BUFFER_IN_SIZE 40
  #define COMUNICATION_BUFFER_OUT_SIZE 30
#endif
#ifdef MODE_SERIAL
  #define COMUNICATION_BUFFER_IN_SIZE 32
  #define COMUNICATION_BUFFER_OUT_SIZE 32
#endif

volatile char comunication_InBuffer[COMUNICATION_BUFFER_IN_SIZE];
volatile char comunication_OutBuffer[COMUNICATION_BUFFER_IN_SIZE];
volatile boolean comunication_ReceiveFlag = false; //When data is available in input buffer
volatile boolean comunication_msgAvailableFlag = false;//When validated message is available in input buffer
volatile boolean comunication_SendFlag = false;

/* I2C communication */
#ifdef MODE_I2C  
  void i2cReceiveEvent(int howMany) {
    if(howMany>1){
      Wire.read();//ignore first byte
      Wire.readBytes((char*)comunication_InBuffer, howMany-1);
      comunication_InBuffer[howMany-1]='\0';
      comunication_ReceiveFlag = true;
    }
    else if(howMany==1)
      Wire.read();
  }
  
  void i2cRequestEvent() {
    if(comunication_SendFlag){
      Wire.write((char*)comunication_OutBuffer);
      memset(comunication_OutBuffer, '\0', COMUNICATION_BUFFER_OUT_SIZE);
      comunication_SendFlag = false;
    }
    else
      Wire.write("");
  }
#endif

/* Serial communication */
#ifdef MODE_SERIAL  
  void readSerial() {
    int i=0;
    while (Serial.available()) {
      delay(3);
      char inChar = (char)Serial.read();
      if (inChar == '\r' || inChar == '\n' || i>COMUNICATION_BUFFER_IN_SIZE-2) {
        break;
      }
      comunication_InBuffer[i++] = inChar;
    }
    comunication_InBuffer[i+1] = '\0';
    comunication_ReceiveFlag = i > 0;
  }
  
  void sendSerial(){
    if(comunication_SendFlag){
      Serial.print((char*)comunication_OutBuffer);
      comunication_SendFlag=false;
    }
  }
#endif

/* Generic functions */
void comunication_begin(unsigned char i2cAdress){
  #ifdef MODE_I2C
      Wire.begin(i2cAdress);//i2c address
      Wire.onRequest(i2cRequestEvent);
      Wire.onReceive(i2cReceiveEvent);
    #endif
  
    #ifdef MODE_SERIAL               
      Serial.begin(115200);
    #endif
}

void comunication_cleanInputs(){
    memset(comunication_InBuffer, '\0', COMUNICATION_BUFFER_IN_SIZE);
    comunication_ReceiveFlag = false;
    comunication_msgAvailableFlag = false;
}

void comunication_write(){
    #ifdef MODE_I2C
    //Apply protocol
    //prepend start byte
    int lastIndex = COMUNICATION_BUFFER_OUT_SIZE-2;
    for(int i=COMUNICATION_BUFFER_OUT_SIZE-2;i>0;i--){
      comunication_OutBuffer[i] = comunication_OutBuffer[i-1];
      if(comunication_OutBuffer[i] == '\0') lastIndex = i;
    }
    comunication_OutBuffer[0] = COMUNICATION_START_BYTE;
    //append end byte
    comunication_OutBuffer[lastIndex+1] = COMUNICATION_END_BYTE;
    //compute checksum
    unsigned char checksum = 0;
    for(int i=1;i<lastIndex;i++){
      checksum ^= comunication_OutBuffer[i];
    }
    comunication_OutBuffer[lastIndex] = checksum;
    #endif
    
    comunication_SendFlag = true;
    
    #ifdef MODE_SERIAL
      sendSerial();
    #endif
}

void comunication_read(){
    #ifdef MODE_SERIAL
      readSerial();
      if(comunication_ReceiveFlag)
        comunication_msgAvailableFlag = true; 
    #endif
    
    #ifdef MODE_I2C
    //Return if no message
    if(!comunication_ReceiveFlag)
      return;
      
    //verify message
    bool valid = true;
    if(comunication_InBuffer[0] != COMUNICATION_START_BYTE)
      valid = false;
    //remove start byte
    int endIndex = 0;
    for(int i=1;i<COMUNICATION_BUFFER_IN_SIZE;i++){
      comunication_InBuffer[i-1] = comunication_InBuffer[i];
      if(comunication_InBuffer[i-1] == COMUNICATION_END_BYTE)
        endIndex = i-1;
    }
    if(endIndex == 0)
      valid = false;
    //compute checksum
    unsigned char checksum = 0;
    for(int i=0;i<endIndex-1;i++){
      checksum ^= comunication_InBuffer[i];
    }
    if(valid && checksum != comunication_InBuffer[endIndex-1])
      valid = false;
    if(valid){//Message ready
      comunication_InBuffer[endIndex-1] = '\0';
      comunication_msgAvailableFlag = true; 
    }
    else{//Report Error
      comunication_cleanInputs();
      sprintf(comunication_OutBuffer, "ERROR");
      comunication_write();
    }
    #endif
}


bool comunication_msgAvailable(){
    return comunication_msgAvailableFlag;
}
#endif //Comunication_h

