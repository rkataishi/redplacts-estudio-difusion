# Red PLACTS · Estudio de difusión

App estática de un solo archivo para generar piezas de difusión a partir de un formulario: **tres pósters completos + tres versiones breves para redes** (estado/historia/publicación). Usa los assets de identidad de Red PLACTS ya integrados y no requiere backend.

Entrypoint publicado: `index.html` en la raíz (GitHub Pages sirve `index.html` por defecto).

## Descripción

- Formulario en 4 pasos: contenido, personas (1–6 expositores + hasta 2 moderadores), imágenes (fondo + hero), encuentro (fecha/hora/plataforma/URL/QR).
- Seis variantes compiladas en `canvas`: 3 pósters (Institucional / Panorámica / Editorial) y 3 para redes (Estado / Historia / Publicación) conmutables con `Pósters` / `Estados e Instagram`.
- Exportación sin recorte ni estirado: PNG por variante o ZIP del grupo visible (`Exportar los 3`). El ZIP de redes incluye además `texto-para-compartir.txt` con la URL completa (el PNG no tiene enlaces clicables).
- Identidad incorporada: 8 SVGs en `window.BRAND_ASSETS` como `data:image/svg+xml;base64` + fondo de ondas reconstruido en `window.WAVE_ASSET`. Los logos se colocan con proporciones y colores originales. Tipografía por defecto `Clear Sans` cargada desde CDN si no está instalada (alternativas: Lato / Open Sans / Inter).

## Uso local

Sin dependencias ni build. Cualquiera de estas dos formas:

1. **Apertura directa:** doble clic en `index.html`.
2. **Servidor local** (evita restricciones `file://` en algunos navegadores para fuentes/QR):
   ```bash
   python3 -m http.server 8000
   # abrir http://localhost:8000/
   ```
   o
   ```bash
   npx serve .
   ```

Flujo: completar los 4 apartados → `Compilar las seis versiones` → cambiar grupo/formato → `PNG` (variante) o `Exportar los 3` (ZIP).

## Privacidad y persistencia en el cliente

- **100 % local.** No hay subida a servidores, no se publican eventos y no se envían imágenes. Todo se procesa en el navegador (canvas, QR en JS).
- **Borrador automático** en este navegador:
  - Intenta `IndexedDB` (`redplacts-estudio-v2`, objectStore `draft`, key `current`) → `#draft-status: "Borrador guardado en este navegador"`.
  - Fallback `localStorage` (`redplacts-estudio-v2`) con el mismo mensaje.
  - Si ambos fallan (modo privado estricto/cuota), `storageMode='none'` → `"Usa Guardar proyecto para conservar los cambios"`.
  - Al recargar, `loadDraft()` restaura y muestra `"Borrador recuperado en este navegador"` o `"Ejemplo listo para editar"`.
- **Proyecto portátil:** `Guardar proyecto` descarga `${stem}-proyecto.json` con todo el estado (textos + imágenes ya optimizadas + encuadres). `Abrir` lo revalida con `validateProject()`, pide confirmación y rehidrata.

Solo se requiere conexión para cargar una fuente no instalada desde su CDN; el PNG final incrusta el render y no depende de fuentes externas al abrirlo.

## Mecanismo de adjuntos

- **Entrada:** `<input type="file" accept="image/jpeg,image/png,image/webp">` por persona (foto), fondo y hero. Soporta drag & drop en `upload-zone`. Límite **20 MB** por imagen y **50 MP** (ancho×alto) antes de optimizar.
- **Optimización (`optimiseImage`):** crea `ObjectURL`, valida dimensiones, redibuja en canvas con `bound = 1100` (fotos de persona) o `2300` (fondo/hero), `toDataURL(type, 0.90)` (JPEG 90 % / PNG). Retorna `{data, name, width, height, crop:{x:50,y:50,zoom:1}}`. Se revoca el ObjectURL al terminar.
- **Almacenamiento:** la imagen queda como **data URL** dentro del estado en memoria y, si se guarda, dentro del JSON del proyecto. De ahí que un proyecto con varias fotos pueda pesar varios MB (límite de importación **45 MB**).
- **Encuadre no destructivo:** controles `Horizontal / Vertical / Acercar (100–180 %)` + opacidad del fondo (`bgOpacity` 0–38 %). El original optimizado se conserva y solo cambian `crop`/`bgOpacity`.
- **Logos/identidad:** no son adjuntos del usuario; los 8 SVGs vienen empaquetados como base64 en el HTML y no necesitan subirse ni reconstruirse por evento.

## Publicación recomendada — GitHub Pages

Recomendada porque es contenido **estático sin build ni Node**.

1. Repositorio en GitHub con `index.html` en la raíz (y `.github/workflows/pages.yml` ya incluido).
2. `Settings → Pages → Build and deployment → Source: GitHub Actions`.
3. Push a `main` (o `Run workflow` manual) — el workflow publica la raíz. La URL queda en `https://<usuario>.github.io/<repo>/`.

Workflow incluido (`.github/workflows/pages.yml`):

- Triggers: `push` a `main` + `workflow_dispatch`.
- Permisos mínimos: `contents: read`, `pages: write`, `id-token: write`.
- Acciones oficiales actuales sin Node/build: `actions/checkout@v4` → `actions/configure-pages@v5` → `actions/upload-pages-artifact@v3` (path `.`) → `actions/deploy-pages@v4`.
- Concurrencia `pages` con `cancel-in-progress: false`.

No requiere configurar `gh-pages` branch ni `npm run build`.

## Vercel no es necesario

GitHub Pages resuelve el hosting estático sin costo adicional ni configuración de framework. Vercel es válido para apps con SSR/funciones, pero este proyecto es un único HTML + assets inline; añadir Vercel solo sumaría complejidad y un proveedor extra sin beneficio. Si ya usás Vercel por otro motivo podés desplegarlo igual, pero **no es requerido ni recomendado** para este caso.

## Estructura

```
.
├── index.html                         # entrypoint en raíz
├── .github/workflows/pages.yml        # deploy Pages sin build
├── .gitignore
└── README.md
```

Sin `LICENSE` — el titular no eligió licencia aún; todos los derechos reservados por defecto.

## Notas

- QR generado offline con `QRCode` (MIT, Kazuhiko Arase) embebido en el HTML; ZIP armado con `zipStore` (STORE sin compresión) y `downloadBlob` vía `URL.createObjectURL`.
- Si el texto no cabe con tipografía legible, la app bloquea la exportación de esa variante y pide abreviar o usar Historia 9:16.
