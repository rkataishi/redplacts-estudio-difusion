# Redesign 01: veintisiete composiciones de posters

Estado: EN EJECUCIÓN, REVISIÓN DE JERARQUÍA Y PERSONALIZACIÓN
Fecha de aprobación: 2026-09-13
Revisión aprobada: 2026-09-14
Segunda revisión aprobada: 2026-09-14
Propietario: Sol
Rama: `main`
Punto de partida: `0981ba7`

## Objetivo

Reconstruir las nueve variantes para que cada una tenga composiciones explícitas y visualmente distintas con 2, 3 y 4 expositores; usar las referencias de `insumos/inspiraciones poster/` solamente para distribución, escala, ritmo y relación entre fotografía y texto; corregir la galería y las acciones del preview; y ampliar el layer local para comentar una variante concreta.

## Resultado exigido

1. Existen 27 contratos visuales identificables: nueve variantes por tres cantidades.
2. Tres expositores es el caso predeterminado de demostración y revisión.
3. Ninguna combinación 2/3/4 muestra fallback, warning de capacidad, texto fuera del lienzo, solapamientos o retratos ilegibles.
4. Dentro de cada variante, 2, 3 y 4 cambian la geometría de las personas, no sólo el número de elementos.
5. Las variantes 01–09 conservan una identidad compositiva propia; 05 y 07 dejan de ser duplicados.
6. Las nueve miniaturas se ven completas en el área disponible sin el título `Vista general`.
7. `Descargar PNG` queda junto a `Exportar los 9` y siempre descarga la variante seleccionada.
8. El layer local permite elegir 01–09, seleccionar elementos internos del póster renderizado y adjunta elemento, coordenadas, composición, variante y cantidad de expositores a cada comentario.
9. Preview, ampliación, thumbnail y PNG representan el mismo layout.
10. Los flujos existentes de edición, proyecto y exportación continúan funcionando.
11. Todas las cards de expositores de una composición tienen exactamente el mismo ancho y alto; ninguna persona recibe una card principal, dominante o secundaria.
12. Las variantes 06 y 09 usan geometrías distintas con 2, 3 y 4 expositores.
13. El selector local de elementos internos usa cursor de selección y no conserva el cursor de ampliación del canvas mientras está activo.
14. Dos o tres expositores comparten la misma línea superior e inferior. Cuatro expositores usan una sola fila o una retícula regular de dos por dos, sin cards escalonadas ni una posición central elevada.
15. `Lato` es la fuente inicial de proyectos nuevos. La tipografía del póster tiene escala general de 115 % y ningún texto auditado baja de 17 px en el lienzo base.
16. El paso 03 de la sidebar permite editar título, expositores, moderación y fecha/acceso. Cada grupo admite estilo `Vibrante`, `Transparente` o `Degradado`; color `Predeterminado`, `Oscuro` o `Acento`; acento verde, azul o ciruela; y escala tipográfica propia.
17. Los estilos y tamaños se guardan en el proyecto, se validan al abrirlo y actualizan preview, ampliación, miniaturas y exportaciones.

## Alcance

Incluye `designs.js`, `index.html`, pruebas E2E de layouts y controles, el layer ignorado `.local-review/`, y evidencia bajo `.audit/poster-redesign-2026-09-12/`.

No incluye colores libres fuera de la paleta aprobada, cambiar logotipos, copiar marcas de las referencias, agregar dependencias, publicar, desplegar o hacer push. Los materiales de `insumos/` permanecen sin versionar. Los casos de 1, 5 y 6 personas conservan soporte mediante layouts seguros, pero no forman parte de la matriz visual explícita 2/3/4.

## Matriz de composiciones

| Variante | 2 expositores | 3 expositores | 4 expositores |
| --- | --- | --- | --- |
| 01 Institucional | dos fichas amplias | tres columnas equilibradas | retícula 2 × 2 |
| 02 Panorámica | dúo lateral igual | tres retratos panorámicos iguales | franja de cuatro retratos iguales |
| 03 Editorial | dos columnas con biografía | tres columnas editoriales | cuatro retratos a sangre |
| 04 Ushuaia cuadrada | dúo alineado | tres cards alineadas | retícula regular 2 × 2 |
| 05 Ushuaia publicación | dúo alineado | tres fichas alineadas | retícula regular 2 × 2 |
| 06 Ushuaia historia | dos retratos verticales | tres columnas verticales | cuatro bandas fotográficas |
| 07 Digital publicación | dos tarjetas alineadas | tres círculos alineados | franja horizontal de cuatro iguales |
| 08 Digital cuadrada | dúo alineado | tres retratos alineados | retícula regular 2 × 2 |
| 09 Digital historia | dos bandas horizontales | tres bandas horizontales | retícula horizontal 2 × 2 |

## Fases

1. [Fase 1: referencias y baseline](redesign_01_posters_27_layouts_fase1_referencias_y_baseline.md).
2. [Fase 2: modelo y harness](redesign_01_posters_27_layouts_fase2_modelo_y_harness.md).
3. [Fase 3: posters 01–03](redesign_01_posters_27_layouts_fase3_posters_01_03.md).
4. [Fase 4: posters 04–06](redesign_01_posters_27_layouts_fase4_posters_04_06.md).
5. [Fase 5: posters 07–09](redesign_01_posters_27_layouts_fase5_posters_07_09.md).
6. [Fase 6: editor y revisión local](redesign_01_posters_27_layouts_fase6_editor_y_revision_local.md).
7. [Fase 7: validación y limpieza](redesign_01_posters_27_layouts_fase7_validacion_y_limpieza.md).

## Método

Cada unidad declara una hipótesis, hace el cambio mínimo y termina con una ejecución real. El veredicto es `VERIFIED`, `NOT VERIFIED` o `INCONCLUSIVE`. La siguiente unidad no comienza si la anterior rompe su caso o una regresión existente.

## Verificación final

```sh
python3 tests/poster_layouts_e2e.py
python3 tests/stage_controls_e2e.py
python3 tests/downloads_e2e.py
python3 tests/image_canvas_e2e.py
python3 tests/ui_smoke.py
git diff --check
```

Además, Browser Use recorre 01–09 con 2, 3 y 4 expositores, guarda 27 capturas comparables e inspecciona cada imagen. Falla cualquier canvas vacío, fallback, warning, card de distinto ancho o alto, podio o card elevada, texto menor a 17 px, contraste insuficiente en un modo, igualdad geométrica entre 06 y 09, corte, superposición, miniatura incompleta, descarga incorrecta o error de consola.

## Criterio visual obligatorio

1. Igualdad: misma medida, línea, tratamiento, escala tipográfica y área fotográfica para todas las personas de una composición.
2. Sin podio: ninguna card aislada queda por encima, centrada como vértice o agrandada respecto de sus pares.
3. Legibilidad: el audit del canvas informa un mínimo de 17 px; nombre, fecha, acceso y textos secundarios se leen en preview ampliado y PNG.
4. Contraste: cada combinación de estilo y color mantiene texto, fondo y borde distinguibles; los modos oscuros y de acento usan texto claro.
5. Estabilidad: cambiar estilo, color, acento o tamaño no mueve controles, rompe menús ni altera el orden de participantes.
6. Persistencia: guardar y volver a abrir conserva todos los ajustes visuales.

## Robustez y eficiencia

La línea base registra duración de composición y 27 capturas. El cierre repite el mismo recorrido. Sólo se optimiza trabajo medido. La matriz declarativa debe evitar cálculos duplicados y mantener las validaciones en las entradas externas.

## Evidencia

- Referencias: `.audit/poster-redesign-2026-09-12/references/`.
- Baseline: `.audit/poster-redesign-2026-09-12/baseline/`.
- Decisiones: `.audit/poster-redesign-2026-09-12/decisions.tsv`.
- Resultados: `.audit/poster-redesign-2026-09-12/after/`.
- Comentarios del usuario: `.local-review/comments.json`.

## Gates

- Gate 0, aprobado: alcance, matriz y mapa de archivos.
- Gate 1: commit local del plan antes de modificar producción.
- Gate 2: harness demuestra el defecto actual y luego las 27 combinaciones válidas.
- Gate 3: cada grupo de tres posters tiene comparación visual antes/después.
- Gate 4: recorrido completo, suite y exportaciones reales.
- Gate 5: aprobación del usuario antes de marcar fases `_done` y graduar.
- Push y publicación quedan fuera de esta aprobación.

## Progreso

- [x] Gate 0 aprobado.
- [x] Gate 1: plan versionado en `9d1057e` antes de editar producción.
- [x] Baseline visual de 27 estados capturado.
- [x] Gates 2–4 y fases 2–7 ejecutados y verificados.
- [x] Revisión 2026-09-14 aprobada por el usuario: cards iguales, 06 y 09 distintas y cursor local corregido.
- [x] Revisión 2026-09-14 implementada y recorrida en 27 estados con Browser Use.
- [x] Segunda revisión 2026-09-14 aprobada: eliminar podios, aumentar tipografía y añadir controles por recuadro.
- [ ] Contrato sin jerarquía, tipografía y personalización implementado.
- [ ] Aprobación de graduación.

Evidencia de la revisión: `.audit/poster-redesign-2026-09-12/revision-2026-09-14/after/`. El renderer informó `POSTER_LAYOUTS_OK states=27 variants=9 elapsed=7.84s`. Las pruebas de controles, descargas, imágenes y flujo principal pasaron. El localhost quedó abierto con tres expositores y el layer local visible.
