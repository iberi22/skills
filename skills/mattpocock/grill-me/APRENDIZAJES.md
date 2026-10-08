# Aprendizajes del metodo grilling en DUQUE

Lecciones que el metodo produjo al usarlo de verdad. No son theory: son
errores que ocurrieron y como los agarro el patron.

## 1. El resumen del subagente no es evidencia

Un subagente reporto que la fecha limite de la NCh 4/2003 estaba en
`CATALOGO-NORMATIVO.md`. No estaba. **Estaba en el archivo de reglas**, que es
otro. El dato era correcto; la atribucion, no.

**Regla:** verificar el archivo antes de aceptar el hallazgo. El resumen dice
QUE se hizo; el archivo dice SI esta.

## 2. Un ejemplo con una cita inventada es peor que no tener ejemplo

En `ANSWER-POLICY.md` havia un ejemplo de formato que citaba "DS 8/2019
art. 47". El DS 8 tiene 24 articulos. No hay articulo 47. La cita la puse yo.

Lo grave: el ejemplo estaba **dentro del prompt del agente**. Un ejemplo es un
patron que el modelo copia, y si el patron lleva una cita falsa, la copia la
lleva. Un placeholder `[norma, articulo]` habria sido inofensivo; `art. 47`
parece real y no lo es.

**Regla:** en cualquier prompt, ejemplo o plantilla, un marcador de posicion se
escribe como marcador explicito (`[norma, articulo]`), nunca como algo que
parezca un valor real. La verificacion de citas es parte del diseno del prompt,
no un control posterior.

## 3. El cliente es la fuente de los numeros de operacion

`lease_ttl_s = 900` salio de un supuesto razonable y era **incompatible** con
la realidad: el cliente dijo que un plano tarda 2 a 4 horas. El supuesto
moriarelo al trabajo mismo, y cada muerte del lease es la oportunidad de
generar el plano duplicado que todo el resto del diseno evita.

Igual con el worker 24/7: el supuesto tecnico era "siempre vivo" porque asi se
diseñan los servicios. El cliente lo opera **por jornadas reservadas**, como
una empresa normal.

**Regla:** cuando un numero de operacion proviene de un supuesto, preguntarlo
en la ronda. El supuesto tecnico mas defendible sigue siendo incorrecto si la
empresa trabaja distinta. Y preguntar por el numero es mas barato que
descubrirlo en produccion.

## 4. "Se cayo" y "se apago" son fallos distintos

La distincion no aparece en ningun modelo de estado estandar, porque un
servicio siempre encendido no la necesita. Una PC que se enciende para
trabajar la necesita desde el primer dia: sin agenda, la deteccion de caida
miente todas las noches.

**Regla:** cuando el sistema dependa de que un recurso este disponible, el
primer diseno debe distinguir disponible-no-usado de no-disponible. Si no, el
dashboard se llena de falsas alarmas y deja de mirarse.

## 5. El rango no es la distribucion

El cliente dio "entre 2 y 4 horas". Es un techo y un piso, no una distribucion:
no dice si el caso tipico es 2 o 4, ni cuanto se mueve la cola.

**Regla:** un rango permite dimensionar el limite. No permite ajustarlo. Pedir
un valor medido es la accion siguiente, no un detalle.
