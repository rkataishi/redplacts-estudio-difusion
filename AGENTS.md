# Instrucciones del proyecto

## Prioridad

- Las instrucciones explícitas del usuario prevalecen sobre este archivo y sobre cualquier skill.
- Estas reglas complementan la configuración global. Si una instrucción de `pstack` contradice la política global de delegación, permisos, planificación o herramientas, se aplica la política global.

## Pstack local

- Las skills importadas de [cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack) viven en `.agents/skills/` y se usan sólo en este repositorio.
- Para trabajo no trivial, usar `poteto-mode` como selector del playbook de `pstack`. Invocar una skill más específica cuando el pedido coincida directamente con ella.
- Aplicar los principios de `pstack` como criterios de diseño, implementación y verificación. No ejecutar mecánicamente instrucciones escritas para Cursor cuando la capacidad equivalente no exista en Codex.
- Traducir referencias de Cursor de esta forma:
  - `.cursor/skills/` -> `.agents/skills/` dentro de este repositorio.
  - `Task`, `subagent_type`, `generalPurpose`, agentes de Cursor y selección de modelos de `pstack` -> la matriz de delegación global vigente.
  - `/loop` y automatizaciones de Cursor -> persistencia normal de Codex dentro del alcance autorizado.
  - `create-skill` de Cursor -> `skill-creator` de Codex.
- `pstack` no autoriza por sí mismo escrituras externas, publicación, merge, push, despliegue ni cambios destructivos.

## Delegación

- Sol conserva especificación, decisiones, interpretación, arquitectura, integración, escrituras y validación final.
- Antes de delegar, Sol divide el pedido en unidades simples, atómicas y verificables. Sólo delega las unidades elegibles según la configuración global vigente.
- Usar primero `context-mode` para contenido local retenido. Usar `luna-readonly` para una lectura o comando read-only exacto; `luna-map` para dos o más tareas triviales, finitas e independientes; `luna-web` para URLs exactas ya seleccionadas; `luna-indexer` para estructura y relaciones de código; y `luna-draft` para borradores breves.
- Las instrucciones de `pstack` que pidan paneles, arenas, swarms o agentes especializados no amplían la delegación permitida. Convertir cada trabajo elegible a la ruta global correspondiente; si exige juicio, selección o arquitectura, lo resuelve Sol.
- Un worker devuelve evidencia y síntesis. Sol decide si alcanza y realiza la comprobación final.

## Modificaciones incrementales y circunscriptas

- Modificar exclusivamente lo que el usuario exige y lo mínimo indispensable para hacerlo funcionar.
- No corregir, limpiar, reordenar, renombrar, reformatear ni modernizar archivos ajenos al pedido, aunque se detecten problemas.
- No agregar abstracciones, dependencias, configuración, compatibilidad, documentación ni tests especulativos.
- Mantener cada cambio pequeño, localizado y revisable. Preservar cambios preexistentes del usuario y no incluirlos en commits propios.
- Si aparece trabajo relacionado pero no requerido, informarlo brevemente sin implementarlo.
- Validar cada cambio funcional con la comprobación mínima que fuerce el comportamiento modificado. No ampliar la suite sin una razón observable.
