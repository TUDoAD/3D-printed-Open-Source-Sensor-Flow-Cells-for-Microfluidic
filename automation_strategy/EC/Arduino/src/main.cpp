//Analog Devices data sheet:** (http://www.analog.com/media/en/technical-documentation/data-sheets/AD9833.pdf)

//----------Librarys----------//

#include "AD9833.h"         //  AD9833 Library Copyright(c): Bill Williams (https://github.com/Billwilliams1952/AD9833-Library-Arduino)
                            //  --> Allows high level communication between Programm and AD9833
                            // Connect: SCK -> D13, SS -> D10, MOSI -> D11
                            
#include <Wire.h>

//#include <movingAvgFloat.h>
#include <Arduino.h>
#include <ADS1115_WE.h>


//----------Definitions----------//

//--AD9833
#define FNC_PIN 10        //  Pin that is connected to FSync on AD9833
AD9833 gen(FNC_PIN);      //  " gen " is the Object of the Signal Generator with internal 25MHz reference
float frequency, kHz;     //  Declare "frequency" and "kHz" as floating point numbers


//--ADS1115
ADS1115_WE adc = ADS1115_WE(0x48);  //  Use this for the 16-bit version
int adc0, adc1;        //  Declare "adc0" and "adc1" as integer reading of ADC
float u_high, u_mid, u_high_cal, u_mid_cal;   //  Declare "u_high" and "u_mid" as floating point numbers for measured voltages
//movingAvgFloat u_high_avg(1);
//movingAvgFloat u_mid_avg(1);

void setup() {

    Serial.begin(115200);
    gen.Begin();          // Initialize Object " gen " as active
    //u_high_avg.begin();
    //u_mid_avg.begin();
    // Set output of signal generator: SINE 50kHz
    frequency = 50000;
    kHz = frequency/1000;
    gen.ApplySignal(SINE_WAVE,     //  Signal type - SINE_WAVE, TRIANGLE_WAVE, SQUARE_WAVE, and HALF_SQUARE_WAVE
                    REG0,          //  write to register 0 (two separate registers can be used)
                    frequency);    //  Frequency - 0 to 12.5 MHz
    
    gen.EnableOutput(true);

    // Initiate ADC
    Wire.begin();
    if(!adc.init()){
        Serial.println("ADS1115 not connected!");
    }
    adc.setVoltageRange_mV(ADS1115_RANGE_4096);
    adc.setConvRate(ADS1115_64_SPS);   // +/- 4.096V  1 bit = 0.125mV
} // setup()

float readChannel(ADS1115_MUX channel) {
    
    float voltage = 0.0;
    adc.setCompareChannels(channel);
    adc.startSingleMeasurement();
    while(adc.isBusy()){}
    voltage = adc.getResult_mV(); // alternative: getResult_V for Volt
    return voltage;

} // readChannel()


void loop() {

    u_high = readChannel(ADS1115_COMP_0_GND);
    u_mid  = readChannel(ADS1115_COMP_1_GND);
    u_high_cal = u_high;
    u_mid_cal  = u_mid;
    Serial.print(millis());Serial.print(";");Serial.print(u_high_cal); Serial.print(";"); Serial.println(u_mid_cal);
    delay(10);
} // loop()


