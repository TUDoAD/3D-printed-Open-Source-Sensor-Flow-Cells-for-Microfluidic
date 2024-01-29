
String command;
String commando;
char firstcharo;
char firstchar;
double nullposition = 0;

//Intervalle für die Einzelnen Phasen(Batch Versuche)
//Phase 1
//int n=160;
//Phase2
//int m=30;
//Phase3
//int o= 24;
int m;
int n;
int i;
int j;
int k;
int o;
String inChar;

boolean phase1 = false;
boolean phase2 = false;
boolean phase3 = false;
boolean ende = false;
boolean pause = false;
boolean GS = false;
boolean Reak = false;
#include <Tic.h>

// On boards with a hardware serial port available for use, use
// that port to communicate with the Tic. For other boards,
// create a SoftwareSerial object using pin 10 to receive (RX)
// and pin 11 to transmit (TX).
#ifdef SERIAL_PORT_HARDWARE_OPEN
#define ticSerial SERIAL_PORT_HARDWARE_OPEN
#else
#include <SoftwareSerial.h>
SoftwareSerial ticSerial(10, 11);
#endif

TicSerial tic1(ticSerial,14);
TicSerial tic2(ticSerial,11);





void setup()
{
  // Set the baud rate.
  ticSerial.begin(9600);
  Serial.begin(9600);
    Serial.println(" S = start");
    Serial.println(" G = Äquimolar fahren");
    Serial.println(" R = reverse");
    Serial.println(" L = Reaktionsmodus");
    Serial.println(" E = Ende");
    Serial.println(" Z = RTD");



  // Give the Tic some time to start up.
  delay(20);

  // Tells the Tic that it is OK to start driving the motor.  The
  // Tic's safe-start feature helps avoid unexpected, accidental
  // movement of the motor: if an error happens, the Tic will not
  // drive the motor again until it receives the Exit Safe Start
  // command.  The safe-start feature can be disbled in the Tic
  // Control Center.
  tic1.exitSafeStart();
  tic2.exitSafeStart();
}

// Sends a "Reset command timeout" command to the Tic.  We must
// call this at least once per second, or else a command timeout
// error will happen.  The Tic's default command timeout period
// is 1000 ms, but it can be changed or disabled in the Tic
// Control Center.
void resetCommandTimeout()
{
  tic1.resetCommandTimeout();
  tic2.resetCommandTimeout();
}

// Delays for the specified number of milliseconds while
// resetting the Tic's command timeout so that its movement does
// not get interrupted.
void delayWhileResettingCommandTimeout(uint32_t ms)
{
  uint32_t start = millis();
  do
  {
    resetCommandTimeout();
  } while ((uint32_t)(millis() - start) <= ms);
}

void loop()
{

  if (Serial.available() > 0) { //check if the serial port is available
    
    

    
    command = Serial.readString(); // read the incoming byte as String
    firstchar = command.charAt(0);
    
    check(firstchar); // die "check"-Funktion sucht nach befehlen und führt diese aus
    } // if Ende
    
  
  
  if (phase1){
    Serial.println("Start");
    
        if(pause){
            i = n ;
         pause=false;
        }
        else{
          Start();
        }  
             
}
  else if(phase2){
      Serial.println("Reaktion");
       
      if(pause){
        j = m ;
        pause=false;
        }
      else{
        Reaktion();
    }  
      
  }
  
  
  else if(phase3){
    reverse();

  }

//  else if(T);{
//    Rampe();
//}
  else if(GS){
    GLS();
  }

  else if(ende){
    Ende();  
  }
  else if(Reak){
    GV();
}
}

void check(char firstchar){   // query of commands
  if (firstchar != ' '){    // first check if command is empty

    if (firstchar == 'S'){
        phase1 = true;
        phase2 = false;
        phase3 = false;
        ende = false; 
        pause = false; 
    }

    if (firstchar == 'L'){
        phase1 = false;
        phase2 = true;
        phase3 = false; 
        ende = false;
        GS = false;
    }

    if (firstchar == 'R'){
        phase1 = false;
        phase2 = false;
        phase3 = true;
        GS = false;
        ende = false;
    }   

        if (firstchar == 'E'){
        phase1 = false;
        phase2 = false;
        phase3 = false; 
        ende = true;
        GS = false;
    }

        if (firstchar == 'G'){
        phase1 = false;
        phase2 = false;
        phase3 = false; 
        ende = false;
        GS= true ;
    }
        if (firstchar == 'Z'){
        phase1 = false;
        phase2 = false;
        phase3 = false; 
        ende = false;
        GS= false ;
        Reak=true;
    }
    }
  }

void Start() {
  
          Serial.println("Moving");
          //Step size
          tic1.setStepMode(TicStepMode::Microstep32);
          // Move forward at 3 ml/min  for 5 seconds.
          tic1.setTargetVelocity(5*1279630);
          delayWhileResettingCommandTimeout(10000);

          tic1.setTargetVelocity(0);
          delayWhileResettingCommandTimeout(100);
}

void Reaktion(){

            Serial.println("Reaktions Modus");
            //Stepsize 
            tic1.setStepMode(TicStepMode::Microstep32);
            tic2.setStepMode(TicStepMode::Microstep32);
            
            // 3ml/min für Pumpe 1
            tic1.setTargetVelocity(1279630);
            
            
            //dritte Geschwindigkeit für Pumpe 2 == 0.5 ml/min
            Serial.println("0.5 ml/min");
            tic2.setTargetVelocity(0.5 * 1279630);
            delayWhileResettingCommandTimeout(120000);
            tic2.setTargetVelocity(0);
            delayWhileResettingCommandTimeout(60000);
            //nach 1 min pumpen, eine Minute warten bis zur nächsten Messung


            
            //vierte Geschwindigkeit für Pumpe 2 ==  0.75 ml / min
            Serial.println("0.75 ml/min");
            tic2.setTargetVelocity(0.75 * 1279630);
            delayWhileResettingCommandTimeout(120000);
            tic2.setTargetVelocity(0);
            delayWhileResettingCommandTimeout(60000);
            //nach 1 min pumpen, eine Minute warten bis zur nächsten Messung


            Serial.println("0.9 ml/min");
            tic2.setTargetVelocity(0.9 * 1279630);
            delayWhileResettingCommandTimeout(120000);
            tic2.setTargetVelocity(0);
            delayWhileResettingCommandTimeout(60000);            


            
            //Fünfte Geschwindigkeit für Pumpe 2 == 3 ml / min
            Serial.println("1 ml/min");
            tic2.setTargetVelocity(1*1279630);
            delayWhileResettingCommandTimeout(120000);
            tic2.setTargetVelocity(0);
            delayWhileResettingCommandTimeout(60000);
            //nach 1 min pumpen, eine Minute warten bis zur nächsten Messung

            Serial.println("1.1 ml/min");
            tic2.setTargetVelocity(1.1*1279630);
            delayWhileResettingCommandTimeout(120000);
            tic2.setTargetVelocity(0);
            delayWhileResettingCommandTimeout(60000);
            //nach 1 min pumpen, eine Minute warten bis zur nächsten Messung


            Serial.println("1.25 ml/min");
            tic2.setTargetVelocity(1.25*1279630);
            delayWhileResettingCommandTimeout(120000);
            tic2.setTargetVelocity(0);
            delayWhileResettingCommandTimeout(60000);
            //nach 1 min pumpen, eine Minute warten bis zur nächsten Messung


            Serial.println("1.5 ml/min");
            tic2.setTargetVelocity(1.5*1279630);
            delayWhileResettingCommandTimeout(120000);
            tic2.setTargetVelocity(0);
            delayWhileResettingCommandTimeout(60000);
            //nach 1 min pumpen, eine Minute warten bis zur nächsten Messung

            Serial.println("2 ml/min");
            Serial.println("Ende");
            tic1.setTargetVelocity(0);
            tic2.setTargetVelocity(2*1279630);
            delayWhileResettingCommandTimeout(120000);
            tic2.setTargetVelocity(0);
            delayWhileResettingCommandTimeout(60000);
            //nach 1 min pumpen, eine Minute warten bis zur nächsten Messung


            



            //end Geschwindigkeit für Pumpe 2 == 0ml / min
            Serial.println("Reaktion vorbei");
            tic2.setTargetVelocity(0);
            delayWhileResettingCommandTimeout(120000);
            //nach 1 min pumpen, eine Minute warten bis zur nächsten Messung
            Serial.println("Ende");
            tic1.setTargetVelocity(0);
            delayWhileResettingCommandTimeout(60000);

             phase1 = false;
             phase2 = false;
             phase3 = false;
             ende = false;
             pause = false;


            
            




}
            
void Ende(){
          Serial.println("Ende");
          // Decelerate to a stop.
          tic1.setTargetVelocity(0);
          tic2.setTargetVelocity(0);
        
}
void GLS()  {
          Serial.println("Gleichschnell");
          //Step size
          tic1.setStepMode(TicStepMode::Microstep32);
          tic2.setStepMode(TicStepMode::Microstep32);
          // Move forward at 3 ml/min  for 5 seconds.
          tic1.setTargetVelocity(1279630);
          delayWhileResettingCommandTimeout(10000);
          tic2.setTargetVelocity(1.05*1279630);
          delayWhileResettingCommandTimeout(10000);


         
   
}

void reverse() {
        Serial.println("Reverse");
          //Step size
          tic1.setStepMode(TicStepMode::Microstep16);  
          tic2.setStepMode(TicStepMode::Microstep16);                  
          // Move backwards 5 ml / min
          tic1.setTargetVelocity(-6398148);
          tic2.setTargetVelocity(-6398148);
}

void GV(){

            
            //Stepsize 
            tic1.setStepMode(TicStepMode::Microstep32);
            tic2.setStepMode(TicStepMode::Microstep32);

            
            Serial.println("RTD Start / 5 min VE-Water");
            tic1.setTargetVelocity(2 * 1279630);
            delayWhileResettingCommandTimeout(10*60000);
            Serial.println("Tracer introduced");
            tic2.setTargetVelocity(10*1279630);
            delayWhileResettingCommandTimeout(2000);
            tic2.setTargetVelocity(0);
            delayWhileResettingCommandTimeout(14*60000); 
            Serial.println("End of RTD");

             phase1 = false;
             phase2 = false;
             phase3 = false;
             ende = true;
             pause = false;}
            

void Reaktion2(){

            Serial.println("Reaktions Modus");
            //Stepsize 
            tic1.setStepMode(TicStepMode::Microstep32);
            tic2.setStepMode(TicStepMode::Microstep32);
            
            // 3ml/min für Pumpe 1
            tic2.setTargetVelocity(1279630);
            
            
            //dritte Geschwindigkeit für Pumpe 2 == 0.5 ml/min
            Serial.println("0.5 ml/min");
            tic1.setTargetVelocity(0.5 * 1279630);
            delayWhileResettingCommandTimeout(120000);
            tic1.setTargetVelocity(0);
            delayWhileResettingCommandTimeout(60000);
            //nach 1 min pumpen, eine Minute warten bis zur nächsten Messung


            
            //vierte Geschwindigkeit für Pumpe 2 ==  0.75 ml / min
            Serial.println("0.75 ml/min");
            tic1.setTargetVelocity(0.75 * 1279630);
            delayWhileResettingCommandTimeout(120000);
            tic1.setTargetVelocity(0);
            delayWhileResettingCommandTimeout(60000);
            //nach 1 min pumpen, eine Minute warten bis zur nächsten Messung


            Serial.println("0.9 ml/min");
            tic1.setTargetVelocity(0.9 * 1279630);
            delayWhileResettingCommandTimeout(120000);
            tic1.setTargetVelocity(0);
            delayWhileResettingCommandTimeout(60000);            


            
            //Fünfte Geschwindigkeit für Pumpe 2 == 3 ml / min
            Serial.println("1 ml/min");
            tic1.setTargetVelocity(1*1279630);
            delayWhileResettingCommandTimeout(120000);
            tic1.setTargetVelocity(0);
            delayWhileResettingCommandTimeout(60000);
            //nach 1 min pumpen, eine Minute warten bis zur nächsten Messung

            Serial.println("1.1 ml/min");
            tic1.setTargetVelocity(1.1*1279630);
            delayWhileResettingCommandTimeout(120000);
            tic1.setTargetVelocity(0);
            delayWhileResettingCommandTimeout(60000);
            //nach 1 min pumpen, eine Minute warten bis zur nächsten Messung


            Serial.println("1.25 ml/min");
            tic1.setTargetVelocity(1.25*1279630);
            delayWhileResettingCommandTimeout(120000);
            tic1.setTargetVelocity(0);
            delayWhileResettingCommandTimeout(60000);
            //nach 1 min pumpen, eine Minute warten bis zur nächsten Messung


            Serial.println("1.5 ml/min");
            tic1.setTargetVelocity(1.5*1279630);
            delayWhileResettingCommandTimeout(120000);
            tic1.setTargetVelocity(0);
            delayWhileResettingCommandTimeout(60000);
            //nach 1 min pumpen, eine Minute warten bis zur nächsten Messung

            Serial.println("2 ml/min");
            Serial.println("Ende");
            tic2.setTargetVelocity(0);
            tic1.setTargetVelocity(2*1279630);
            delayWhileResettingCommandTimeout(120000);
            tic1.setTargetVelocity(0);
            delayWhileResettingCommandTimeout(60000);
            //nach 1 min pumpen, eine Minute warten bis zur nächsten Messung


            



            //end Geschwindigkeit für Pumpe 2 == 0ml / min
            Serial.println("Reaktion vorbei");
            tic2.setTargetVelocity(0);
            delayWhileResettingCommandTimeout(120000);
            //nach 1 min pumpen, eine Minute warten bis zur nächsten Messung
            Serial.println("Ende");
            tic1.setTargetVelocity(0);
            delayWhileResettingCommandTimeout(60000);

             phase1 = false;
             phase2 = false;
             phase3 = false;
             ende = false;
             pause = false;


            
            




}
  
  
  
  
  


  


  
