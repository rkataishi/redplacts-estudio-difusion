# Fase 2: modelo y harness

Estado: PENDIENTE

## Objetivo

Representar la composición como una matriz explícita `variante × cantidad` y construir el control automático antes de cambiar resultados.

## Trabajo

1. Definir perfiles para 2, 3 y 4 dentro del renderer propietario.
2. Separar geometría de personas, hero, título, reunión y moderación.
3. Mantener fallbacks seguros para 1, 5 y 6.
4. Añadir `tests/poster_layouts_e2e.py` para capturar dimensiones, issues y firma geométrica.
5. Exigir que las tres firmas de una variante sean distintas.

## Verificación

El harness debe fallar contra la línea base por el poster 03 de cuatro personas y por layouts sin cambio geométrico. Luego debe pasar las 27 combinaciones sin falsear la comprobación.
