#ifndef __VALVULASPP__
#define __VALVULASPP__

/* -> 90° valvula cerrada, min = 80 -> 0°valvula abierta
 *  
 * valvula 1,  max = 158, min = 80  oxigeno
 * valvula 2,  max = 152, min = 72  espiracion
 * valvula 3,  max = 154, min = 72  aire
 * valvula 4,  max = 157, min = 75  inspiracion
 * 
 */

/*******************************************************************************
                                  DEFINITIONS
*******************************************************************************/
#define Max_Valvula_PP_Aire    154
#define Min_Valvula_PP_Aire     72

#define Max_Valvula_PP_Oxigeno 158
#define Min_Valvula_PP_Oxigeno  80

#define Max_Valvula_PP_Inspiracion 157
#define Min_Valvula_PP_Inspiracion  75

#define Max_Valvula_PP_Espiracion 152
#define Min_Valvula_PP_Espiracion  72


/*******************************************************************************
                        EXTERNAL VARIABLES
*******************************************************************************/
int vp1=23;
int vp2=22;
int vp3=19;
int vp4=18;
int v1=14;
int v2=27;
int v3=26;
int v4=25;

int S0;
int S1;
int S2;
int PinS0=15;
int PinS1=4;
int PinS2=5;
int PinSensor=34;
float AlarmaPres=0.5;

#define Constante_Conversion 0.000805664      // resolucion del conversor
#define Constante_Atenuacion 1.5              // atenuacion del amplificador operacional 1.665
#define Error_temperatura    1                // de 0 a 85° grados 
#define Error_presion        0.5              // -7 a 7KPa
#define Vs                   5.0              // Volatje de alimentacion del sensor 
#define factor_presion       0.057            // Constante del fabricante
#define Conversion_PSI       0.145038         // Factor de conversion a PSI
#define Constante_presion    0.75             // constante del fabricante del sensor de 150PSI
#define Conversion_Mpa_PSI   145.038          // conversion de Mpa a PSI

#define a                   36.077            // Pendiente
#define b                   17.351            // Intercepto

#define Linealidad_Oxigeno  37.3928           // Constante de linealidad del sensor de oxigeno

/*******************************************************************************
//                             enumeration                                    //
*******************************************************************************/


/*******************************************************************************
//                             ESTRUCTURAS                                    //
*******************************************************************************/



/*******************************************************************************
//                              FUNCIONES                                      //
*******************************************************************************/
void ValvulasPP_Init        (void);
void Valvula_PP_Oxigeno     (int angulo);
void Valvula_PP_Aire        (int angulo);
void Valvula_PP_Inspiracion (int angulo);
void Valvula_PP_Espiracion  (int angulo);



#endif /*__VALVULASPP__*/
