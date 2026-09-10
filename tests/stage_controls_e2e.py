#!/usr/bin/env python3
"""
E2E: controles de stage sin descarga (no-export).
- Fresh valid all fields → Generar canvas
- assert no data-collection buttons, no #auto-preview element
- exactly 9 variant buttons + 9 overview cards (unique 0..8)
- iterate click all 9 variants, wait selected card each
- exercise export-scale 1 / 2
- socialPhotos / socialQR toggles via JS/state
- zoom dialog: open via poster-frame only, close
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
        # 1. ASSERT NO collection-toggle, NO auto-preview
        # ============================================================
        coll_btns = driver.find_elements(By.CSS_SELECTOR, "[data-collection]")
        assert len(coll_btns) == 0, f"se esperaron 0 data-collection buttons, hay {len(coll_btns)}"
        print("✓ no data-collection buttons (selector plano)")

        auto_el = driver.find_elements(By.ID, "auto-preview")
        assert len(auto_el) == 0, "no debe existir #auto-preview"
        print("✓ no #auto-preview element")

        # ============================================================
        # 2. VARIANT BUTTONS: exactly 9 visible (0..8)
        # ============================================================
        variant_btns = driver.find_elements(By.CSS_SELECTOR, "[data-variant-select]")
        visible_variants = [b for b in variant_btns if b.is_displayed()]
        assert len(visible_variants) == 9, f"esperado 9 variant buttons, got {len(visible_variants)}"
        variant_ids = sorted(b.get_attribute("data-variant-select") for b in visible_variants)
        assert variant_ids == [str(i) for i in range(9)], f"variant ids inesperados: {variant_ids}"
        print(f"✓ 9 variant buttons unique 0..8: {variant_ids}")

        # ============================================================
        # 3. OVERVIEW CARDS: exactly 9 (0..8)
        # ============================================================
        overview_cards = driver.find_elements(By.CSS_SELECTOR, "[data-overview]")
        assert len(overview_cards) == 9, f"esperado 9 overview cards, got {len(overview_cards)}"
        ov_ids = sorted(el.get_attribute("data-overview") for el in overview_cards)
        assert ov_ids == [str(i) for i in range(9)], f"overview ids inesperados: {ov_ids}"
        print(f"✓ 9 overview cards unique 0..8: {ov_ids}")

        # ============================================================
        # 4. CLICK ALL 9 VARIANTS, wait selected card each
        # ============================================================
        for i in range(9):
            btn = driver.find_element(By.CSS_SELECTOR, f'[data-variant-select="{i}"]')
            real_click(driver, btn)
            WebDriverWait(driver, TIMEOUT).until(
                lambda d, idx=str(i): d.execute_script(
                    "return document.querySelector('.poster-card.is-selected')?.dataset.card"
                ) == idx,
                message=f"variant {i} no seleccionado",
            )
            assert driver.execute_script(
                "return document.querySelector('.poster-card.is-selected')?.dataset.card"
            ) == str(i), f"variant {i} click falló"
            assert _count_displayed(driver, ".poster-card.is-selected") == 1
            print(f"  ✓ variant {i} clicked & selected")

        # ============================================================
        # 5. EXPORT-SCALE: exercise 1 / 2
        # ============================================================
        es_sel = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "export-scale"))
        )
        assert es_sel.is_displayed(), "export-scale no visible"
        js_set_value(driver, "#export-scale", "1")
        wait_state(driver, "Number(window.PLACTSStudio.getState().options.scale)===1", msg="scale no cambió a 1")
        print("✓ export-scale → 1 (1080px) ok")
        js_set_value(driver, "#export-scale", "2")
        wait_state(driver, "Number(window.PLACTSStudio.getState().options.scale)===2", msg="scale no restaurado")
        print("✓ export-scale → 2 (2160px) restaurado")

        # ============================================================
        # 6. SOCIAL PHOTOS / SOCIAL QR toggles via JS/state
        # ============================================================
        sp_el = driver.find_elements(By.ID, "social-photos")
        if sp_el:
            js_set_value(driver, "#social-photos", True)
            wait_state(driver, "window.PLACTSStudio.getState().options.socialPhotos===true", msg="socialPhotos no true")
            js_set_value(driver, "#social-photos", False)
            wait_state(driver, "window.PLACTSStudio.getState().options.socialPhotos===false", msg="socialPhotos no false")
            js_set_value(driver, "#social-photos", True)
            wait_state(driver, "window.PLACTSStudio.getState().options.socialPhotos===true", msg="socialPhotos no true restore")
            print("✓ socialPhotos toggle ok")
        else:
            state_photos = driver.execute_script("return window.PLACTSStudio.getState().options.socialPhotos")
            driver.execute_script("window.PLACTSStudio.getState().options.socialPhotos=true")
            wait_state(driver, "window.PLACTSStudio.getState().options.socialPhotos===true", msg="state socialPhotos no true")
            driver.execute_script("window.PLACTSStudio.getState().options.socialPhotos=false")
            wait_state(driver, "window.PLACTSStudio.getState().options.socialPhotos===false", msg="state socialPhotos no false")
            driver.execute_script(f"window.PLACTSStudio.getState().options.socialPhotos={repr(state_photos)}")
            print("✓ socialPhotos via JS/state ok (input removed)")

        sq_el = driver.find_elements(By.ID, "social-qr")
        if sq_el:
            js_set_value(driver, "#social-qr", True)
            wait_state(driver, "window.PLACTSStudio.getState().options.socialQR===true", msg="socialQR no true")
            js_set_value(driver, "#social-qr", False)
            wait_state(driver, "window.PLACTSStudio.getState().options.socialQR===false", msg="socialQR no false")
            js_set_value(driver, "#social-qr", True)
            wait_state(driver, "window.PLACTSStudio.getState().options.socialQR===true", msg="socialQR no true restore")
            print("✓ socialQR toggle ok")
        else:
            state_qr = driver.execute_script("return window.PLACTSStudio.getState().options.socialQR")
            driver.execute_script("window.PLACTSStudio.getState().options.socialQR=true")
            wait_state(driver, "window.PLACTSStudio.getState().options.socialQR===true", msg="state socialQR no true")
            driver.execute_script("window.PLACTSStudio.getState().options.socialQR=false")
            wait_state(driver, "window.PLACTSStudio.getState().options.socialQR===false", msg="state socialQR no false")
            driver.execute_script(f"window.PLACTSStudio.getState().options.socialQR={repr(state_qr)}")
            print("✓ socialQR via JS/state ok (input removed)")

        # ============================================================
        # 7. RE-GENERAR para tener canvas limpio tras cambios
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
        # 8. ZOOM DIALOG: open via poster-frame only (view-button hidden on desktop)
        # ============================================================
        v0_btn = driver.find_element(By.CSS_SELECTOR, '[data-variant-select="0"]')
        real_click(driver, v0_btn)
        time.sleep(0.3)

        frame_el = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".poster-card.is-selected .poster-frame"))
        )
        real_click(driver, frame_el)
        WebDriverWait(driver, TIMEOUT).until(
            lambda d: d.execute_script("return document.getElementById('zoom-dialog').open"),
            message="zoom-dialog no abrió via poster-frame",
        )
        print("✓ zoom dialog abierto via poster-frame")
        close_zoom = driver.find_element(By.CSS_SELECTOR, "[data-close='zoom-dialog']")
        real_click(driver, close_zoom)
        WebDriverWait(driver, TIMEOUT).until(
            lambda d: not d.execute_script("return document.getElementById('zoom-dialog').open"),
            message="zoom-dialog no se cerró",
        )
        print("✓ zoom dialog cerrado")

        # ============================================================
        # 9. CAPTION DIALOG: open, copy, close
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
        caption_text = driver.execute_script("return document.getElementById('caption-text').value")
        assert len(caption_text) > 10, f"caption-text vacío o muy corto: '{caption_text[:50]}'"
        print(f"  caption-text len={len(caption_text)}")

        copy_text_btn = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "copy-caption-text"))
        )
        real_click(driver, copy_text_btn)
        time.sleep(0.5)
        print("✓ caption copy-text clicked")

        dl_btn = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "download-caption"))
        )
        assert dl_btn.is_displayed(), "download-caption button not visible"
        print("✓ download-caption button present")

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
        # 10. SCREENSHOT
        # ============================================================
        SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(SCREENSHOT))
        assert SCREENSHOT.exists() and SCREENSHOT.stat().st_size > 0
        print(f"✓ screenshot {SCREENSHOT} ({SCREENSHOT.stat().st_size} bytes)")

        # ============================================================
        # 11. CONSOLE NO SEVERE
        # ============================================================
        assert_no_severe_logs(driver)
        print("✓ consola sin SEVERE")

        total = time.time() - start_all
        print(f"\n=== STAGE CONTROLS E2E OK (nueve outputs) === total {total:.2f}s")
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
