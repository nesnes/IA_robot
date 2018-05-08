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

void setup()   {                
  Serial.begin(9600);
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

#define INPUT_STR_SIZE 32
#define OUPUT_STR_SIZE 32
char inputString[INPUT_STR_SIZE];
char outputString[OUPUT_STR_SIZE];
boolean stringReady = false;

void readSerial() {
  int i=0;
  while (Serial.available()) {
    delay(3);
    char inChar = (char)Serial.read();
    if (inChar == '\r' || inChar == '\n' || i>INPUT_STR_SIZE-2) {
      break;
    }
    inputString[i++] = inChar;
  }
  inputString[i+1] = '\0';
  stringReady = i > 0;
}

void resetOutputString(){
  memset(outputString, '\0', OUPUT_STR_SIZE);
}

void loop() {
  int lastScore = score;
  readSerial();
  if(stringReady){
    if(inputString[0] == '#' && inputString[1] != '\0'){ //Print debug message
      addMessage(inputString+1); //+1 on the pointer to move after the #
      updateScreen();
    }
    else if(!strcmp(inputString, "color get")){
      sprintf(outputString, "color %i\r\n", colorStatus);
      Serial.print(outputString);
    }
    else if(!strcmp(inputString, "start get")){
      sprintf(outputString, "start %i\r\n", startStatus);
      Serial.print(outputString);
    }
    else if(strstr(inputString, "score set") != NULL){
      sscanf(inputString, "score set %i", &score);
    }
    else if(!strcmp(inputString, "id")){
      sprintf(outputString, "ControlPanelAlexV1\r\n"); //max 32 bit (with \r\n)
      Serial.print(outputString);
    }
    else{
      Serial.print("ERROR\r\n");
    }
    memset(inputString, '\0', INPUT_STR_SIZE);
    stringReady = false;
  }
  int color = getColor();
  int start = getStart();
  if(color != colorStatus || start != startStatus || lastScore != score){
    colorStatus = color;
    startStatus = start;
    updateScreen();
  }
}


