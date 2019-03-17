
#define MODE_I2C
#ifndef MODE_I2C
  #define MODE_SERIAL
#endif

#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define OLED_MOSI   9
#define OLED_CLK   10
#define OLED_DC    11
#define OLED_CS    12
#define OLED_RESET 13

#define DISPLAY_ON
#ifdef DISPLAY_ON
Adafruit_SSD1306 display(OLED_MOSI, OLED_CLK, OLED_DC, OLED_RESET, OLED_CS);
#endif

#define START_BTN_PIN 7
#define COLOR_BTN_PIN 8

static const unsigned char PROGMEM logo16_ARI[] =
{ B00000001, B10000000,
  B00000111, B11100000,
  B00011100, B00111000,
  B00100000, B00000100,
  B00100100, B00100100,
  B00100000, B00000100,
  B00011111, B11111000,
  B00000000, B00000000,
  B00111111, B11111100,
  B00111000, B00011100,
  B00001000, B00010000,
  B00001000, B00010000,
  B00100001, B10000111,
  B01010001, B01000010,
  B11111001, B10000010,
  B10001001, B01000111 };

#if (SSD1306_LCDHEIGHT != 64)
#error("Height incorrect, please fix Adafruit_SSD1306.h!");
#endif

#if(SERIAL_TX_BUFFER_SIZE == 64)
#error("Reduce the buffer sizes to RX=32 TX=32 in the #defines of \\Arduino-1.x.x\\hardware\\arduino\\cores\\arduino\\HardwareSerial.h")
#endif

int freeRam () {
  extern int __heap_start, *__brkval; 
  int v; 
  return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval); 
}

#define LINE_CHAR_SIZE 23
char messages[7][LINE_CHAR_SIZE];
int messageIndex = -1;

void scrollTextUp(){
  for( int i=1;i<7;i++){
    memcpy(messages[i-1], messages[i], LINE_CHAR_SIZE);
  }
  memset(messages[6], '\0', LINE_CHAR_SIZE);
}

//Very important to add a '\0' at the end of the char* message
void addMessage(const char* msg){
  messageIndex++;
  if(messageIndex == 7){
    messageIndex = 6;
    scrollTextUp();
  }
  memset(messages[messageIndex], '\0', LINE_CHAR_SIZE);
  int rowSize = LINE_CHAR_SIZE - 2;
  if(messageIndex==0)
    rowSize = 18;
  int msgLength = 0;
  for(int i=0;msg[i]!='\0';i++)
    msgLength++;
  int charNumber = min(rowSize, msgLength);
  for(int i=0;i<charNumber;i++)
    messages[messageIndex][i] = msg[i];
  messages[messageIndex][rowSize+1] = '\0';
  
  if(msgLength>rowSize){
    char subMsg[msgLength-charNumber+1];
    for(int i=charNumber;i<msgLength;i++)
      subMsg[i-charNumber] = msg[i];
    subMsg[msgLength-charNumber] = '\0';
    addMessage(subMsg);
  }
}

void printMessages(){
  #ifdef DISPLAY_ON
  display.setCursor(0, 9);
  for( int i=0;i<7;i++){
    display.println(messages[i]);
  }
  #endif
}

int getColor(){
  if(digitalRead(COLOR_BTN_PIN))
    return 0;
  else
    return 1;
}

int getStart(){
  if(digitalRead(START_BTN_PIN))
    return 0;
  else
    return 1;
}

int colorStatus = 0;
int startStatus = 0;
int score = 42;
void printButtons(){
  #ifdef DISPLAY_ON
  display.setCursor(0, 0);
  char line[19];
  sprintf(line, "C=%i S=%i Score=%i\0", colorStatus, startStatus, score);
  display.println(line);
  display.drawFastHLine(0, 7, 110, 1);
  #endif
}

void updateScreen(){
  #ifdef DISPLAY_ON
  display.clearDisplay();
  printButtons();
  printMessages();
  display.fillRect(110, 0, 17, 16, BLACK);
  display.drawBitmap(111, 0, logo16_ARI, 16, 16, WHITE);
  display.display();
  #endif
}

/* I2C communication */
#ifdef MODE_I2C
  #define I2C_BUFFER_IN_SIZE 40
  #define I2C_BUFFER_OUT_SIZE 30
  
  volatile char i2cInBuffer[I2C_BUFFER_IN_SIZE];
  volatile char i2cOutBuffer[I2C_BUFFER_OUT_SIZE];
  volatile boolean i2cReceiveFlag = false;
  volatile boolean i2cSendFlag = false;
  void i2cReceiveEvent(int howMany) {
    if(howMany>1){
      Wire.read();//ignore first byte
      Wire.readBytes((char*)i2cInBuffer, howMany-1);
      i2cInBuffer[howMany-1]='\0';
      i2cReceiveFlag = true;
    }
    else if(howMany==1)
      Wire.read();
  }
  
  void i2cRequestEvent() {
    if(i2cSendFlag){
      Wire.write((char*)i2cOutBuffer);
      memset(i2cOutBuffer, '\0', I2C_BUFFER_OUT_SIZE);
      i2cSendFlag = false;
    }
    else
      Wire.write("");
  }
#endif

/* Serial communication */
#ifdef MODE_SERIAL
  #define SERIAL_BUFFER_IN_SIZE 32
  #define SERIAL_BUFFER_OUT_SIZE 32
  volatile char serialInBuffer[SERIAL_BUFFER_IN_SIZE];
  volatile char serialOutBuffer[SERIAL_BUFFER_OUT_SIZE];
  volatile boolean serialReadFlag = false;
  volatile boolean serialSendFlag = false;
  
  void readSerial() {
    int i=0;
    while (Serial.available()) {
      delay(3);
      char inChar = (char)Serial.read();
      if (inChar == '\r' || inChar == '\n' || i>SERIAL_BUFFER_IN_SIZE-2) {
        break;
      }
      serialInBuffer[i++] = inChar;
    }
    serialInBuffer[i+1] = '\0';
    serialReadFlag = i > 0;
  }
  
  void sendSerial(){
    if(serialSendFlag){
      Serial.print((char*)serialOutBuffer);
      serialSendFlag=false;
    }
  }
#endif

void setup()   { 
  #ifdef MODE_I2C
    Wire.begin(5);                //i2c address
    Wire.onRequest(i2cRequestEvent);
    Wire.onReceive(i2cReceiveEvent);
  #endif

  #ifdef MODE_SERIAL               
    Serial.begin(115200);
  #endif
  
  pinMode(START_BTN_PIN, INPUT_PULLUP);
  pinMode(COLOR_BTN_PIN, INPUT_PULLUP);
  #ifdef DISPLAY_ON
    display.begin(SSD1306_SWITCHCAPVCC);
    display.clearDisplay();
    display.setRotation(2);
    display.setTextSize(1);
    display.setTextColor(WHITE);
  #endif
  for( int i=0;i<7;i++){
      memset(messages[i], '\0', LINE_CHAR_SIZE);
  }
  startStatus = getStart();
  colorStatus = getColor();
  updateScreen();
}

void executeOrder(volatile boolean &readReady, char* readBuffer, volatile boolean &writeReady, char* writeBuffer, int readBufferSize){
  if(readReady){
    if(readBuffer[0] == '#' && readBuffer[1] != '\0'){ 
      addMessage(readBuffer+1);
      updateScreen();
    }
    else if(strstr(readBuffer, "color get")){
      sprintf(writeBuffer, "color %i\r\n", colorStatus);
      writeReady = true;
    }
    else if(strstr(readBuffer, "start get")){
      sprintf(writeBuffer, "start %i\r\n", startStatus);
      writeReady = true;
    }
    else if(strstr(readBuffer, "score set") != NULL){
      sscanf(readBuffer, "score set %i", &score);
    }
    else if(strstr(readBuffer, "id")){
      sprintf(writeBuffer, "ControlPanelAlexV1\r\n"); //max 32 bit (with \r\n)
      writeReady = true;
    }
    else{
      sprintf(writeBuffer, "ERROR\r\n");
      writeReady = true;
    }
    memset(readBuffer, '\0', readBufferSize);
    readReady=false;
  }
}

void loop() {
  int lastScore = score;

  #ifdef MODE_I2C
    executeOrder(i2cReceiveFlag, i2cInBuffer, i2cSendFlag, i2cOutBuffer, I2C_BUFFER_IN_SIZE);
  #endif
  
  #ifdef MODE_SERIAL
    readSerial();
    executeOrder(serialReadFlag, serialInBuffer, serialSendFlag, serialOutBuffer, SERIAL_BUFFER_IN_SIZE);
    sendSerial();
  #endif
  
  int color = getColor();
  int start = getStart();
  if(color != colorStatus || start != startStatus || lastScore != score){
    colorStatus = color;
    startStatus = start;
    updateScreen();
  }
}


