# Fase 9: proyectos, diálogos y exportaciones

Estado: PENDIENTE

## Objetivo

Comprobar persistencia, acciones globales, diálogos y archivos generados con recorridos completos.

## Recorrido

1. Nuevo proyecto con estado vacío y confirmación cuando haya cambios.
2. Cancelar y aceptar confirmaciones; verificar que cancelar no muta estado.
3. Cargar demo desde estado limpio y modificado.
4. Guardar B; reiniciar; cargar B; comparar todos los campos, orden y crops.
5. Cargar archivo inválido, versión inesperada y cancelación del picker.
6. Recargar navegador y comprobar persistencia local prevista.
7. Abrir/cerrar Identidad, Acerca de, Demo y confirmaciones por botón, escape y foco.
8. Exportar cada PNG individual y verificar firma, dimensiones y contenido no vacío.
9. Exportar ZIP y verificar nueve PNG con nombres/dimensiones esperados.
10. Exportar TXT y comparar contenido visible.
11. Exportar proyecto y reimportarlo en una sesión nueva.
12. Confirmar que una descarga fallida no altera el proyecto.

## Verificación

```sh
python3 tests/project_actions_e2e.py
python3 tests/dialogs_e2e.py
python3 tests/downloads_e2e.py
```

Esperado: round-trip exacto y descargas válidas. Falla: pérdida silenciosa, diálogo sin cierre accesible, archivo corrupto o dimensiones incorrectas.
