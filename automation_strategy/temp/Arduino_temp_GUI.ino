
#include <MovingAverageFloat.h>

#include <Adafruit_MAX31865.h> 

Adafruit_MAX31865 thermo = Adafruit_MAX31865(10, 11, 12, 13);
#define RREF      430.0 // The value of the Rref resistor. Use 430.0 for PT100 and 4300.0 for PT1000
#define RNOMINAL  100 // The 'nominal' 0-degrees-C resistance of the sensor (100.0 for PT100)

void setup() {
  Serial.begin(115200);
  thermo.begin(MAX31865_4WIRE);  // set to 2WIRE or 4WIRE as necessary
}

void loop() {
  float rtd = thermo.readRTD();
  float ratio = rtd;
  ratio /= 32768;
  Serial.println(RREF*ratio,8);
  delay(10);
}
