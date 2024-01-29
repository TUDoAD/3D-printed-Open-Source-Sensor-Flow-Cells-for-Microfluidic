#include "DFRobot_PH.h"
#include "DFRobot_EC10.h"
#include <EEPROM.h>
#include <SPI.h>
#include "Adafruit_MAX31855.h"

#define PH_PIN A1
#define EC_PIN A2
#define MAXDO   0
#define MAXCS   1
#define MAXCLK  5

Adafruit_MAX31855 thermocouple(MAXCLK, MAXCS, MAXDO);

float voltage,voltage1,phValue,temperature = 21,ecValue;
DFRobot_PH ph;
DFRobot_EC10 ec;

void setup()
{
    Serial.begin(9600);  
    
}

void loop()
{
    static unsigned long timepoint = millis();
    if(millis()-timepoint>1000U){                  //time interval: 1s
        timepoint = millis();
        temperature = thermocouple.readCelsius();         // read your temperature sensor to execute temperature compensation
       
        Serial.print(" ");
        Serial.print(temperature);
    }
    ph.calibration(voltage,temperature);           
    ec.calibration(voltage,temperature);          // calibration process by Serail CMD
}


    
