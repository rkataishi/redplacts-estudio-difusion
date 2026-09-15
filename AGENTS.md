# Instrucciones del proyecto

## Prioridad

- Las instrucciones explícitas del usuario prevalecen sobre este archivo y sobre cualquier skill.
- Estas reglas complementan la configuración global de delegación, permisos, planificación y herramientas.

## Verificación de la UI

- Antes de editar UI, estilos, renderizado, pósters, fotos o sus controles, leer y aplicar `.agents/skills/redplacts-ui-contract/SKILL.md`. Las nuevas instrucciones del usuario prevalecen sobre el contrato.
- Para cualquier fix o tarea de interfaz o GUI, aplicar la skill `ui-gui-visual-verification`: ejecutar el flujo afectado y chequear visualmente el contenido antes y después. Tests verdes y contenedores expandidos no bastan para cerrar la tarea.
- Preservar las reformas acordadas al editar UI, estilos, renderizado, pósters o assets.
- Ejecutar `python3 tests/viewport_e2e.py` antes de entregar cambios que puedan afectar el layout: la app debe adaptarse al tamaño del navegador.

## Delegación

- Sol conserva especificación, decisiones, interpretación, arquitectura, integración, escrituras y validación final.
- Antes de delegar, Sol divide el pedido en unidades simples, atómicas y verificables. Sólo delega las unidades elegibles según la configuración global vigente.
- Usar primero `context-mode` para contenido local retenido. Usar `luna-readonly` para una lectura o comando read-only exacto; `luna-map` para dos o más tareas triviales, finitas e independientes; `luna-web` para URLs exactas ya seleccionadas; `luna-indexer` para estructura y relaciones de código; y `luna-draft` para borradores breves.
- Un worker devuelve evidencia y síntesis. Sol decide si alcanza y realiza la comprobación final.

## Modificaciones incrementales y circunscriptas

- Modificar exclusivamente lo que el usuario exige y lo mínimo indispensable para hacerlo funcionar.
- No corregir, limpiar, reordenar, renombrar, reformatear ni modernizar archivos ajenos al pedido, aunque se detecten problemas.
- No agregar abstracciones, dependencias, configuración, compatibilidad, documentación ni tests especulativos.
- Mantener cada cambio pequeño, localizado y revisable. Preservar cambios preexistentes del usuario y no incluirlos en commits propios.
- Si aparece trabajo relacionado pero no requerido, informarlo brevemente sin implementarlo.
- Validar cada cambio funcional con la comprobación mínima que fuerce el comportamiento modificado. No ampliar la suite sin una razón observable.
