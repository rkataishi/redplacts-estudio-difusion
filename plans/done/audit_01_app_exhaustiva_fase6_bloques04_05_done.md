# Fase 6: fecha/reunión y texto para compartir

Estado: COMPLETA

## Objetivo

Verificar por separado los bloques laterales 04 y 05 y su efecto sobre la composición.

## Recorrido bloque 04

1. Alternar fecha/hora/modalidad/sede/enlace en todas las combinaciones expuestas.
2. Confirmar campos condicionales, validación y representación en las nueve piezas.
3. Probar ausencia de datos opcionales sin reservar aire visual.

## Recorrido bloque 05

1. Confirmar ubicación permanente como quinto bloque de la barra izquierda.
2. Generar texto desde proyectos A, B y C.
3. Editar manualmente, copiar, seleccionar todo, borrar y regenerar.
4. Verificar saltos, caracteres especiales, orden de datos y ausencia de información oculta.
5. Confirmar que crecer el texto aumenta solamente el área desplazable correspondiente y no mueve el CTA a mitad del bloque.

## Verificación

```sh
python3 tests/content_meeting_e2e.py
python3 tests/downloads_e2e.py
```

Esperado: bloque 05 estable, texto completo y geometría sin huecos. Falla: orden incorrecto, texto truncado o reflow del editor.

## Resultado

- Fecha, horarios, zona, acceso, URL, sede y QR se alternaron y validaron sin residuos.
- El bloque 05 permanece en la barra lateral; su texto se copia y descarga completo como TXT.
- El crecimiento del contenido no mueve el CTA ni impide alcanzar el final del panel.
- `content_meeting_e2e.py`, `stage_controls_e2e.py` y `downloads_e2e.py` terminaron en código 0.
