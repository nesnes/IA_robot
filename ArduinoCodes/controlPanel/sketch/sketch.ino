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
Adafruit_SSD1306 display(128,64,OLED_MOSI, OLED_CLK, OLED_DC, OLED_RESET, OLED_CS);
#endif

#define START_BTN_PIN 7
#define COLOR_BTN_PIN 8

#define MODE_I2C
#ifndef MODE_I2C
  #define MODE_SERIAL
  //#define SERIAL_DEBUG
#endif
#include "comunication.h"

static const unsigned char PROGMEM logo16_ARI[] =
{ B00000001, B10000000,
  B00000111, B11100000,
  B00011000, B00111000,
  B00100000, B00000100,
  B00100000, B00000100,
  B00111100, B11100100,
  B00100011, B00010100,
  B00101011, B01010100,
  B00100011, B00010100,
  B00111100, B11100100,
  B00100000, B00000100,
  B00100000, B00000100,
  B00101111, B11100100,
  B00110101, B01010100,
  B00110101, B01010100,
  B00101111, B11100100 };

#if (SSD1306_LCDHEIGHT != 64)
//#error("Height incorrect, please fix Adafruit_SSD1306.h!");
#endif

#if(SERIAL_TX_BUFFER_SIZE == 64)
//#error("Reduce the buffer sizes to RX=32 TX=32 in the #defines of \\Arduino-1.x.x\\hardware\\arduino\\cores\\arduino\\HardwareSerial.h")
#endif

int freeRam () {
  extern int __heap_start, *__brkval; 
  int v; 
  return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval); 
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
int score = 0;
void printButtons(){
  #ifdef DISPLAY_ON
  display.setCursor(0, 0);
  display.setTextSize(1);
  char line[19];
  sprintf(line, "C=%i S=%i Score=%i\0", colorStatus, startStatus, score);
  display.println(line);
  display.drawFastHLine(0, 7, 110, 1);
  display.setTextSize(7);
  display.setCursor(2, 17);
  display.println(score);
  #endif
}

void updateScreen(){
  #ifdef DISPLAY_ON
  display.clearDisplay();
  printButtons();
  display.fillRect(110, 0, 17, 16, BLACK);
  display.drawBitmap(111, 0, logo16_ARI, 16, 16, WHITE);
  display.display();
  #endif
}

void setup()   {          
  comunication_begin(9);//I2C address 9      
  //Serial.begin(115200);
  pinMode(START_BTN_PIN, INPUT_PULLUP);
  pinMode(COLOR_BTN_PIN, INPUT_PULLUP);
  #ifdef DISPLAY_ON
  display.begin(SSD1306_SWITCHCAPVCC);
  display.clearDisplay();
  display.setRotation(2);
  display.setTextSize(1);
  display.setTextColor(WHITE);
  #endif
  startStatus = getStart();
  colorStatus = getColor();
  updateScreen();
}

void executeOrder(){
  comunication_read();
  if(comunication_msgAvailable()){
    if(comunication_InBuffer[0] == '#' && comunication_InBuffer[1] != '\0'){
      //ignore
    }
    else if(!strcmp(comunication_InBuffer, "id")){
      sprintf(comunication_OutBuffer, "ControlPanel");//max 29 Bytes
      comunication_write();//async
    }
    else if(strstr(comunication_InBuffer, "score set")){
      sscanf(comunication_InBuffer, "score set %i ", &score);
      sprintf(comunication_OutBuffer, "OK");//max 29 Bytes
      comunication_write();//async
    }
    else if(!strcmp(comunication_InBuffer, "get")){
      sprintf(comunication_OutBuffer, "C %i S %i", colorStatus, startStatus);//max 29 Bytes
      comunication_write();//async
    }
    else{
      sprintf(comunication_OutBuffer,"ERROR");
      comunication_write();//async
    }
    comunication_cleanInputs();
  }
}   

void loop() {
  int lastScore = score;
  int color = getColor();
  int start = getStart();
  executeOrder();
  if(color != colorStatus || start != startStatus || lastScore != score){
    colorStatus = color;
    startStatus = start;
    updateScreen();
  }
}


