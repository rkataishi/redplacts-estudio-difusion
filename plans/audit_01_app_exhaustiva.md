# Audit 01: auditoría integral de Red PLACTS

Estado: APROBADO, EN EJECUCIÓN
Fecha de aprobación: 2026-09-12
Propietario: Sol
Rama: `main`
Punto de partida: `4fa2bbc`

## Objetivo

Recorrer la aplicación como una persona usuaria, click a click y estado por estado; detectar y reproducir defectos funcionales y visuales; corregir solamente defectos demostrados; eliminar código probado como inalcanzable o redundante; y cerrar con evidencia actual de funcionamiento, exportaciones reales y revisión visual de las nueve piezas.

## Resultado exigido

La auditoría termina solamente cuando:

1. Cada control visible tiene un recorrido registrado o un bloqueo explícito.
2. Las cinco secciones laterales conservan posición, scroll y acceso a sus controles al crecer el contenido.
3. El preview muestra completa la pieza vertical dentro del espacio disponible, sin desplazar herramientas ni thumbnails.
4. Las nueve visualizaciones usan la imagen hero con jerarquía, recorte y alineación comprensibles.
5. Las variantes 04, 05, 06 y 07 distribuyen su espacio sin huecos arbitrarios.
6. Subir archivos, agregar texto, ordenar personas, abrir menús y cambiar opciones no rompe la geometría del editor.
7. Guardar, cargar, reiniciar, usar demo y exportar conserva o reemplaza el estado correcto.
8. PNG, ZIP, TXT y proyecto exportado se generan y contienen datos verificables.
9. La aplicación funciona en escritorio, tablet y móvil, con navegación por teclado básica y sin errores de consola durante el recorrido.
10. Toda eliminación de código tiene evidencia de inalcanzabilidad y una comprobación posterior.

## Alcance

Incluye `index.html`, `designs.js`, las pruebas E2E existentes y los artefactos de auditoría. Incluye todos los controles, diálogos, cargas, recortes, preview, thumbnails, variantes y exportaciones actualmente expuestos por la aplicación.

No incluye rediseñar la identidad, agregar features, migrar de tecnología, introducir dependencias, publicar, hacer push o modificar los materiales preexistentes no versionados (`.tmp-ux-review/`, `ESTADO_Y_PLAN.md`, `insumos/`).

## Proyectos de prueba

| ID | Estado | Propósito |
| --- | --- | --- |
| A mínimo | Campos obligatorios mínimos, una persona, sin opcionales | Detectar dependencias ocultas y layouts vacíos |
| B realista | Texto, fecha, modalidad, hero, expositores y moderación realistas | Validar el recorrido habitual |
| C máximo | Textos largos, máximas personas razonables, imágenes y opcionales | Forzar overflow, scroll y redistribución |
| D vacíos | Opcionales agregados y luego vaciados/eliminados | Detectar residuos de estado y huecos |
| E errores | Tipos/tamaños inválidos, acciones incompletas, cancelaciones | Validar límites y recuperación |

## Matriz visual obligatoria

| Superficie | Viewports / tamaños |
| --- | --- |
| Editor | 1280×757, 1440×900, 1920×1080, 768×1024, 390×844 |
| Pieza 01 | 1080×1350 |
| Pieza 02 | 1080×1920 |
| Pieza 03 | 1080×1080 |
| Pieza 04 | 1200×628 |
| Pieza 05 | 1600×900 |
| Pieza 06 | 1080×1080 |
| Pieza 07 | 1200×628 |
| Pieza 08 | 1080×1920 |
| Pieza 09 | 1080×1350 |

## Fases y dependencias

1. [Fase 1: línea base](audit_01_app_exhaustiva_fase1_baseline.md). No se edita producto antes de capturarla.
2. [Fase 2: editor y navegación](audit_01_app_exhaustiva_fase2_editor.md). Depende de fase 1.
3. [Fase 3: contenido](audit_01_app_exhaustiva_fase3_contenido.md). Depende de fase 2.
4. [Fase 4: personas](audit_01_app_exhaustiva_fase4_personas.md). Depende de fase 2.
5. [Fase 5: imágenes](audit_01_app_exhaustiva_fase5_imagenes.md). Depende de fase 2.
6. [Fase 6: bloques 04 y 05](audit_01_app_exhaustiva_fase6_bloques04_05.md). Depende de fases 3 a 5.
7. [Fase 7: preview](audit_01_app_exhaustiva_fase7_preview.md). Depende de fases 2 a 6.
8. [Fase 8: nueve piezas](audit_01_app_exhaustiva_fase8_piezas.md). Depende de fase 7.
9. [Fase 9: proyectos, diálogos y exportación](audit_01_app_exhaustiva_fase9_proyectos_exportacion.md). Depende de fases 3 a 8.
10. [Fase 10: responsive y accesibilidad](audit_01_app_exhaustiva_fase10_responsive_accesibilidad.md). Depende de fases 2 a 9.
11. [Fase 11: limpieza](audit_01_app_exhaustiva_fase11_limpieza.md). Depende de evidencia de fases anteriores.
12. [Fase 12: validación final](audit_01_app_exhaustiva_fase12_validacion_final.md). Depende de todas las anteriores.

## Método de ejecución

Cada hallazgo se procesa como una unidad verificable:

1. Hipótesis concreta y estado exacto que la fuerza.
2. Captura o medición antes del cambio.
3. Causa raíz localizada en fuente.
4. Cambio mínimo y circunscripto.
5. Prueba funcional directa.
6. Nueva captura con el mismo viewport y estado.
7. Veredicto `VERIFIED`, `NOT VERIFIED` o `INCONCLUSIVE` en `.audit/audit_01_decisions.tsv`.

No se acepta como evidencia visual una captura no abierta e inspeccionada durante esta ejecución. Las pruebas automáticas complementan, no reemplazan, el recorrido real.

## Comandos comunes

Servidor local:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Resultado esperado: servidor activo y `curl -I http://127.0.0.1:8000/` devuelve HTTP 200. Falla: puerto inaccesible, documento no servido o recursos 4xx/5xx.

Suite completa:

```sh
for test in tests/*_e2e.py tests/ui_smoke.py; do python3 "$test"; done
```

Resultado esperado: todos los scripts terminan con código 0. Falla: excepción, timeout, aserción, descarga ausente o consola con error no esperado.

Control de cambios:

```sh
git diff --check
git status --short
git diff --stat
```

Resultado esperado: sin errores de whitespace y solamente archivos del alcance. Falla: cambios ajenos, archivos temporales incorporados o diff no explicable por hallazgos.

## Robustez y eficiencia

La línea base registra tiempos de carga, dimensiones y duración de la suite. El cierre repite las mismas mediciones. Se investiga una regresión si la carga o la suite aumenta de manera apreciable, si un render agrega trabajo repetido visible o si el preview rehace geometría sin una acción de usuario. No se agregan optimizaciones sin una medición que las justifique.

## Evidencia y artefactos

- Informe: `docs/reports/redplacts_app_audit_2026-09-12.md`
- Decisiones: `.audit/audit_01_decisions.tsv`
- Línea base: `.audit/baseline/`
- Capturas corregidas: `.audit/screenshots/`
- Exportaciones verificadas: `.audit/exports/`
- Geometría y tiempos: `.audit/measurements/`

## Gates de aprobación

- Gate 0, aprobado: mapa, alcance y creación de este plan.
- Gate 1: commit local del plan antes de editar producto.
- Gate 2: línea base capturada e inspeccionada.
- Gate 3: cada fase queda cerrada con evidencia y estado actualizado.
- Gate 4: el usuario debe aprobar la graduación/archivo del plan terminado.
- Publicación y push quedan fuera de esta aprobación.

## Progreso

- [x] Alcance y mapa aprobados por el usuario.
- [x] Commit local del plan.
- [x] Fase 1.
- [ ] Fase 2.
- [ ] Fase 3.
- [ ] Fase 4.
- [ ] Fase 5.
- [ ] Fase 6.
- [ ] Fase 7.
- [ ] Fase 8.
- [ ] Fase 9.
- [ ] Fase 10.
- [ ] Fase 11.
- [ ] Fase 12.
- [ ] Aprobación de graduación.
