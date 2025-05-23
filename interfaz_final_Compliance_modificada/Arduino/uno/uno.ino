
#include <ESP32Servo.h>
#include "ValvulasProporcionales.h"
#include <Separador.h>
Separador s;

//se utiliza para hacer uso del segundo nucleo
TaskHandle_t Task1;

int buzer = 12;
bool flag = false;
bool flag2 = false;
float Presion_Inspiracion = 0;
float Presion_Espiracion = 0;
float Presion_Prom = 0;
float Flujo_Total = 0;
float Volumen = 0;
float Presion_Tanque = 0;


//Datos de entrada
String Modo = "";
String Onda = "";
int FIO2;
float Vmax;
float Pmax;
float Qmax;
float PEEP;
float Frec;
float Tinsp;
float Tespi;
float Tespe1;
float Tespe2;
float aire;
float oxigeno;
float PresT;


char valor = 'j';

Servo myServo1;  // create servo object to control a servo
Servo myServo2;  // create servo object to control a servo
Servo myServo3;  // create servo object to control a servo
Servo myServo4;  // create servo object to control a servo

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(buzer, OUTPUT);
  ValvulasPP_Init();
  ValvulasOn_Init();
  //instancia segundo nucleo asociado auna funcion
  xTaskCreatePinnedToCore(
    task1Func, /* Task function. */
    "Task1",   /* name of task. */
    10000,     /* Stack size of task */
    NULL,      /* parameter of the task */
    10,        /* priority of the task */
    &Task1,    /* Task handle to keep track of created task */
    0);        /* pin task to core 0 */
  pinMode(PinS0, OUTPUT);
  pinMode(PinS1, OUTPUT);
  pinMode(PinS2, OUTPUT);
}
void lector() {
  String datos_reci = Serial.readString();
  Modo = s.separa(datos_reci, '?', 0);
  Onda = s.separa(datos_reci, '?', 1);
  FIO2 = s.separa(datos_reci, '?', 2).toInt();
  Vmax = s.separa(datos_reci, '?', 3).toFloat();
  Pmax = s.separa(datos_reci, '?', 4).toFloat();
  Qmax = s.separa(datos_reci, '?', 5).toFloat();
  PEEP = s.separa(datos_reci, '?', 6).toFloat();
  Frec = s.separa(datos_reci, '?', 7).toFloat();
  Tinsp = s.separa(datos_reci, '?', 8).toFloat();
  Tespe1 = s.separa(datos_reci, '?', 9).toFloat();
  Tespi = s.separa(datos_reci, '?', 10).toFloat();
  Tespe2 = s.separa(datos_reci, '?', 11).toFloat();
  aire = s.separa(datos_reci, '?', 12).toFloat();
  oxigeno = s.separa(datos_reci, '?', 13).toFloat();
  PresT = s.separa(datos_reci, '?', 14).toFloat();
  if (Modo == "V") {
    valor = 'e';
  }
  if (Modo == "P") {
    valor = 'e';
  }
  if (Modo == "f") {
    valor = 'f';
  }
  if (Modo == "a") {
    valor = 'a';
  }
  if (Modo == "b") {
    valor = 'b';
  }
  if (Modo == "r") {
    ESP.restart();
  }
  Serial.println(Tinsp);
}
void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    
    lector();
  }
  switch (valor) {
    case 'a':
      digitalWrite(buzer, 1);
      delay(500);
      digitalWrite(buzer, 0);
      delay(200);
      digitalWrite(buzer, 1);
      delay(500);
      digitalWrite(buzer, 0);
      delay(200);
      break;
    case 'b':
      digitalWrite(buzer, 1);
      delay(600);
      digitalWrite(buzer, 0);
      delay(200);
      digitalWrite(buzer, 1);
      delay(800);
      digitalWrite(buzer, 0);
      delay(300);
      break;
    case 'e':
      alimentacionOFF();
      delay(100);
      alimentacionON();
      PosValvPP();
      flag = true;
      flag2 = true;
      break;
    case 'f':
      alimentacionOFF();
      flag = false;
      flag2 = false;
      Volumen = 0;
      break;
  }
  valor = 'j';
  if (flag) {
    Serial.print('S');
    sen_presion();
    delay(20);
    sen_flujo();
    delay(20);
  }
}
//------------------------------------------------Leer sensor de presion en la linea de inspiracion------------------
//Preguntar
void sen_presion(void) {
  S0 = 1;
  S1 = 0;
  S2 = 0;
  digitalWrite(PinS0, S0);
  digitalWrite(PinS1, S1);
  digitalWrite(PinS2, S2);
  Presion_Inspiracion = analogRead(PinSensor);

  float Compensacion = 0;
  Compensacion = (Error_presion * Error_temperatura * factor_presion * Vs);
  Presion_Inspiracion *= Constante_Conversion;
  Presion_Inspiracion *= Constante_Atenuacion;
  if (Presion_Inspiracion < 4.6) {
    Presion_Inspiracion += 0.3;
  }
  //Serial.printf ("voltaje: %.2f v\n", Presion_Inspiracion);
  Presion_Inspiracion -= Compensacion;
  Presion_Inspiracion /= Vs;
  Presion_Inspiracion -= 0.5;
  Presion_Inspiracion /= factor_presion;
  Presion_Inspiracion *= Conversion_PSI;
  Presion_Inspiracion *= 91.3991;  //donde 1.3 factor de ajuste, 70.307 convierte psi a cmH2O
  S0 = 1;
  S1 = 0;
  S2 = 0;
  digitalWrite(PinS0, S0);
  digitalWrite(PinS1, S1);
  digitalWrite(PinS2, S2);
  Presion_Espiracion = analogRead(PinSensor);

  Compensacion = (Error_presion * Error_temperatura * factor_presion * Vs);
  Presion_Espiracion *= Constante_Conversion;
  Presion_Espiracion *= Constante_Atenuacion;
  if (Presion_Espiracion < 4.6) {
    Presion_Espiracion += 0.3;
  }
  //Serial.printf ("voltaje: %.2f v\n", Presion_Inspiracion);
  Presion_Espiracion -= Compensacion;
  Presion_Espiracion /= Vs;
  Presion_Espiracion -= 0.5;
  Presion_Espiracion /= factor_presion;
  Presion_Espiracion *= Conversion_PSI;
  Presion_Espiracion *= 91.3991;  //donde 1.3 factor de ajuste, 70.307 convierte psi a cmH2O

  Presion_Prom = 6 + ((Presion_Espiracion + Presion_Espiracion) / 2);

  if (Presion_Prom > Pmax) {
    digitalWrite(buzer, HIGH);
  } else {

    digitalWrite(buzer, LOW);
  }
  if (Presion_Prom < PEEP) {
    digitalWrite(v4, 0);
  }

  Serial.print('P');
  Serial.print(Presion_Prom);
}

//------------------------------------------------Leer sensor de presion en el tanque------------------------------
void sen_pres_tank(void) {
  digitalWrite(PinS0, LOW);
  digitalWrite(PinS1, LOW);
  digitalWrite(PinS2, HIGH);
  delay(1);
  Presion_Tanque = analogRead(PinSensor);
  //Preguntar
  Presion_Tanque = (0.053 * Presion_Tanque) - 9.7188;
  //Serial.print(Presion_Tanque);
  //Serial.println('?');
  //delay(1);
  control_pres_tank();
}
//------------------------------------------------Leer sensor de flujo en la linea de inspiracion------------------
//Preguntar
void sen_flujo(void) {
  digitalWrite(PinS0, LOW);
  digitalWrite(PinS1, HIGH);
  digitalWrite(PinS2, HIGH);
  delay(1);
  float flujoEspir = analogRead(PinSensor);

  flujoEspir *= Constante_Conversion;
  flujoEspir *= Constante_Atenuacion;
  if (flujoEspir < 4.6) {
    flujoEspir += 0.3;
  }
  //Serial.printf ("voltaje: %.2f v\n", Flujo_Espiracion);
  flujoEspir *= a;
  flujoEspir -= b;
  if (flujoEspir < 0) {
    flujoEspir = 0;
  }

  digitalWrite(PinS0, HIGH);
  digitalWrite(PinS1, LOW);
  digitalWrite(PinS2, HIGH);
  delay(1);
  float flujoInsp = analogRead(PinSensor);

  flujoInsp *= Constante_Conversion;
  flujoInsp *= Constante_Atenuacion;
  if (flujoInsp < 4.6) {
    flujoInsp += 0.3;
  }
  //Serial.printf ("voltaje: %.2f v\n", Flujo_Inspiracion);
  flujoInsp *= a * 1.03;
  flujoInsp -= b;
  if (flujoInsp < 0) {
    flujoInsp = 0;
  }
  Flujo_Total = flujoInsp - (flujoEspir*0.88);
  Volumen = Volumen + (Flujo_Total*1000*0.0430237356221901/60);
  Serial.print('F');
  Serial.print(Flujo_Total);
  Serial.print('V');
  Serial.print(Volumen);
  Serial.println('?');
  delay(1);
  sen_pres_tank();
}

//------------------------------------------------Abrir valvulas de alimentacion-------------------------------------
void alimentacionON(void) {

  Valvula_PP_Aire(aire);
  digitalWrite(v1, HIGH);
  Valvula_PP_Oxigeno(oxigeno);
  digitalWrite(v2, HIGH);
  delay(100);
}
//------------------------------------------------Cerrar valvulas de alimentacion--------------------------------------
void alimentacionOFF(void) {

  Valvula_PP_Aire(0);
  digitalWrite(v1, LOW);
  Valvula_PP_Oxigeno(0);
  digitalWrite(v2, LOW);
  Valvula_PP_Inspiracion(0);
  Valvula_PP_Espiracion(0);
  delay(100);
}
void control_pres_tank() {
  if (Presion_Tanque < PresT) {
    digitalWrite(v1, 1);
    digitalWrite(v2, 1);
  } else {
    digitalWrite(v1, 0);
    digitalWrite(v2, 0);
  }
}
//------------------------------------------------nucleo 2--------------------------------------------------------------------------------------
void task1Func(void* pvParameters) {
  for (;;) {
    if (flag2) {
      digitalWrite(v3, HIGH);
      delay(Tinsp * 1000);

      digitalWrite(v3, LOW);
      delay(Tespe1 * 1000);

      digitalWrite(v4, HIGH);
      delay(Tespi * 1000);

      digitalWrite(v4, LOW);
      delay(Tespe2 * 1000);
      Volumen = 0;
    }
    delay(200);  //vTaskDelay( pdMS_TO_TICKS( 200 ) );
  }
}
//------------------------------------------------Posicionar valvulas Proporcionales---------------------------------------------------
void PosValvPP(void) {

  Valvula_PP_Inspiracion(0);
  Valvula_PP_Espiracion(0);
  delay(300);
  Valvula_PP_Inspiracion(34);
  Valvula_PP_Espiracion(45);
}

//------------------------------------------------Inicializacion de las valvulas proporcionales------------------------------------------------------------

void ValvulasPP_Init(void) {

  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);
  myServo1.setPeriodHertz(50);       // standard 50 hz servo
  myServo1.attach(vp1, 1000, 3000);  // attaches the servo on pin 18 to the servo object

  myServo2.setPeriodHertz(50);       // standard 50 hz servo
  myServo2.attach(vp2, 1000, 3000);  // attaches the servo on pin 18 to the servo object

  myServo3.setPeriodHertz(50);       // standard 50 hz servo
  myServo3.attach(vp3, 1000, 3000);  // attaches the servo on pin 18 to the servo object

  myServo4.setPeriodHertz(50);       // standard 50 hz servo
  myServo4.attach(vp4, 1000, 3000);  // attaches the servo on pin 18 to the servo object
}

//------------------------------------------------Inicializacion de las valvulas on/off------------------------------------------------------------

void ValvulasOn_Init(void) {
  pinMode(v1, OUTPUT);
  pinMode(v2, OUTPUT);
  pinMode(v3, OUTPUT);
  pinMode(v4, OUTPUT);
  digitalWrite(v1, 0);
  digitalWrite(v2, 0);
  digitalWrite(v3, 0);
  digitalWrite(v4, 0);
}


//------------------------------------------------LLeva a la valvula proporcional de aire al angulo deseado------------------------------------------------------------

void Valvula_PP_Aire(int angulo) {
  angulo = map(angulo, 0, 100, Max_Valvula_PP_Aire, Min_Valvula_PP_Aire);
  myServo1.write(angulo);
}

//------------------------------------------------LLeva a la valvula proporcional de oxigeno al angulo deseado------------------------------------------------------------

void Valvula_PP_Oxigeno(int angulo) {
  angulo = map(angulo, 0, 100, Max_Valvula_PP_Oxigeno, Min_Valvula_PP_Oxigeno);
  myServo2.write(angulo);
}

//------------------------------------------------LLeva a la valvula proporcional de inspiracion al angulo deseado------------------------------------------------------------

void Valvula_PP_Inspiracion(int angulo) {
  angulo = map(angulo, 0, 100, Max_Valvula_PP_Inspiracion, Min_Valvula_PP_Inspiracion);
  myServo3.write(angulo);
}

//------------------------------------------------LLeva a la valvula proporcional de espiracion al angulo deseado------------------------------------------------------------

void Valvula_PP_Espiracion(int angulo) {
  angulo = map(angulo, 0, 100, Max_Valvula_PP_Espiracion, Min_Valvula_PP_Espiracion);
  myServo4.write(angulo);
}