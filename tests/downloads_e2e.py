#!/usr/bin/env python3
"""
E2E: botones de descarga / exportación.
- Fresh proyecto válido → Generar canvas
- save-project JSON (click y Ctrl/Cmd+S)
- individual PNG (data-export button) × 9
- zoom-download PNG (dialog)
- export-all ZIP único (9 PNG + JSON + LEEME + texto-para-acompanar)
- caption download TXT
- Screenshot 32-downloads.png
- py_compile
"""
import os
import sys
import time
import glob
import zipfile
import traceback
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    from tests.ui_smoke import (
        _driver, real_click, wait_js, _write_solid_png,
        assert_no_severe_logs, BASE_URL, get_state,
    )
except ImportError:
    try:
        from ui_smoke import (  # type: ignore
            _driver, real_click, wait_js, _write_solid_png,
            assert_no_severe_logs, BASE_URL, get_state,
        )
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
                opts.add_experimental_option("prefs", {"profile": {"default_content_setting_values": {"automatic_downloads": 1}}})
            except Exception:
                pass
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
                message=msg or f"timeout {js_predicate}",
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

import py_compile

TIMEOUT = 15
SCREENSHOT = Path("/tmp/ui-e2e/32-downloads.png")
DOWNLOAD_DIR = Path("/tmp/ui-e2e/downloads-dl")


def _pre_files(pattern):
    return set(glob.glob(str(DOWNLOAD_DIR / pattern)))


def _post_files(pattern, before):
    after = set(glob.glob(str(DOWNLOAD_DIR / pattern)))
    return after - before


def _wait_new_file(pattern, before, label, timeout=8, min_size=100):
    """Poll for new file matching pattern until timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        new = _post_files(pattern, before)
        if new:
            p = new.pop()
            sz = os.path.getsize(p)
            assert sz > min_size, f"{label}: archivo demasiado pequeño ({sz} bytes)"
            return p, sz
        time.sleep(0.5)
    raise AssertionError(f"{label}: no apareció archivo nuevo ({pattern}) en {timeout}s")


def run():
    driver = None
    start_all = time.time()
    try:
        driver = _driver()
        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

        # Chrome download prefs
        driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": str(DOWNLOAD_DIR),
        })

        # --- fresh state ---
        driver.get(BASE_URL)
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState === 'complete'")
        )
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
            message="PLACTSStudio.whenReady no disponible",
        )
        driver.execute_async_script(
            """
            const cb = arguments[arguments.length-1];
            window.PLACTSStudio.whenReady().then(()=>cb(true)).catch(e=>cb('error:'+e));
            """
        )
        assert driver.execute_script("return !!(window.PLACTSStudio)"), "PLACTSStudio no existe"
        assert_no_severe_logs(driver)
        print("✓ fresh state ready")

        # --- fill all required fields ---
        driver.execute_script(
            """
            const set=(sel,val)=>{
              const el=document.querySelector(sel); if(!el) return;
              el.focus(); el.value=val;
              el.dispatchEvent(new Event('input',{bubbles:true}));
              el.dispatchEvent(new Event('change',{bubbles:true}));
            };
            set('#event-title','E2E Downloads');
            set('#event-date','2026-10-05');
            set('#event-time','18:00');
            set('#event-timezone','Argentina · UTC−3');
            """
        )
        wait_state = lambda js, msg="": wait_js(driver, js, timeout=TIMEOUT, msg=msg)
        wait_state("window.PLACTSStudio.getState().event.title==='E2E Downloads'")
        print("✓ fields filled")

        # --- expositor requerido (mínimo 1) ---
        driver.execute_script(
            """
            const state = window.PLACTSStudio.getState();
            const firstId = state.speakers[0].id;
            let el = document.getElementById('name-' + firstId);
            if (!el) el = document.querySelector('[data-person=\"' + firstId + '\"] [data-person-field=\"name\"]');
            if (!el) throw new Error('input expositor no encontrado: name-' + firstId);
            el.focus();
            el.value = 'Expositor E2E';
            el.dispatchEvent(new Event('input', {bubbles: true}));
            el.dispatchEvent(new Event('change', {bubbles: true}));
            """
        )
        wait_state("window.PLACTSStudio.getState().speakers[0].name==='Expositor E2E'", msg="expositor E2E no reflejado en state")
        print("✓ expositor E2E seteado")

        # validación sin errores antes de Generar
        wait_state("window.PLACTSStudio.validationErrors(window.PLACTSStudio.getState()).length===0", msg="validationErrors no es 0 antes de Generar")
        _err_len = driver.execute_script("return window.PLACTSStudio.validationErrors(window.PLACTSStudio.getState()).length")
        assert _err_len == 0, f"validationErrors antes de Generar: esperado 0, got {_err_len}"
        print("✓ validationErrors 0 antes de Generar")

        # --- Generar ---
        compile_btn = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "compile-button"))
        )
        real_click(driver, compile_btn)
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script(
                "return document.querySelector('.poster-card canvas') && document.querySelector('.poster-card canvas').width>0"
            ),
            message="canvas no apareció tras Generar",
        )
        print("✓ Generar → canvas visible")

        # ============================================================
        # 1. SAVE-PROJECT JSON (click)
        # ============================================================
        before_json = _pre_files("*.json")
        save_btn = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "save-project"))
        )
        real_click(driver, save_btn)
        json_path, json_sz = _wait_new_file("*.json", before_json, "save-project click", min_size=50)
        assert json_path.lower().endswith(".json"), f"save-project: extensión no es .json: {json_path}"
        print(f"✓ save-project (click) ok: {Path(json_path).name} ({json_sz} bytes)")
        # robustez mismo nombre: eliminar primer JSON y esperar que Ctrl/Cmd+S lo recree
        expected_json_name = Path(json_path).name
        expected_json_path = DOWNLOAD_DIR / expected_json_name
        try:
            os.remove(json_path)
        except FileNotFoundError:
            pass
        except Exception:
            pass
        _t0 = time.time()
        while expected_json_path.exists() and time.time() - _t0 < 2:
            time.sleep(0.1)
            try:
                os.remove(str(expected_json_path))
            except Exception:
                pass

        # ============================================================
        # 2. SAVE-PROJECT JSON (Ctrl/Cmd+S)
        # ============================================================
        before_json2 = _pre_files("*.json")
        # focus body to ensure keydown fires
        driver.execute_script("document.body.focus();")
        time.sleep(0.2)
        body = driver.find_element(By.TAG_NAME, "body")
        # Ctrl+S on macOS = Meta+S
        is_mac = driver.execute_script("return navigator.platform||''").lower().find("mac") >= 0
        mod = Keys.COMMAND if is_mac else Keys.CONTROL
        body.send_keys(mod + "s")
        time.sleep(0.2)
        body.send_keys(Keys.NULL)  # release modifier
        # esperar que reaparezca el mismo archivo (robusto al mismo nombre) + fallback genérico
        deadline = time.time() + 8
        json_path2 = None
        json_sz2 = 0
        while time.time() < deadline:
            if expected_json_path.exists():
                try:
                    sz = expected_json_path.stat().st_size
                except Exception:
                    sz = 0
                if sz > 50:
                    json_path2 = str(expected_json_path)
                    json_sz2 = sz
                    break
            new = _post_files("*.json", before_json2)
            if new:
                for cand in list(new):
                    try:
                        csz = os.path.getsize(cand)
                    except Exception:
                        continue
                    if csz > 50:
                        json_path2 = cand
                        json_sz2 = csz
                        break
                if json_path2:
                    break
            time.sleep(0.5)
        assert json_path2, f"Ctrl/Cmd+S: no reapareció {expected_json_name} ni nuevo JSON en 8s (before={before_json2})"
        assert json_path2.lower().endswith(".json"), f"Ctrl/Cmd+S: extensión no es .json: {json_path2}"
        assert json_sz2 > 50, f"Ctrl/Cmd+S: archivo demasiado pequeño ({json_sz2} bytes): {json_path2}"
        print(f"✓ save-project (Ctrl/Cmd+S) ok: {Path(json_path2).name} ({json_sz2} bytes)")

        # ============================================================
        # 3. INDIVIDUAL PNG × 9 (data-export button per variant)
        # ============================================================
        OUTPUT_DIR = Path("/tmp/ui-e2e")
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        plans = driver.execute_script("return window.PLACTSStudio.getPlans()")
        assert plans and len(plans) >= 9, f"getPlans() devolvió {len(plans) if plans else 0} planes, esperado ≥9"
        print(f"✓ getPlans() → {len(plans)} planes")

        for _i in range(9):
            # select variant
            sel = driver.find_element(By.CSS_SELECTOR, f'[data-variant-select="{_i}"]')
            real_click(driver, sel)
            time.sleep(0.3)

            # save full selected canvas as PNG via dataURL
            canvas_data_url = driver.execute_script(
                "const c=document.querySelector('.poster-card.is-selected canvas'); "
                "return c ? c.toDataURL('image/png') : null;"
            )
            assert canvas_data_url, f"output-{_i}: no se obtuvo canvas dataURL"
            # strip data URL prefix
            import base64 as _b64
            _header, _data = canvas_data_url.split(",", 1)
            _png_bytes = _b64.b64decode(_data)
            _out_path = OUTPUT_DIR / f"output-{_i}.png"
            _out_path.write_bytes(_png_bytes)
            assert _out_path.exists() and _out_path.stat().st_size > 500, \
                f"output-{_i}: archivo demasiado pequeño ({_out_path.stat().st_size} bytes)"
            print(f"✓ output-{_i}.png saved ({_out_path.stat().st_size} bytes)")

            # assert canvas dimensions match getPlans()[i]
            plan = plans[_i]
            _cw = driver.execute_script(
                "const c=document.querySelector('.poster-card.is-selected canvas'); "
                "return c ? c.width : 0;"
            )
            _ch = driver.execute_script(
                "const c=document.querySelector('.poster-card.is-selected canvas'); "
                "return c ? c.height : 0;"
            )
            assert _cw == plan["width"], f"output-{_i}: canvas width {_cw} != plan width {plan['width']}"
            assert _ch == plan["height"], f"output-{_i}: canvas height {_ch} != plan height {plan['height']}"
            print(f"✓ output-{_i}: canvas {_cw}×{_ch} matches plan {plan['width']}×{plan['height']}")

            # click individual data-export and await PNG download
            before_png = _pre_files("*.png")
            export_btn = WebDriverWait(driver, TIMEOUT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".poster-card.is-selected .poster-actions .btn[data-export]"))
            )
            real_click(driver, export_btn)
            png_path, png_sz = _wait_new_file("*.png", before_png, f"individual PNG variant {_i}", timeout=10, min_size=2000)
            assert png_path.lower().endswith(".png"), f"individual PNG variant {_i}: extensión incorrecta: {png_path}"
            print(f"✓ individual PNG variant {_i} ok: {Path(png_path).name} ({png_sz} bytes)")

        # robustez: clean up last downloaded PNG before zoom-download
        expected_png_name = Path(png_path).name
        expected_png_path = DOWNLOAD_DIR / expected_png_name
        try:
            os.remove(png_path)
        except FileNotFoundError:
            pass
        except Exception:
            pass
        _t0 = time.time()
        while expected_png_path.exists() and time.time() - _t0 < 2:
            time.sleep(0.1)
            try:
                os.remove(str(expected_png_path))
            except Exception:
                pass

        # ============================================================
        # 4. ZOOM-DOWNLOAD PNG
        # ============================================================
        # preview único: stage ya en mode-focus o card visible, abrir zoom desde poster frame
        wait_state(
            "document.getElementById('stage').classList.contains('mode-focus') || !!document.querySelector('.poster-card.is-selected') || !!document.querySelector('.poster-card:not([hidden])')",
            msg="stage no en mode-focus ni card visible antes de zoom",
        )
        _stage_mode_focus = driver.execute_script("return document.getElementById('stage').classList.contains('mode-focus')")
        _card_visible = driver.execute_script("return !!document.querySelector('.poster-card.is-selected') || !!document.querySelector('.poster-card:not([hidden])')")
        assert _stage_mode_focus or _card_visible, "preview único: stage sin mode-focus ni card visible antes de zoom"
        poster_frame = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".poster-card.is-selected .poster-frame"))
        )
        real_click(driver, poster_frame)
        WebDriverWait(driver, TIMEOUT).until(
            lambda d: d.execute_script("return document.getElementById('zoom-dialog').open"),
            message="zoom dialog no abrió tras poster frame",
        )
        print("✓ zoom dialog abierto")

        before_png2 = _pre_files("*.png")
        zoom_dl = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "zoom-download"))
        )
        real_click(driver, zoom_dl)
        # esperar que reaparezca el mismo path (robusto al mismo nombre) o nuevo PNG >1000
        deadline = time.time() + 10
        zp = None
        zsz = 0
        while time.time() < deadline:
            if expected_png_path.exists():
                try:
                    sz = expected_png_path.stat().st_size
                except Exception:
                    sz = 0
                if sz > 1000:
                    zp = str(expected_png_path)
                    zsz = sz
                    break
            new = _post_files("*.png", before_png2)
            if new:
                for cand in list(new):
                    try:
                        csz = os.path.getsize(cand)
                    except Exception:
                        continue
                    if csz > 1000:
                        zp = cand
                        zsz = csz
                        break
                if zp:
                    break
            time.sleep(0.5)
        assert zp, f"zoom-download PNG: no reapareció {expected_png_name} ni nuevo PNG >1000 en 10s (before={before_png2})"
        assert zp.lower().endswith(".png"), f"zoom-download PNG: extensión incorrecta: {zp}"
        assert zsz > 1000, f"zoom-download PNG: archivo demasiado pequeño ({zsz} bytes): {zp}"
        print(f"✓ zoom-download PNG ok: {Path(zp).name} ({zsz} bytes)")

        # close zoom — asegurar cerrado
        close_zoom = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-close='zoom-dialog']"))
        )
        real_click(driver, close_zoom)
        WebDriverWait(driver, TIMEOUT).until(
            lambda d: not d.execute_script("return document.getElementById('zoom-dialog').open")
        )
        wait_state("!document.getElementById('zoom-dialog').open", msg="zoom-dialog sigue abierto tras cierre")
        time.sleep(0.2)
        print("✓ zoom cerrado")

        # ============================================================
        # 5. EXPORT-ALL ZIP único
        # ============================================================
        before_zip = _pre_files("*.zip")
        export_all = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "export-all"))
        )
        real_click(driver, export_all)
        zip_path, zip_sz = _wait_new_file("*.zip", before_zip, "export-all ZIP", timeout=12, min_size=5000)
        assert zip_path.lower().endswith(".zip"), f"export-all: extensión no es .zip: {zip_path}"
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            png_count = sum(1 for n in names if n.lower().endswith(".png"))
            json_count = sum(1 for n in names if n.lower().endswith(".json"))
            leeme_count = sum(1 for n in names if "leeme" in n.lower())
            texto_count = sum(1 for n in names if "texto-para-acompanar" in n.lower() or ("texto" in n.lower() and "acompanar" in n.lower()))
            assert png_count == 9, f"ZIP: esperado 9 PNGs, got {png_count} in {names}"
            assert json_count >= 1, f"ZIP: esperado ≥1 JSON, got {json_count} in {names}"
            assert leeme_count >= 1, f"ZIP: esperado LEEME, got {names}"
            assert texto_count >= 1, f"ZIP: esperado texto-para-acompanar, got {names}"
            for n in names:
                info = zf.getinfo(n)
                assert info.file_size > 0, f"ZIP entry vacía: {n}"
        print(f"✓ export-all ZIP ok: {Path(zip_path).name} ({zip_sz} bytes, {len(names)} entries: {png_count} PNG + {json_count} JSON + LEEME + texto-para-acompanar)")

        # ============================================================
        # 6. CAPTION DOWNLOAD TXT
        # ============================================================
        caption_btn = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "copy-caption"))
        )
        real_click(driver, caption_btn)
        WebDriverWait(driver, TIMEOUT).until(
            lambda d: d.execute_script("return document.getElementById('caption-dialog').open"),
            message="caption-dialog no abrió",
        )
        print("✓ caption dialog abierto")

        before_txt = _pre_files("*.txt")
        dl_txt = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "download-caption"))
        )
        real_click(driver, dl_txt)
        txt_path, txt_sz = _wait_new_file("*.txt", before_txt, "caption download TXT", min_size=10)
        assert txt_path.lower().endswith(".txt"), f"caption TXT: extensión incorrecta: {txt_path}"
        print(f"✓ caption download TXT ok: {Path(txt_path).name} ({txt_sz} bytes)")

        # close caption dialog
        close_caption = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#caption-dialog [data-close='caption-dialog']"))
        )
        real_click(driver, close_caption)
        WebDriverWait(driver, TIMEOUT).until(
            lambda d: not d.execute_script("return document.getElementById('caption-dialog').open"),
            message="caption-dialog no se cerró",
        )
        print("✓ caption dialog cerrado")

        # ============================================================
        # 7. SCREENSHOT
        # ============================================================
        SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(SCREENSHOT))
        assert SCREENSHOT.exists() and SCREENSHOT.stat().st_size > 0
        print(f"✓ screenshot {SCREENSHOT} ({SCREENSHOT.stat().st_size} bytes)")

        # ============================================================
        # 8. CONSOLE NO SEVERE
        # ============================================================
        assert_no_severe_logs(driver)
        print("✓ consola sin SEVERE")

        total = time.time() - start_all
        print(f"\n=== DOWNLOADS E2E OK === total {total:.2f}s")
        print(f"  downloads: {DOWNLOAD_DIR}")
        for f in sorted(DOWNLOAD_DIR.iterdir()):
            print(f"    {f.name} ({f.stat().st_size} bytes)")

    except Exception as e:
        print("\n--- DOWNLOADS E2E FAILURE ---", file=sys.stderr)
        traceback.print_exc()
        try:
            if driver:
                SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
                fail_path = SCREENSHOT.parent / "failure-32-downloads.png"
                driver.save_screenshot(str(fail_path))
                print(f"screenshot fallo en {fail_path}", file=sys.stderr)
                try:
                    with open(SCREENSHOT.parent / "failure-32-downloads.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                except Exception:
                    pass
        except Exception as se:
            print(f"no se pudo guardar screenshot fallo: {se}", file=sys.stderr)
        raise AssertionError(f"downloads_e2e fallo: {e}") from e
    finally:
        try:
            if driver:
                driver.quit()
        except Exception:
            pass


def test_downloads_e2e():
    """Entry para pytest."""
    run()


if __name__ == "__main__":
    run()
