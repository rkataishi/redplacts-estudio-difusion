#!/usr/bin/env python3
"""
E2E: controles de stage sin descarga (no-export).
- Fresh valid all fields → Generar canvas
- collection posters / social toggle (posters first, then social)
- exactly 3 variant buttons visible each collection; click all 6 total (0..5)
- poster-format, feed-format, export-scale selects
- socialPhotos / socialQR toggles
- autoPreview toggle
- re-Generar
- zoom dialog: open via poster frame and via view button, close each
- caption dialog: open, copy, close
- screenshot 30-stage.png
- console no severe; py_compile
"""
import os
import sys
import time
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
SCREENSHOT = Path("/tmp/ui-e2e/30-stage.png")

# ---------- helpers ----------

def js_set_value(driver, selector, value):
    driver.execute_script(
        """
        const sel = arguments[0], val = arguments[1];
        const el = document.querySelector(sel);
        if (!el) throw new Error('selector no encontrado: ' + sel);
        el.focus();
        if (el.tagName === 'SELECT') {
            el.value = val;
            el.dispatchEvent(new Event('input', {bubbles:true}));
            el.dispatchEvent(new Event('change', {bubbles:true}));
        } else if (el.type === 'checkbox') {
            if (el.checked !== Boolean(val)) { el.click(); }
        } else {
            el.value = val;
            el.dispatchEvent(new Event('input', {bubbles:true}));
            el.dispatchEvent(new Event('change', {bubbles:true}));
        }
        """,
        selector, value,
    )


def wait_state(driver, js_pred, msg="", timeout=TIMEOUT):
    wait_js(driver, js_pred, timeout=timeout, msg=msg)


def _count_displayed(driver, css):
    return len([e for e in driver.find_elements(By.CSS_SELECTOR, css) if e.is_displayed()])


# ---------- main ----------

def run():
    driver = None
    start_all = time.time()
    try:
        driver = _driver()

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
            set('#event-title','E2E Stage Controls');
            set('#event-date','2026-10-05');
            set('#event-time','18:00');
            set('#event-timezone','Argentina · UTC−3');
            """
        )
        wait_state(driver, "window.PLACTSStudio.getState().event.title==='E2E Stage Controls'")
        wait_state(driver, "window.PLACTSStudio.getState().event.date==='2026-10-05'")
        print("✓ fields filled")

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
        # 1. COLLECTION TOGGLE: posters first, then social
        # ============================================================
        btn_posters = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-collection="posters"]'))
        )
        real_click(driver, btn_posters)
        wait_state(driver, "document.querySelector('[data-collection=\"posters\"]').getAttribute('aria-pressed')==='true'")
        time.sleep(0.5)
        pf = driver.find_element(By.ID, "poster-format")
        assert pf.is_displayed(), "poster-format no visible en collection posters"
        print("✓ collection posters activada")

        btn_social = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-collection="social"]'))
        )
        real_click(driver, btn_social)
        wait_state(driver, "document.querySelector('[data-collection=\"social\"]').getAttribute('aria-pressed')==='true'")
        time.sleep(0.5)
        ss = driver.find_element(By.ID, "social-settings")
        assert ss.is_displayed(), "social-settings no visible en collection social"
        print("✓ collection social activada")

        # ============================================================
        # 2. VARIANT BUTTONS: exactly 3 visible each; click all 6
        # ============================================================
        real_click(driver, btn_posters)
        wait_state(driver, "document.querySelector('[data-collection=\"posters\"]').getAttribute('aria-pressed')==='true'")
        time.sleep(0.5)
        variant_btns = driver.find_elements(By.CSS_SELECTOR, "[data-variant-select]")
        visible_posters = [b for b in variant_btns if b.is_displayed()]
        assert len(visible_posters) == 3, f"posters collection: esperado 3 variant buttons, got {len(visible_posters)}"
        poster_variants = [b.get_attribute("data-variant-select") for b in visible_posters]
        print(f"✓ posters variant buttons: {poster_variants}")

        for b in visible_posters:
            idx = b.get_attribute("data-variant-select")
            real_click(driver, b)
            WebDriverWait(driver, TIMEOUT).until(
                lambda d, i=idx: d.execute_script(
                    "return document.querySelector('.poster-card.is-selected')?.dataset.card"
                ) == i,
                message=f"variant {idx} no seleccionado",
            )
            assert driver.execute_script(
                "return document.querySelector('.poster-card.is-selected')?.dataset.card"
            ) == idx, f"variant {idx} click falló"
            assert _count_displayed(driver, ".poster-card.is-selected") == 1
            print(f"  ✓ variant posters {idx} clicked & selected")

        real_click(driver, btn_social)
        wait_state(driver, "document.querySelector('[data-collection=\"social\"]').getAttribute('aria-pressed')==='true'")
        time.sleep(0.5)
        variant_btns2 = driver.find_elements(By.CSS_SELECTOR, "[data-variant-select]")
        visible_social = [b for b in variant_btns2 if b.is_displayed()]
        assert len(visible_social) == 3, f"social collection: esperado 3 variant buttons, got {len(visible_social)}"
        social_variants = [b.get_attribute("data-variant-select") for b in visible_social]
        print(f"✓ social variant buttons: {social_variants}")

        for b in visible_social:
            idx = b.get_attribute("data-variant-select")
            real_click(driver, b)
            WebDriverWait(driver, TIMEOUT).until(
                lambda d, i=idx: d.execute_script(
                    "return document.querySelector('.poster-card.is-selected')?.dataset.card"
                ) == i,
                message=f"variant {idx} no seleccionado",
            )
            assert driver.execute_script(
                "return document.querySelector('.poster-card.is-selected')?.dataset.card"
            ) == idx, f"variant {idx} click falló"
            assert _count_displayed(driver, ".poster-card.is-selected") == 1
            print(f"  ✓ variant social {idx} clicked & selected")

        # ============================================================
        # 3. SELECTS: poster-format, feed-format, export-scale
        # ============================================================
        real_click(driver, btn_posters)
        wait_state(driver, "document.querySelector('[data-collection=\"posters\"]').getAttribute('aria-pressed')==='true'")
        time.sleep(0.3)
        pf_sel = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "poster-format"))
        )
        assert pf_sel.is_displayed(), "poster-format no visible"
        js_set_value(driver, "#poster-format", "story")
        wait_state(driver, "window.PLACTSStudio.getState().options.format==='story'", msg="format no cambió a story")
        print("✓ poster-format → story ok")
        js_set_value(driver, "#poster-format", "portrait")
        wait_state(driver, "window.PLACTSStudio.getState().options.format==='portrait'", msg="format no restaurado")
        print("✓ poster-format → portrait restaurado")

        real_click(driver, btn_social)
        wait_state(driver, "document.querySelector('[data-collection=\"social\"]').getAttribute('aria-pressed')==='true'")
        time.sleep(0.3)
        ff_sel = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "feed-format"))
        )
        assert ff_sel.is_displayed(), "feed-format no visible"
        js_set_value(driver, "#feed-format", "square")
        wait_state(driver, "window.PLACTSStudio.getState().options.feedFormat==='square'", msg="feedFormat no cambió a square")
        print("✓ feed-format → square ok")
        js_set_value(driver, "#feed-format", "portrait")
        wait_state(driver, "window.PLACTSStudio.getState().options.feedFormat==='portrait'", msg="feedFormat no restaurado")
        print("✓ feed-format → portrait restaurado")

        es_sel = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "export-scale"))
        )
        assert es_sel.is_displayed(), "export-scale no visible"
        js_set_value(driver, "#export-scale", "1")
        wait_state(driver, "Number(window.PLACTSStudio.getState().options.scale)===1" , msg="scale no cambió a 1")
        print("✓ export-scale → 1 (1080px) ok")
        js_set_value(driver, "#export-scale", "2")
        wait_state(driver, "Number(window.PLACTSStudio.getState().options.scale)===2", msg="scale no restaurado")
        print("✓ export-scale → 2 (2160px) restaurado")

        # ============================================================
        # 4. TOGGLES: socialPhotos / socialQR
        # ============================================================
        sp_chk = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "social-photos"))
        )
        js_set_value(driver, "#social-photos", True)
        wait_state(driver, "window.PLACTSStudio.getState().options.socialPhotos===true", msg="socialPhotos no true")
        js_set_value(driver, "#social-photos", False)
        wait_state(driver, "window.PLACTSStudio.getState().options.socialPhotos===false", msg="socialPhotos no false")
        js_set_value(driver, "#social-photos", True)
        wait_state(driver, "window.PLACTSStudio.getState().options.socialPhotos===true", msg="socialPhotos no true restore")
        print("✓ socialPhotos toggle ok")

        sq_chk = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "social-qr"))
        )
        js_set_value(driver, "#social-qr", True)
        wait_state(driver, "window.PLACTSStudio.getState().options.socialQR===true", msg="socialQR no true")
        js_set_value(driver, "#social-qr", False)
        wait_state(driver, "window.PLACTSStudio.getState().options.socialQR===false", msg="socialQR no false")
        js_set_value(driver, "#social-qr", True)
        wait_state(driver, "window.PLACTSStudio.getState().options.socialQR===true", msg="socialQR no true restore")
        print("✓ socialQR toggle ok")

        # ============================================================
        # 5. AUTO-PREVIEW TOGGLE
        # ============================================================
        auto_chk = driver.find_element(By.ID, "auto-preview")
        assert auto_chk.is_displayed(), "auto-preview no visible"
        js_set_value(driver, "#auto-preview", False)
        assert not driver.execute_script("return document.getElementById('auto-preview').checked"), "auto-preview no quedó off"
        print("✓ auto-preview OFF")
        js_set_value(driver, "#auto-preview", True)
        assert driver.execute_script("return document.getElementById('auto-preview').checked"), "auto-preview no quedó on"
        print("✓ auto-preview ON")

        # ============================================================
        # 6. RE-GENERAR para tener canvas limpio tras cambios
        # ============================================================
        real_click(driver, compile_btn)
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script(
                "return document.querySelector('.poster-card canvas') && document.querySelector('.poster-card canvas').width>0"
            ),
            message="canvas no apareció tras re-Generar",
        )
        print("✓ re-Generar ok")

        # ============================================================
        # 7. ZOOM DIALOG: open via poster frame and via view button, close each
        # ============================================================
        real_click(driver, btn_posters)
        wait_state(driver, "document.querySelector('[data-collection=\"posters\"]').getAttribute('aria-pressed')==='true'")
        time.sleep(0.5)

        v0_btn = driver.find_element(By.CSS_SELECTOR, '[data-variant-select="0"]')
        real_click(driver, v0_btn)
        time.sleep(0.3)

        # --- open zoom via poster frame ---
        frame_el = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".poster-card.is-selected .poster-frame"))
        )
        real_click(driver, frame_el)
        zoom_diag = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "zoom-dialog"))
        )
        WebDriverWait(driver, TIMEOUT).until(
            lambda d: d.execute_script("return document.getElementById('zoom-dialog').open")
        )
        print("✓ zoom dialog abierto via poster frame")
        close_btn = zoom_diag.find_element(By.CSS_SELECTOR, "[data-close='zoom-dialog']")
        real_click(driver, close_btn)
        WebDriverWait(driver, TIMEOUT).until(
            lambda d: not d.execute_script("return document.getElementById('zoom-dialog').open")
        )
        print("✓ zoom dialog cerrado (frame)")

        # --- open zoom via view button ---
        view_btn = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".poster-card.is-selected .view-button"))
        )
        real_click(driver, view_btn)
        WebDriverWait(driver, TIMEOUT).until(
            lambda d: d.execute_script("return document.getElementById('zoom-dialog').open")
        )
        print("✓ zoom dialog abierto via view button")
        close_btn2 = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#zoom-dialog [data-close='zoom-dialog']"))
        )
        real_click(driver, close_btn2)
        WebDriverWait(driver, TIMEOUT).until(
            lambda d: not d.execute_script("return document.getElementById('zoom-dialog').open")
        )
        print("✓ zoom dialog cerrado (view button)")

        # restore to compare mode if needed
        try:
            view_compare = driver.find_element(By.ID, "view-compare")
            if view_compare.is_displayed():
                real_click(driver, view_compare)
                time.sleep(0.3)
        except Exception:
            pass

        # ============================================================
        # 8. CAPTION DIALOG: open, copy, close
        # ============================================================
        caption_btn = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "copy-caption"))
        )
        real_click(driver, caption_btn)
        caption_diag = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "caption-dialog"))
        )
        WebDriverWait(driver, TIMEOUT).until(
            lambda d: d.execute_script("return document.getElementById('caption-dialog').open"),
            message="caption-dialog no abrió",
        )
        print("✓ caption dialog abierto")
        caption_text = driver.execute_script("return document.getElementById('caption-text').value")
        assert len(caption_text) > 10, f"caption-text vacío o muy corto: '{caption_text[:50]}'"
        print(f"  caption-text len={len(caption_text)}")

        copy_text_btn = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "copy-caption-text"))
        )
        real_click(driver, copy_text_btn)
        time.sleep(0.5)
        print("✓ caption copy-text button clicked")

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
        # 9. SCREENSHOT
        # ============================================================
        SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(SCREENSHOT))
        assert SCREENSHOT.exists() and SCREENSHOT.stat().st_size > 0
        print(f"✓ screenshot {SCREENSHOT} ({SCREENSHOT.stat().st_size} bytes)")

        # ============================================================
        # 10. CONSOLE NO SEVERE
        # ============================================================
        assert_no_severe_logs(driver)
        print("✓ consola sin SEVERE")

        total = time.time() - start_all
        print(f"\n=== STAGE CONTROLS E2E OK (no-descarga) === total {total:.2f}s")
        py_compile.compile(str(Path(__file__)), doraise=True)
        print(f"✓ py_compile ok {Path(__file__).name}")

    except Exception as e:
        print("\n--- STAGE CONTROLS E2E FAILURE ---", file=sys.stderr)
        traceback.print_exc()
        try:
            if driver:
                SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
                fail_path = SCREENSHOT.parent / "failure-30-stage.png"
                driver.save_screenshot(str(fail_path))
                print(f"screenshot fallo en {fail_path}", file=sys.stderr)
                try:
                    with open(SCREENSHOT.parent / "failure-30-stage.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                except Exception:
                    pass
        except Exception as se:
            print(f"no se pudo guardar screenshot fallo: {se}", file=sys.stderr)
        raise AssertionError(f"stage_controls_e2e fallo: {e}") from e
    finally:
        try:
            if driver:
                driver.quit()
        except Exception:
            pass


def test_stage_controls_e2e():
    """Entry para pytest."""
    run()


if __name__ == "__main__":
    run()
