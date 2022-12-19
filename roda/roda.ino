#define pwm1 5
#define pwm2 6
#define pwm3 9
#define pwm4 10

// String stringOne; // Initial type of class
int i, j;

void setup() {
  pinMode(pwm1, OUTPUT);
  pinMode(pwm2, OUTPUT);
  pinMode(pwm3, OUTPUT);
  pinMode(pwm4, OUTPUT);
  Serial.begin(9600);
  Serial.setTimeout(1);
}

int kiri = 2;
int kanan = 2;

void loop() {
  if (Serial.available() > 0)
  {
    int data;
    i = Serial.readString().toInt();
    if (i == 0 || i == 1 || i == 2 ){
      if(j==0){
         if (kiri > 0)
          {
              if (kiri <= 5)
              {
                  kiri = 0;
                  kanan = 0;
              }
              else
              {
                  kiri-=2;
                  kanan-=2;
              }
              analogWrite(pwm1, 0);
              analogWrite(pwm2, kiri);
              analogWrite(pwm3, 0);
              analogWrite(pwm4, kanan);
              delay(100); 
          }
//        stringOne = String("Aspal");
        }
      } else if (i == 3 && j == 0){
        if (kiri < 40)
          {
              if (kiri >= 35)
              {
                  kiri = 40;
                  kanan = 40;
              }
              else
              {
                  kiri+=2;
                  kanan+=2;
              }
              analogWrite(pwm1, 0);
              analogWrite(pwm2, kiri);
              analogWrite(pwm3, 0);
              analogWrite(pwm4, kanan);
              delay(100); 
          }
//        stringOne = String("Paving");
      } else if (i == 4){
        j=1;
      }
      if (j == 1){
        if (kiri > 0)
          {
              if (kiri <= 5)
              {
                  kiri = 0;
                  kanan = 0;
              }
              else
              {
                  kiri-=2;
                  kanan-=2;
              }
              analogWrite(pwm1, 0);
              analogWrite(pwm2, kiri);
              analogWrite(pwm3, 0);
              analogWrite(pwm4, kanan);
              delay(100); 
          }
      }

    delay(100);

    
    if (j == 1 && kiri == 0){
      Serial.println("ARDUINOSTOP");
    } else {
      Serial.println(String(kiri));
    }
  } 
}