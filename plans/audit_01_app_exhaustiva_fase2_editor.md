# Fase 2: editor, navegación, menús y scroll

Estado: PENDIENTE

## Objetivo

Probar que la estructura del editor permanece estable mientras cambia el contenido y que todo control sigue alcanzable.

## Matriz click a click

1. Recorrer los bloques laterales 01 a 05 hacia adelante, atrás y en orden alternado.
2. Abrir/cerrar cada acordeón, menú, selector y diálogo desde mouse y teclado.
3. Repetir con sidebar al inicio, mitad y final del scroll.
4. Añadir contenido hasta forzar overflow en cada bloque y verificar que el encabezado pueda volver al tope.
5. Verificar que `Generar piezas` quede en la zona de acciones inferior y nunca a mitad del contenido.
6. Verificar que ningún control quede tapado, recortado o fuera del área desplazable.
7. Cambiar bloque con foco dentro de input, botón, lista y menú abierto; comprobar foco y cierre correcto.
8. Redimensionar entre los cinco viewports con menús abiertos y cerrados.
9. Confirmar que `Texto para compartir` es el bloque 05 de la barra izquierda.
10. Confirmar ausencia del rótulo `3 expositores` y de contadores residuales equivalentes.

## Medidas

Registrar bounding boxes antes/después de cada mutación crítica, posición del CTA, dimensiones del panel y rango completo de scroll.

## Verificación

```sh
python3 tests/ui_smoke.py
python3 tests/stage_controls_e2e.py
```

Esperado: controles estables y alcanzables; sin salto estructural involuntario. Falla: desplazamiento no solicitado, scroll bloqueado, menú cortado o CTA flotando entre campos.
