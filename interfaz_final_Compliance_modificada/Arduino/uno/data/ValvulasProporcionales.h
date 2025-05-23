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
extern const int vp1;
extern const int vp2;
extern const int vp3;
extern const int vp4;
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
