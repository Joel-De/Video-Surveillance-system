#include <Servo.h>
#define HORIZONTAL_SERVO_PIN 2
#define VERTICAL_SERVO_PIN 3

#define SERVO_MAX_POS 150
#define SERVO_MIN_POS 0

#define SERVO_SPEED 15  // delay between angle move in ms

Servo ServoH;  // create servo objects
Servo ServoV;


String SerialBuffer;
int angleinput;
String ID;
void setup() {
  ServoH.attach(HORIZONTAL_SERVO_PIN);
  ServoV.attach(VERTICAL_SERVO_PIN);
  ServoH.write(0);
  ServoV.write(70);
    
  Serial.begin(19200);
  Serial.setTimeout(50);
  
}


void MoveServo(Servo &ServoID, int angle){
  if ((angle>SERVO_MAX_POS) || (angle < SERVO_MIN_POS)){
    return;
  }
  int cstep = (angle >= ServoID.read()) ? 1 : -1;
  
  for (int cpos = ServoID.read(); cpos != angle; cpos += cstep) {
    ServoID.write(cpos);              
    delay(10);                       
  }
  //pos = angle;
}
void loop() {



  
 if (Serial.available()){
   SerialBuffer = Serial.readString();
   ID = SerialBuffer.substring(0,2);
   angleinput = SerialBuffer.substring(2).toInt();

   if (ID == "HM"){
      MoveServo(ServoH, angleinput);
      
   }else if (ID == "HN"){
      MoveServo(ServoH, ServoH.read() + angleinput);
      
   }else if (ID == "VM"){
      MoveServo(ServoV, angleinput);
      
   }else if (ID == "VN"){
      MoveServo(ServoV, ServoV.read() + angleinput);
      
   }else{
    MoveServo(ServoH, 180);
    MoveServo(ServoH, 0);
   }
   Serial.print("1");
 }

}
