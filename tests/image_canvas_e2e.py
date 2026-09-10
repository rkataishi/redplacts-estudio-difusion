#!/usr/bin/env python3
"""
Prueba E2E visual independiente: demuestra que tres clases de imagen modifican el canvas.
- Reutiliza helpers desde ui_smoke (_driver, real_click, wait_js, _write_solid_png, assert_no_severe_logs, BASE_URL)
- Flujo: abrir/limpiar storage compatible → esperar ready → completar title/date/time/timezone → Generar
         → colección social variante Estado → canvas visible → /tmp/ui-e2e 01-base
         → fingerprint JS estable → PNGs sólidos 2400x1600 (foto azul, fondo rojo, hero verde)
         → upload foto speaker → espera state/socialPhotos/render/fingerprint → 02-photo
         → upload background → espera state/bgOpacity/fingerprint → 03-background
         → upload hero → espera state/fingerprint → 04-hero
         → verifica CTA Reemplazar y consola sin SEVERE → cleanup driver/PNGs (conserva screenshots)
"""
import os
import sys
import time
import traceback
import tempfile
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- reutilizar helpers desde ui_smoke (spec) o replica mínimo ---
try:
    from tests.ui_smoke import _driver, real_click, wait_js, _write_solid_png, assert_no_severe_logs, BASE_URL
except ImportError:
    try:
        from ui_smoke import _driver, real_click, wait_js, _write_solid_png, assert_no_severe_logs, BASE_URL  # type: ignore
    except ImportError:
        # replica mínima requerida si ui_smoke no está disponible
        import base64 as _b64
        import struct as _struct
        import zlib as _zlib
        from selenium import webdriver as _webdriver
        from selenium.webdriver.chrome.options import Options as _Options

        BASE_URL = os.environ.get("PLACTS_BASE_URL", "http://127.0.0.1:8000")
        TIMEOUT_FALLBACK = 15

        def _driver():
            opts = _Options()
            opts.add_argument("--headless=new")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument("--disable-gpu")
            opts.add_argument("--window-size=1280,900")
            try:
                opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})
            except Exception:
                pass
            d = _webdriver.Chrome(options=opts)
            d.set_window_size(1280, 900)
            return d

        def wait_js(driver, js_predicate, timeout=TIMEOUT_FALLBACK, msg=""):
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script(f"return !!({js_predicate})"),
                message=msg or f"timeout esperando JS: {js_predicate}",
            )

        def real_click(driver, element):
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
            time.sleep(0.15)
            try:
                element.click()
            except Exception:
                driver.execute_script("arguments[0].click();", element)

        def assert_no_severe_logs(driver):
            try:
                logs = driver.get_log("browser")
            except Exception:
                return
            severe = [l for l in logs if l.get("level") == "SEVERE"]
            assert not severe, f"Console SEVERE detectado: {severe} | logs completos: {logs}"

        def _write_solid_png(path, width=2400, height=1600, rgb=(180, 180, 190)):
            def _chunk(chunk_type, data):
                c = chunk_type + data
                return _struct.pack(">I", len(data)) + c + _struct.pack(">I", _zlib.crc32(c) & 0xffffffff)

            sig = b"\x89PNG\r\n\x1a\n"
            ihdr_data = _struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
            ihdr = _chunk(b"IHDR", ihdr_data)
            row = b"\x00" + bytes(rgb) * width
            raw = row * height
            compressed = _zlib.compress(raw)
            idat = _chunk(b"IDAT", compressed)
            iend = _chunk(b"IEND", b"")
            with open(path, "wb") as f:
                f.write(sig + ihdr + idat + iend)


TIMEOUT = 15
SCREENSHOT_DIR = Path("/tmp/ui-e2e")

# JS fingerprint: toma getImageData del canvas visible, muestrea bytes y devuelve hash numérico estable + dimensiones
CANVAS_FINGERPRINT_JS = r"""
const fn = () => {
  const pickVisibleCanvas = () => {
    let card = document.querySelector('.poster-card.is-selected:not([hidden])');
    if (card && card.querySelector('canvas')) return card.querySelector('canvas');
    card = document.querySelector('.poster-card.is-selected');
    if (card && card.querySelector('canvas')) {
      const c = card.querySelector('canvas');
      const r = c.getBoundingClientRect();
      if (r.width > 0 && r.height > 0) return c;
    }
    const all = [...document.querySelectorAll('.poster-card')];
    for (const el of all) {
      if (el.hidden) continue;
      const style = window.getComputedStyle(el);
      if (style.display === 'none' || style.visibility === 'hidden') continue;
      const rect = el.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) continue;
      const c = el.querySelector('canvas');
      if (c) {
        const cr = c.getBoundingClientRect();
        if (cr.width > 0 && cr.height > 0) return c;
      }
    }
    // fallback: primer canvas visible
    const canvases = [...document.querySelectorAll('canvas')];
    for (const c of canvases) {
      const r = c.getBoundingClientRect();
      if (r.width > 0 && r.height > 0 && c.width > 0 && c.height > 0) return c;
    }
    return null;
  };
  const canvas = pickVisibleCanvas();
  if (!canvas) return {error: 'no-canvas-visible', width: 0, height: 0, hash: 0};
  if (!canvas.width || !canvas.height) return {error: 'invalid-dimensions', width: canvas.width||0, height: canvas.height||0, hash: 0};
  const ctx = canvas.getContext('2d');
  if (!ctx) return {error: 'no-context', width: canvas.width, height: canvas.height, hash: 0};
  const w = canvas.width, h = canvas.height;
  try {
    const img = ctx.getImageData(0, 0, w, h);
    const data = img.data;
    // muestreo estable: ~8000 lecturas
    const targetSamples = 8000;
    let step = Math.max(4, Math.floor(data.length / targetSamples) & ~3);
    if (step === 0) step = 4;
    let hash = 2166136261 >>> 0;
    for (let i = 0; i < data.length; i += step) {
      hash ^= data[i];
      hash = Math.imul(hash, 16777619) >>> 0;
    }
    hash ^= w; hash = Math.imul(hash, 16777619) >>> 0;
    hash ^= h; hash = Math.imul(hash, 16777619) >>> 0;
    return {hash: hash>>>0, width: w, height: h, bytes: data.length, step: step};
  } catch (e) {
    return {error: String(e), width: w, height: h, hash: 0};
  }
};
return fn();
"""

def canvas_fingerprint(driver):
    """Ejecuta JS fingerprint y valida retorno."""
    res = driver.execute_script(f"return (function(){{ {CANVAS_FINGERPRINT_JS} }})();")
    # driver.execute_script ya retorna el objeto; si vino envuelto asegurar keys
    if not isinstance(res, dict):
        raise AssertionError(f"canvas_fingerprint retorno inesperado: {res}")
    if res.get("error"):
        raise AssertionError(f"canvas_fingerprint error: {res}")
    if not res.get("hash") or not res.get("width") or not res.get("height"):
        raise AssertionError(f"canvas_fingerprint dimensiones/hash inválidos: {res}")
    return res

def _wait_fingerprint_change(driver, prev_hash, timeout=30, label="fingerprint"):
    """Espera a que fingerprint cambie respecto a prev_hash; retorna nuevo fingerprint."""
    t0 = time.time()
    last = None
    def _check(d):
        nonlocal last
        try:
            fp = canvas_fingerprint(d)
            last = fp
            return fp.get("hash") != prev_hash and fp.get("hash") != 0
        except Exception:
            return False
    try:
        WebDriverWait(driver, timeout).until(_check, message=f"timeout esperando {label} distinto de {prev_hash}")
    except Exception as e:
        cur = None
        try:
            cur = driver.execute_script(f"return (function(){{ {CANVAS_FINGERPRINT_JS} }})();")
        except Exception:
            pass
        raise AssertionError(f"{label} no cambió tras {timeout}s: prev={prev_hash} last={last} cur_js={cur} err={e}") from e
    elapsed = time.time() - t0
    print(f"  fingerprint {label} cambió en {elapsed:.2f}s: {prev_hash} -> {last['hash']} ({last['width']}x{last['height']})")
    return last, elapsed

def run():
    driver = None
    tmp_files = []
    start_all = time.time()
    try:
        driver = _driver()
        # 1) abrir y limpiar storage de forma compatible (igual que ui_smoke)
        driver.get(BASE_URL)
        WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState === 'complete'"))
        driver.execute_script("try{localStorage.clear();}catch(e){} try{sessionStorage.clear();}catch(e){}")
        try:
            driver.execute_async_script(
                """
                const cb = arguments[arguments.length-1];
                (async () => {
                    try{
                        if (window.indexedDB && indexedDB.databases) {
                            const dbs = await indexedDB.databases();
                            for (const db of dbs) { try{ indexedDB.deleteDatabase(db.name);}catch(e){} }
                        } else {
                            try{ indexedDB.deleteDatabase('redplacts-estudio-v2'); }catch(e){}
                            try{ indexedDB.deleteDatabase('redplacts-estudio'); }catch(e){}
                        }
                    }catch(e){}
                    try{ localStorage.clear(); }catch(e){}
                    try{ sessionStorage.clear(); }catch(e){}
                    cb(true);
                })();
                """
            )
        except Exception:
            pass
        driver.get(BASE_URL)
        WebDriverWait(driver, TIMEOUT).until(
            lambda d: d.execute_script("return !!(window.PLACTSStudio && window.PLACTSStudio.whenReady)"),
            message="window.PLACTSStudio.whenReady no disponible tras recarga",
        )
        driver.execute_async_script(
            """
            const cb = arguments[arguments.length-1];
            window.PLACTSStudio.whenReady().then(()=>cb(true)).catch(e=>cb('error:'+e));
            """
        )
        assert driver.execute_script("return !!(window.PLACTSStudio)"), "window.PLACTSStudio no existe tras whenReady"
        assert_no_severe_logs(driver)
        print("✓ ready: storage limpio y PLACTSStudio.whenReady resuelto")

        # 2) completar title/date/time/timezone y disparar input
        # usar JS para setear valores independientemente del panel visible, luego disparar eventos
        title_val = "Evento E2E prueba visual"
        date_val = "2026-09-28"
        time_val = "19:00"
        tz_val = "Argentina · UTC−3"
        driver.execute_script(
            """
            const title = arguments[0], date = arguments[1], timeV = arguments[2], tz = arguments[3];
            const set = (sel, val) => {
              const el = document.querySelector(sel);
              if (!el) return false;
              el.focus();
              el.value = val;
              el.dispatchEvent(new Event('input', {bubbles:true}));
              el.dispatchEvent(new Event('change', {bubbles:true}));
              return true;
            };
            set('#event-title', title);
            set('#event-date', date);
            set('#event-time', timeV);
            set('#event-timezone', tz);
            """,
            title_val, date_val, time_val, tz_val
        )
        # verificar que state refleje los cambios (espera breve)
        wait_js(driver, f"window.PLACTSStudio.getState().event.title===`{title_val}`", timeout=10, msg="title no se reflejó en state")
        wait_js(driver, f"window.PLACTSStudio.getState().event.date===`{date_val}`", msg="date no reflejada")
        wait_js(driver, f"window.PLACTSStudio.getState().event.time===`{time_val}`", msg="time no reflejada")
        wait_js(driver, f"window.PLACTSStudio.getState().event.timezone===`{tz_val}`", msg="timezone no reflejada")
        print(f"✓ formulario base completado: title='{title_val}' date={date_val} time={time_val} tz={tz_val}")

        # 3) click Generar (compile)
        compile_btn = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "compile-button")))
        real_click(driver, compile_btn)
        # esperar a que compile haya rendereado (poster-grid con canvas)
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.querySelector('.poster-card canvas') && document.querySelector('.poster-card canvas').width>0"),
            message="timeout esperando canvas tras Generar"
        )
        # asegurar que no hay errores de validación bloqueantes (pero puede haber warnings)
        time.sleep(0.6)  # pequeño respiro para render estable
        print("✓ Generar click: canvas inicial disponible")

        # 4) seleccionar colección social variante Estado (data-collection social, variant 3)
        # colección social
        try:
            col_social = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-collection="social"]')))
            # si ya está pressed true, igual click asegura estado
            real_click(driver, col_social)
            WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return document.querySelector('[data-collection=\"social\"]').getAttribute('aria-pressed')==='true'"))
        except Exception as e:
            raise AssertionError(f"no se pudo seleccionar colección social: {e}") from e
        print("✓ colección social seleccionada")

        # variante Estado = 3
        try:
            var_estado = WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-variant-select="3"]')))
            # esperar que sea visible (no hidden)
            WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return !document.querySelector('[data-variant-select=\"3\"]').hidden"))
            real_click(driver, var_estado)
            WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return document.querySelector('.poster-card.is-selected')?.dataset.card==='3'"))
            WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return document.querySelector('[data-variant-select=\"3\"][aria-pressed=\"true\"]')!==null"))
        except Exception as e:
            raise AssertionError(f"no se pudo seleccionar variante Estado (3): {e}") from e
        # esperar canvas visible válido
        WebDriverWait(driver, TIMEOUT).until(
            lambda d: d.execute_script(
                "const c=document.querySelector('.poster-card.is-selected canvas'); return !!(c && c.width>0 && c.height>0 && c.getBoundingClientRect().width>0);"
            ),
            message="canvas visible válido no apareció tras seleccionar Estado",
        )
        # además verificar que el plan sea válido (no unavailable)
        wait_js(driver, "window.PLACTSStudio.getPlans()[3] && window.PLACTSStudio.getPlans()[3].valid===true", msg="plan Estado no válido tras Generar (revisar datos)")
        print("✓ variante Estado (3) seleccionada, canvas visible válido")

        # crear /tmp/ui-e2e y screenshot 01-base
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        fp_base = canvas_fingerprint(driver)
        print(f"fingerprint 01-base: hash={fp_base['hash']} {fp_base['width']}x{fp_base['height']} bytes={fp_base['bytes']} step={fp_base['step']}")
        base_path = SCREENSHOT_DIR / "01-base.png"
        driver.save_screenshot(str(base_path))
        assert base_path.exists() and base_path.stat().st_size > 0, f"screenshot 01-base no creado en {base_path}"
        print(f"✓ screenshot 01-base guardado en {base_path}")

        # 5) crear PNGs sólidos distintos 2400x1600: foto azul, fondo rojo, hero verde
        tmp_photo = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
        tmp_bg = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
        tmp_hero = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
        tmp_files.extend([tmp_photo, tmp_bg, tmp_hero])
        _write_solid_png(tmp_photo, 2400, 1600, rgb=(40, 80, 220))   # azul
        _write_solid_png(tmp_bg, 2400, 1600, rgb=(220, 40, 40))     # rojo
        _write_solid_png(tmp_hero, 2400, 1600, rgb=(40, 180, 80))   # verde
        for p in [tmp_photo, tmp_bg, tmp_hero]:
            assert os.path.exists(p) and os.path.getsize(p) > 0, f"PNG sólido no creado: {p}"
        print(f"✓ PNGs sólidos 2400x1600 creados: foto azúl={tmp_photo} bg rojo={tmp_bg} hero verde={tmp_hero}")

        # helper para asegurar input visible antes de send_keys (si panel hidden, abrir tab correspondiente)
        def _ensure_photo_input_visible():
            # intentar localizar input; si no displayed, abrir tab Participantes
            try:
                inp = driver.find_element(By.CSS_SELECTOR, "input[data-photo]")
                if inp.is_displayed():
                    return inp
            except Exception:
                pass
            try:
                tab_people = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "tab-people")))
                real_click(driver, tab_people)
                WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "panel-people").is_displayed())
            except Exception:
                pass
            # re-locar después de abrir tab
            inputs = driver.find_elements(By.CSS_SELECTOR, "#speakers-list input[data-photo]")
            if inputs:
                return inputs[0]
            return WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-photo]")))

        def _ensure_image_input_visible(kind):  # kind background|hero
            sel = f"#image-{kind}"
            try:
                inp = driver.find_element(By.CSS_SELECTOR, sel)
                if inp.is_displayed() or driver.execute_script("return document.getElementById(arguments[0])!==null", f"image-{kind}"):
                    # check panel visibility
                    panel = driver.find_element(By.ID, "panel-images")
                    if panel.is_displayed():
                        return inp
            except Exception:
                pass
            try:
                tab_images = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "tab-images")))
                real_click(driver, tab_images)
                WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "panel-images").is_displayed())
            except Exception:
                pass
            return WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))

        def _return_to_social_estado():
            # volver a seleccionar social + estado para fingerprint
            try:
                col = driver.find_element(By.CSS_SELECTOR, '[data-collection="social"]')
                if col.get_attribute("aria-pressed") != "true":
                    real_click(driver, col)
                    WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return document.querySelector('[data-collection=\"social\"]').getAttribute('aria-pressed')==='true'"))
                var = driver.find_element(By.CSS_SELECTOR, '[data-variant-select="3"]')
                if var.get_attribute("aria-pressed") != "true":
                    real_click(driver, var)
                    WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return document.querySelector('.poster-card.is-selected')?.dataset.card==='3'"))
                WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return document.querySelector('.poster-card.is-selected canvas') && document.querySelector('.poster-card.is-selected canvas').width>0"))
            except Exception as e:
                print(f"warn: no se pudo volver a social/Estado: {e}", file=sys.stderr)

        # 6) Upload foto primer speaker; esperar photo state, socialPhotos true, render actualizado y fingerprint distinto; screenshot 02-photo
        photo_input = _ensure_photo_input_visible()
        person_id = photo_input.get_attribute("data-photo")
        assert person_id, "no se encontró data-photo en primer input de participante"
        t_photo_start = time.time()
        photo_input.send_keys(os.path.abspath(tmp_photo))
        # esperar state photo.data
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script(
                "const id=arguments[0]; const s=window.PLACTSStudio.getState(); const p=(s.speakers.find(x=>x.id===id)||s.moderators.find(x=>x.id===id)); return !!(p && p.photo && p.photo.data);",
                person_id,
            ),
            message=f"timeout esperando photo.data para speaker {person_id} tras upload foto azul",
        )
        # esperar socialPhotos true (se activa al subir foto per uploadImage)
        wait_js(driver, "window.PLACTSStudio.getState().options.socialPhotos===true", timeout=15, msg="socialPhotos no pasó a true tras upload foto")
        _return_to_social_estado()
        # esperar fingerprint distinto
        fp_photo, dur_photo = _wait_fingerprint_change(driver, fp_base["hash"], timeout=30, label="02-photo")
        # validar que photo.state sea azul? solo chequear data URL presente y dimensiones redimensionadas <=1100
        st = driver.execute_script("return window.PLACTSStudio.getState()")
        person = next((p for p in (st["speakers"] + st["moderators"]) if p["id"] == person_id), None)
        assert person and person.get("photo"), f"speaker {person_id} sin photo tras upload"
        assert person["photo"].get("data","").startswith("data:image"), "photo.data no es data URL"
        w = person["photo"].get("width"); h = person["photo"].get("height")
        assert w and h and max(w,h) <= 1100, f"foto no redimensionada correctamente: {w}x{h}"
        print(f"✓ upload foto speaker {person_id} ok: {w}x{h} socialPhotos=true dur={time.time()-t_photo_start:.2f}s fp {fp_base['hash']} -> {fp_photo['hash']}")
        shot2 = SCREENSHOT_DIR / "02-photo.png"
        driver.save_screenshot(str(shot2))
        assert shot2.exists() and shot2.stat().st_size>0
        print(f"✓ screenshot 02-photo en {shot2}")

        # 7) Upload background, esperar state/bgOpacity>=28 y fingerprint distinto; screenshot 03-background
        bg_input = _ensure_image_input_visible("background")
        t_bg_start = time.time()
        bg_input.send_keys(os.path.abspath(tmp_bg))
        wait_js(driver, "!!window.PLACTSStudio.getState().images.background", timeout=15, msg="state.images.background sigue null tras upload rojo")
        wait_js(driver, "!!window.PLACTSStudio.getState().images.background.data", timeout=15, msg="background.data vacío")
        # bgOpacity >=28 (uploadImage fuerza 32 si <28)
        wait_js(driver, "window.PLACTSStudio.getState().options.bgOpacity>=28", timeout=10, msg="bgOpacity no subió a >=28 tras background")
        st_bg = driver.execute_script("return window.PLACTSStudio.getState()")
        assert st_bg["images"]["background"]["data"].startswith("data:image"), "background.data no es data URL"
        print(f"✓ upload background rojo ok: bgOpacity={st_bg['options']['bgOpacity']}")
        _return_to_social_estado()
        fp_bg, dur_bg = _wait_fingerprint_change(driver, fp_photo["hash"], timeout=30, label="03-background")
        # asegurar distinto de base también
        assert fp_bg["hash"] != fp_base["hash"], f"fingerprint background debe diferir de base: {fp_bg['hash']} == {fp_base['hash']}"
        shot3 = SCREENSHOT_DIR / "03-background.png"
        driver.save_screenshot(str(shot3))
        assert shot3.exists() and shot3.stat().st_size>0
        print(f"✓ screenshot 03-background en {shot3} dur={time.time()-t_bg_start:.2f}s fp {fp_photo['hash']} -> {fp_bg['hash']}")

        # 8) Upload hero, esperar state y fingerprint distinto; screenshot 04-hero
        hero_input = _ensure_image_input_visible("hero")
        t_hero_start = time.time()
        hero_input.send_keys(os.path.abspath(tmp_hero))
        wait_js(driver, "!!window.PLACTSStudio.getState().images.hero", timeout=15, msg="state.images.hero sigue null tras upload verde")
        wait_js(driver, "!!window.PLACTSStudio.getState().images.hero.data", timeout=15, msg="hero.data vacío")
        st_hero = driver.execute_script("return window.PLACTSStudio.getState()")
        assert st_hero["images"]["hero"]["data"].startswith("data:image"), "hero.data no es data URL"
        print(f"✓ upload hero verde ok: {st_hero['images']['hero']['width']}x{st_hero['images']['hero']['height']}")
        _return_to_social_estado()
        fp_hero, dur_hero = _wait_fingerprint_change(driver, fp_bg["hash"], timeout=30, label="04-hero")
        assert fp_hero['hash'] not in (fp_base['hash'], fp_photo['hash'], fp_bg['hash']), f"fingerprint hero debe ser único, got {fp_hero['hash']} repetido"
        shot4 = SCREENSHOT_DIR / "04-hero.png"
        driver.save_screenshot(str(shot4))
        assert shot4.exists() and shot4.stat().st_size>0
        print(f"✓ screenshot 04-hero en {shot4} dur={time.time()-t_hero_start:.2f}s fp {fp_bg['hash']} -> {fp_hero['hash']}")

        # 9) Verificar CTA Reemplazar y consola sin SEVERE
        # volver a panel imágenes para verificar CTAs visibles (aunque pueden estar en DOM hidden, forzar navegación)
        try:
            tab_images_final = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "tab-images")))
            real_click(driver, tab_images_final)
            WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "panel-images").is_displayed())
        except Exception:
            pass
        # CTA background
        bg_cta = WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#asset-background .upload-copy .btn")))
        bg_text = bg_cta.text.strip()
        assert bg_text == "Reemplazar imagen de fondo", f"CTA background esperado 'Reemplazar imagen de fondo', got '{bg_text}'"
        print(f"✓ CTA background verificado: '{bg_text}'")
        # CTA hero (puede estar en asset-hero .upload-copy .btn)
        hero_cta = WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#asset-hero .upload-copy .btn")))
        hero_text = hero_cta.text.strip()
        assert hero_text == "Reemplazar imagen principal", f"CTA hero esperado 'Reemplazar imagen principal', got '{hero_text}'"
        print(f"✓ CTA hero verificado: '{hero_text}'")

        assert_no_severe_logs(driver)
        print("✓ consola sin SEVERE")

        total = time.time() - start_all
        print("\n=== IMAGE CANVAS E2E OK ===")
        print(f"fingerprints: base={fp_base['hash']} photo={fp_photo['hash']} bg={fp_bg['hash']} hero={fp_hero['hash']}")
        print(f"dimensiones: base={fp_base['width']}x{fp_base['height']} photo={fp_photo['width']}x{fp_photo['height']} bg={fp_bg['width']}x{fp_bg['height']} hero={fp_hero['width']}x{fp_hero['height']}")
        print(f"duraciones: photo={dur_photo:.2f}s bg={dur_bg:.2f}s hero={dur_hero:.2f}s total={total:.2f}s")
        print(f"screenshots conservados en {SCREENSHOT_DIR}: 01-base.png 02-photo.png 03-background.png 04-hero.png")
        # verificar que los 4 screenshots existen
        for name in ["01-base.png","02-photo.png","03-background.png","04-hero.png"]:
            p = SCREENSHOT_DIR / name
            assert p.exists(), f"screenshot esperado no existe: {p}"
        print("E2E visual: las tres clases de imagen modifican el canvas (fingerprints distintos)")

    except Exception as e:
        print("\n--- IMAGE CANVAS E2E FAILURE ---", file=sys.stderr)
        traceback.print_exc()
        # intentar guardar screenshot de fallo sin borrar los previos
        try:
            if driver:
                fail_path = SCREENSHOT_DIR / "failure.png"
                SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
                driver.save_screenshot(str(fail_path))
                print(f"screenshot fallo guardado en {fail_path}", file=sys.stderr)
                # page source
                try:
                    with open(SCREENSHOT_DIR / "failure.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                except Exception:
                    pass
        except Exception as se:
            print(f"no se pudo guardar screenshot de fallo: {se}", file=sys.stderr)
        raise AssertionError(f"image_canvas_e2e fallo: {e}") from e
    finally:
        # cleanup PNG temporales, conservar screenshots
        for _p in tmp_files:
            if _p and os.path.exists(_p):
                try:
                    os.unlink(_p)
                except Exception:
                    pass
        try:
            if driver:
                driver.quit()
        except Exception:
            pass


def test_image_canvas_e2e():
    """Entry para pytest."""
    run()


if __name__ == "__main__":
    run()
