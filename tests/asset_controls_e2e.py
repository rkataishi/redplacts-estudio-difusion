#!/usr/bin/env python3
"""
E2E solo controles de imagenes globales.
- Usa helpers de ui_smoke (_driver, real_click, wait_js, _write_solid_png, assert_no_severe_logs, BASE_URL, get_state)
- Fresh valid (clear storage + reload + whenReady) sin delegar arquitectura
- Panel images; upload background/hero PNG, replace background different y assert data cambia
- Crop x/y/zoom para cada (background/hero) y verifica outputs y state
- bgOpacity set 55 verifica output y state
- Remove bg/hero y verifica CTA Cargar
- Drag/drop hero via DataTransfer/File JS
- Keyboard Space/Enter trigger con contador click sin dialogo nativo
- Screenshot /tmp/ui-e2e/21-assets.png y console sin SEVERE; py_compile ok
"""
import base64
import os
import sys
import time
import traceback
import tempfile
import py_compile
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    from tests.ui_smoke import _driver, real_click, wait_js, _write_solid_png, assert_no_severe_logs, BASE_URL, get_state
except ImportError:
    try:
        from ui_smoke import _driver, real_click, wait_js, _write_solid_png, assert_no_severe_logs, BASE_URL, get_state  # type: ignore
    except ImportError:
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
            WebDriverWait(driver, timeout).until(lambda d: d.execute_script(f"return !!({js_predicate})"), message=msg or f"timeout {js_predicate}")

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
            assert not severe, f"Console SEVERE detectado: {severe}"

        def get_state(driver):
            return driver.execute_script("return window.PLACTSStudio.getState()")

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
SCREENSHOT = Path("/tmp/ui-e2e/21-assets.png")


def wait_state(driver, js_pred, msg="", timeout=TIMEOUT):
    wait_js(driver, js_pred, timeout=timeout, msg=msg)


def js_set_slider(driver, selector, value):
    driver.execute_script(
        """
        const sel = arguments[0], val = arguments[1];
        const el = document.querySelector(sel);
        if (!el) throw new Error('slider no encontrado: '+sel);
        el.value = String(val);
        el.dispatchEvent(new Event('input', {bubbles:true}));
        el.dispatchEvent(new Event('change', {bubbles:true}));
        """,
        selector, value,
    )


def run():
    driver = None
    tmp_files = []
    start_all = time.time()
    try:
        driver = _driver()

        # Fresh valid igual que ui_smoke / image_canvas_e2e
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
        print("✓ fresh state ready: storage limpio + whenReady")

        # Completar minimo valido para Generar: title/date/time/timezone
        driver.execute_script(
            """
            const set = (sel,val)=>{
              const el=document.querySelector(sel); if(!el) return false;
              el.focus(); el.value=val;
              el.dispatchEvent(new Event('input',{bubbles:true}));
              el.dispatchEvent(new Event('change',{bubbles:true}));
              return true;
            };
            set('#event-title','Evento E2E Assets 21');
            set('#event-date','2026-09-28');
            set('#event-time','19:00');
            set('#event-timezone','Argentina · UTC−3');
            """
        )
        wait_js(driver, "window.PLACTSStudio.getState().event.title==='Evento E2E Assets 21'", msg="title no reflejado")
        wait_js(driver, "window.PLACTSStudio.getState().event.date==='2026-09-28'", msg="date no reflejada")
        wait_js(driver, "window.PLACTSStudio.getState().event.time==='19:00'", msg="time no reflejado")
        # Generar
        compile_btn = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "compile-button")))
        real_click(driver, compile_btn)
        WebDriverWait(driver, 15).until(lambda d: d.execute_script("return document.querySelector('.poster-card canvas') && document.querySelector('.poster-card canvas').width>0"), message="canvas tras Generar no aparecio")
        print("✓ fresh valid Generar ok: canvas visible")

        # Panel images
        tab_images = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "tab-images")))
        real_click(driver, tab_images)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "panel-images").is_displayed())
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-images").get_attribute("aria-selected")=="true")
        print("✓ panel images visible")

        # Helper para esperar state image no null
        def wait_image(kind, should_exist=True, timeout=15):
            if should_exist:
                wait_js(driver, f"!!window.PLACTSStudio.getState().images.{kind}", timeout=timeout, msg=f"images.{kind} no existe tras operacion")
                wait_js(driver, f"!!window.PLACTSStudio.getState().images.{kind}.data", timeout=timeout, msg=f"images.{kind}.data vacio")
            else:
                wait_js(driver, f"!window.PLACTSStudio.getState().images.{kind}", timeout=timeout, msg=f"images.{kind} deberia ser null")

        # Crear PNGs temporales para background y hero
        tmp_bg1 = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
        tmp_bg2 = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
        tmp_hero = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
        tmp_files.extend([tmp_bg1, tmp_bg2, tmp_hero])
        _write_solid_png(tmp_bg1, 800, 600, rgb=(220, 40, 40))  # rojo
        _write_solid_png(tmp_bg2, 800, 600, rgb=(40, 40, 220))  # azul distinto
        _write_solid_png(tmp_hero, 800, 600, rgb=(40, 180, 80))  # verde
        for p in [tmp_bg1, tmp_bg2, tmp_hero]:
            assert os.path.exists(p) and os.path.getsize(p) > 0

        # Upload background PNG (rojo)
        bg_input = WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.ID, "image-background")))
        bg_input.send_keys(os.path.abspath(tmp_bg1))
        wait_image("background", True, 15)
        st = get_state(driver)
        bg_data1 = st["images"]["background"]["data"]
        assert bg_data1.startswith("data:image"), "background data no es data URL"
        bg_cta = WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#asset-background .upload-copy .btn")))
        assert bg_cta.text.strip() == "Reemplazar imagen de fondo", f"CTA bg esperado Reemplazar, got '{bg_cta.text}'"
        print(f"✓ upload background ok data len {len(bg_data1)} CTA Reemplazar")

        # Upload hero PNG (verde)
        hero_input = WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.ID, "image-hero")))
        hero_input.send_keys(os.path.abspath(tmp_hero))
        wait_image("hero", True, 15)
        st = get_state(driver)
        hero_data1 = st["images"]["hero"]["data"]
        assert hero_data1.startswith("data:image"), "hero data no es data URL"
        hero_cta = WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#asset-hero .upload-copy .btn")))
        assert hero_cta.text.strip() == "Reemplazar imagen principal", f"CTA hero esperado Reemplazar, got '{hero_cta.text}'"
        print(f"✓ upload hero ok data len {len(hero_data1)} CTA Reemplazar")

        # Replace background different (azul) y assert data cambia
        bg_input2 = driver.find_element(By.ID, "image-background")
        bg_input2.send_keys(os.path.abspath(tmp_bg2))
        # esperar data distinta
        WebDriverWait(driver, 15).until(lambda d: d.execute_script("return window.PLACTSStudio.getState().images.background.data") != bg_data1, message="background data no cambio tras replace")
        st2 = get_state(driver)
        bg_data2 = st2["images"]["background"]["data"]
        assert bg_data2 != bg_data1, "background data deberia cambiar tras replace con imagen distinta"
        assert bg_data2.startswith("data:image")
        print(f"✓ replace background different ok: data cambia {len(bg_data1)} -> {len(bg_data2)} (distinto)")

        # Crop x/y/zoom para cada (background y hero) y outputs/state
        # background
        for kind in ["background", "hero"]:
            # verificar que crop controls existen
            for axis, test_val, expected_state, output_sel in [
                ("x", 22, 22, f"#crop-{kind}-x + output"),
                ("y", 83, 83, f"#crop-{kind}-y + output"),
                ("zoom", 150, 1.5, f"#crop-{kind}-zoom + output"),
            ]:
                slider_sel = f"#crop-{kind}-{axis}"
                # asegurar existe
                el = WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, slider_sel)))
                # para zoom el output muestra porcentaje entero (150), state es 1.5
                js_set_slider(driver, slider_sel, test_val)
                if axis == "zoom":
                    wait_js(driver, f"window.PLACTSStudio.getState().images.{kind}.crop.zoom===1.5", msg=f"{kind} zoom state no 1.5")
                    out = driver.find_element(By.CSS_SELECTOR, output_sel).text_content if hasattr(driver.find_element(By.CSS_SELECTOR, output_sel), 'text_content') else driver.find_element(By.CSS_SELECTOR, output_sel).text
                    # robust: use execute_script for output text
                    out_text = driver.execute_script("return document.querySelector(arguments[0]).textContent", output_sel)
                    assert out_text.strip() == "150", f"{kind} zoom output esperado 150 got '{out_text}'"
                    assert abs(get_state(driver)["images"][kind]["crop"]["zoom"] - 1.5) < 0.001
                else:
                    wait_js(driver, f"window.PLACTSStudio.getState().images.{kind}.crop.{axis}==={test_val}", msg=f"{kind} crop {axis} no {test_val}")
                    out_text = driver.execute_script("return document.querySelector(arguments[0]).textContent", output_sel)
                    assert out_text.strip() == str(test_val), f"{kind} crop {axis} output esperado {test_val} got '{out_text}'"
                    assert get_state(driver)["images"][kind]["crop"][axis] == test_val
                print(f"✓ crop {kind} {axis}={test_val} output/state ok")
            # reset a valores medios para no afectar drag/drop (opcional)
        # bgOpacity set 55 output/state
        bg_opacity_sel = "#bg-opacity"
        bg_opacity_input = WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, bg_opacity_sel)))
        js_set_slider(driver, bg_opacity_sel, 55)
        wait_js(driver, "window.PLACTSStudio.getState().options.bgOpacity===55", msg="bgOpacity state no 55")
        op_out = driver.execute_script("return document.querySelector('#bg-opacity + output').textContent")
        assert op_out.strip() == "55%", f"bgOpacity output esperado 55% got '{op_out}'"
        assert get_state(driver)["options"]["bgOpacity"] == 55
        print("✓ bgOpacity set 55 output/state ok")

        # Remove bg/hero y CTA Cargar
        # quitar background
        rm_bg = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-remove-image="background"]')))
        real_click(driver, rm_bg)
        wait_image("background", False)
        # CTA debe ser Cargar imagen de fondo
        bg_cta_after = WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#asset-background .upload-copy .btn")))
        assert bg_cta_after.text.strip() == "Cargar imagen de fondo", f"tras quitar bg CTA esperado Cargar, got '{bg_cta_after.text}'"
        assert get_state(driver)["images"]["background"] is None
        print("✓ remove background ok CTA Cargar")

        # quitar hero
        rm_hero = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-remove-image="hero"]')))
        real_click(driver, rm_hero)
        wait_image("hero", False)
        hero_cta_after = WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#asset-hero .upload-copy .btn")))
        assert hero_cta_after.text.strip() == "Cargar imagen principal", f"tras quitar hero CTA esperado Cargar, got '{hero_cta_after.text}'"
        assert get_state(driver)["images"]["hero"] is None
        print("✓ remove hero ok CTA Cargar")

        # Drag/drop hero via DataTransfer/File JS
        tmp_drag = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
        tmp_files.append(tmp_drag)
        _write_solid_png(tmp_drag, 700, 500, rgb=(180, 40, 220))  # morado distinto
        with open(tmp_drag, "rb") as f:
            b64_drag = base64.b64encode(f.read()).decode("ascii")
        # ejecutar drop JS
        driver.execute_script(
            """
            const b64 = arguments[0];
            const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
            const file = new File([bytes], "hero-drag.png", {type:"image/png"});
            const dt = new DataTransfer();
            dt.items.add(file);
            const zone = document.querySelector('#asset-hero [data-drop="hero"]');
            if (!zone) throw new Error('drop zone hero no encontrado');
            zone.dispatchEvent(new DragEvent('dragover', {bubbles:true, cancelable:true, dataTransfer: dt}));
            zone.dispatchEvent(new DragEvent('drop', {bubbles:true, cancelable:true, dataTransfer: dt}));
            """,
            b64_drag,
        )
        wait_image("hero", True, 20)
        st_drag = get_state(driver)
        assert st_drag["images"]["hero"]["data"].startswith("data:image")
        hero_cta_drag = WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#asset-hero .upload-copy .btn")))
        assert hero_cta_drag.text.strip() == "Reemplazar imagen principal"
        print(f"✓ drag/drop hero via DataTransfer/File JS ok data len {len(st_drag['images']['hero']['data'])}")

        # Keyboard Space/Enter trigger con click counter sin dialogo nativo
        # instalar contador interceptando input.click
        driver.execute_script(
            """
            window.__heroClickCount = 0;
            const input = document.getElementById('image-hero');
            if (!input) throw new Error('input hero no encontrado');
            // preservar original por si se necesita pero no llamar
            input.__origClick = input.click.bind(input);
            input.click = function(){ window.__heroClickCount = (window.__heroClickCount||0)+1; };
            // asegurar trigger es focusable
            const trigger = document.querySelector('#asset-hero [data-drop="hero"]');
            if (!trigger) throw new Error('trigger hero no encontrado');
            trigger.setAttribute('tabindex','0');
            """
        )
        trigger_el = WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#asset-hero [data-drop="hero"]')))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", trigger_el)
        time.sleep(0.2)
        trigger_el.click()  # foco
        driver.execute_script("arguments[0].focus();", trigger_el)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return document.activeElement === document.querySelector('#asset-hero [data-drop=\"hero\"]')"))
        # Space
        trigger_el.send_keys(Keys.SPACE)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return window.__heroClickCount===1"), message="contador click tras Space no 1")
        assert driver.execute_script("return window.__heroClickCount") == 1
        print("✓ keyboard Space trigger input.click contador 1")
        # Enter
        trigger_el.send_keys(Keys.ENTER)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return window.__heroClickCount===2"), message="contador click tras Enter no 2")
        assert driver.execute_script("return window.__heroClickCount") == 2
        print("✓ keyboard Enter trigger input.click contador 2 (sin dialogo nativo)")

        # Screenshot /tmp/ui-e2e/21-assets.png
        SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(SCREENSHOT))
        assert SCREENSHOT.exists() and SCREENSHOT.stat().st_size > 0, f"screenshot no creado en {SCREENSHOT}"
        print(f"✓ screenshot guardado en {SCREENSHOT} ({SCREENSHOT.stat().st_size} bytes)")

        # Console sin SEVERE
        assert_no_severe_logs(driver)
        print("✓ consola sin SEVERE")

        total = time.time() - start_all
        print(f"\n=== ASSET CONTROLS E2E OK === total {total:.2f}s")
        # py_compile check interno
        py_compile.compile(str(Path(__file__)), doraise=True)
        print(f"✓ py_compile ok {Path(__file__).name}")

    except Exception as e:
        print("\n--- ASSET CONTROLS E2E FAILURE ---", file=sys.stderr)
        traceback.print_exc()
        try:
            if driver:
                SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
                fail_path = SCREENSHOT.parent / "failure-21-assets.png"
                driver.save_screenshot(str(fail_path))
                print(f"screenshot fallo en {fail_path}", file=sys.stderr)
                try:
                    with open(SCREENSHOT.parent / "failure-21-assets.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                except Exception:
                    pass
        except Exception as se:
            print(f"no se pudo guardar screenshot fallo: {se}", file=sys.stderr)
        raise AssertionError(f"asset_controls_e2e fallo: {e}") from e
    finally:
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


def test_asset_controls_e2e():
    """Entry para pytest."""
    run()


if __name__ == "__main__":
    run()
