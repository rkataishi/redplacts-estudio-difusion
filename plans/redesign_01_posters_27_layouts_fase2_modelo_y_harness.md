# Fase 2: modelo y harness

Estado: EN REVISIÓN

## Objetivo

Representar la composición como una matriz explícita `variante × cantidad` y construir el control automático antes de cambiar resultados.

## Trabajo

1. Definir perfiles para 2, 3 y 4 dentro del renderer propietario.
2. Separar geometría de personas, hero, título, reunión y moderación.
3. Mantener fallbacks seguros para 1, 5 y 6.
4. Añadir `tests/poster_layouts_e2e.py` para capturar dimensiones, issues y firma geométrica.
5. Exigir que las tres firmas de una variante sean distintas.
6. Registrar la caja de cada card y exigir ancho y alto iguales dentro de cada uno de los 27 estados.
7. Exigir que las firmas geométricas de 06 y 09 sean distintas para cada cantidad.
8. Modelar cuatro grupos editables de recuadros con estilo, modo de color, acento y escala tipográfica.
9. Validar listas cerradas, escalas acotadas y compatibilidad con proyectos anteriores.
10. Rechazar podios, cards elevadas y cualquier texto auditado menor a 17 px.

## Verificación

El harness debe fallar contra la línea base por el poster 03 de cuatro personas y por layouts sin cambio geométrico. Luego debe pasar las 27 combinaciones sin falsear la comprobación.

Resultado: `POSTER_LAYOUTS_OK states=27 variants=9`; las 27 firmas de composición son explícitas y los tres casos de cada variante son distintos.

Revisión 2026-09-14: el audit registra `speaker-card-0` a `speaker-card-3`. El harness rechaza medidas distintas dentro de un estado y firmas iguales entre 06 y 09. Resultado real: `POSTER_LAYOUTS_OK states=27 variants=9 elapsed=7.84s`.
