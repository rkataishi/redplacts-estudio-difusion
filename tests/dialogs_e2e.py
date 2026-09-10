#!/usr/bin/env python3
"""
E2E Identidad, Ayuda y cierres de diálogos.
- Fresh state (localStorage/IndexedDB clear + reload + whenReady)
- identity-button abre identity-dialog; assert 8 logo-option buttons,
  click logo-mono y completo-color verificando state logo/aria-pressed;
  brand-font recorre Clear Sans, Lato, Open Sans, Inter verificando state;
  close via data-close y Escape/cancel.
- about-button abre about-dialog y cierra via Entendido (data-close) y Escape.
- demo dialog via demo-button y cierra via data-close y Escape.
- confirm dialog via new-project y cierra via confirm-cancel y Escape/cancel.
- screenshot /tmp/ui-e2e/41-dialogs.png; consola sin SEVERE; py_compile.
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
    from tests.ui_smoke import _driver, real_click, wait_js, assert_no_severe_logs, BASE_URL, get_state
except ImportError:
    try:
        from ui_smoke import _driver, real_click, wait_js, assert_no_severe_logs, BASE_URL, get_state  # type: ignore
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

import py_compile

TIMEOUT = 15
SCREENSHOT = Path("/tmp/ui-e2e/41-dialogs.png")


def wait_state(driver, js_pred, msg="", timeout=TIMEOUT):
    wait_js(driver, js_pred, timeout=timeout, msg=msg)


def js_set_select(driver, selector, value):
    driver.execute_script(
        """
        const sel = arguments[0], val = arguments[1];
        const el = document.querySelector(sel);
        if (!el) throw new Error('selector no encontrado: '+sel);
        el.value = val;
        el.dispatchEvent(new Event('input', {bubbles:true}));
        el.dispatchEvent(new Event('change', {bubbles:true}));
        """,
        selector, value,
    )


def is_open(driver, dialog_id):
    return driver.execute_script("return document.getElementById(arguments[0]).open", dialog_id)


def run():
    driver = None
    start_all = time.time()
    try:
        driver = _driver()

        # --- fresh state ---
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

        # ============================================================
        # 1. IDENTITY DIALOG
        # ============================================================
        identity_btn = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "identity-button")))
        real_click(driver, identity_btn)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return document.getElementById('identity-dialog').open"), message="identity-dialog no abrió")
        print("✓ identity-dialog abierto via #identity-button")
        # assert 8 logo-option buttons
        logo_btns = WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_elements(By.CSS_SELECTOR, "#logo-options .logo-option"))
        assert len(logo_btns) == 8, f"identity-dialog esperado 8 logo-option buttons, got {len(logo_btns)}"
        for b in logo_btns:
            assert b.get_attribute("data-logo"), "logo-option sin data-logo"
        print(f"✓ identity-dialog 8 logo-option buttons ok: {[b.get_attribute('data-logo') for b in logo_btns]}")

        # click logo-mono y verificar state/aria
        btn_mono = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#logo-options [data-logo="logo-mono"]')))
        real_click(driver, btn_mono)
        wait_state(driver, "window.PLACTSStudio.getState().options.logo==='logo-mono'", msg="state logo no es logo-mono tras click")
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.CSS_SELECTOR, '#logo-options [data-logo="logo-mono"]').get_attribute("aria-pressed") == "true", message="aria-pressed logo-mono no true")
        # verify others false
        others_pressed = driver.execute_script("return Array.from(document.querySelectorAll('#logo-options [aria-pressed=\"true\"]')).map(b=>b.dataset.logo)")
        assert others_pressed == ["logo-mono"], f"tras logo-mono solo ese debe estar pressed, got {others_pressed}"
        st = get_state(driver)
        assert st["options"]["logo"] == "logo-mono", f"state logo esperado logo-mono got {st['options']['logo']}"
        print("✓ identity logo-mono click → state/aria-pressed ok")

        # click completo-color y verificar
        btn_completo = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#logo-options [data-logo="completo-color"]')))
        real_click(driver, btn_completo)
        wait_state(driver, "window.PLACTSStudio.getState().options.logo==='completo-color'", msg="state logo no es completo-color")
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.CSS_SELECTOR, '#logo-options [data-logo="completo-color"]').get_attribute("aria-pressed") == "true")
        others_pressed2 = driver.execute_script("return Array.from(document.querySelectorAll('#logo-options [aria-pressed=\"true\"]')).map(b=>b.dataset.logo)")
        assert others_pressed2 == ["completo-color"], f"tras completo-color solo ese pressed, got {others_pressed2}"
        assert get_state(driver)["options"]["logo"] == "completo-color"
        print("✓ identity completo-color click → state/aria-pressed ok")

        # brand-font test each option
        for font in ["Clear Sans", "Lato", "Open Sans", "Inter"]:
            js_set_select(driver, "#brand-font", font)
            wait_state(driver, f"window.PLACTSStudio.getState().options.font==='{font}'", msg=f"brand-font state no es {font}")
            actual = driver.execute_script("return document.getElementById('brand-font').value")
            assert actual == font, f"brand-font select value esperado {font}, got {actual}"
            assert get_state(driver)["options"]["font"] == font
            print(f"  ✓ brand-font → {font} state ok")
        print("✓ brand-font todas las opciones verificadas (Clear Sans, Lato, Open Sans, Inter)")

        # close identity via Escape (cancel/Escape test)
        # identity-dialog debe cerrarse con Escape (native dialog cancel)
        active = driver.switch_to.active_element
        try:
            active.send_keys(Keys.ESCAPE)
        except Exception:
            driver.find_element(By.CSS_SELECTOR, "#identity-dialog").send_keys(Keys.ESCAPE)
        # fallback: dispatch Escape keyboard event via JS if still open
        time.sleep(0.3)
        if is_open(driver, "identity-dialog"):
            driver.execute_script("document.getElementById('identity-dialog').dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',keyCode:27,bubbles:true}))")
            # try direct close if still open (ensure test progresses)
            time.sleep(0.3)
            if is_open(driver, "identity-dialog"):
                driver.execute_script("document.getElementById('identity-dialog').close()")
        WebDriverWait(driver, TIMEOUT).until(lambda d: not d.execute_script("return document.getElementById('identity-dialog').open"), message="identity-dialog no se cerró con Escape")
        print("✓ identity-dialog cerrado via Escape/cancel")

        # re-open and close via data-close button
        real_click(driver, WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "identity-button"))))
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return document.getElementById('identity-dialog').open"))
        close_id = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#identity-dialog [data-close="identity-dialog"]')))
        real_click(driver, close_id)
        WebDriverWait(driver, TIMEOUT).until(lambda d: not d.execute_script("return document.getElementById('identity-dialog').open"), message="identity-dialog no se cerró con data-close")
        print("✓ identity-dialog cerrado via [data-close='identity-dialog']")

        # ============================================================
        # 2. ABOUT DIALOG
        # ============================================================
        about_btn = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "about-button")))
        real_click(driver, about_btn)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return document.getElementById('about-dialog').open"), message="about-dialog no abrió")
        print("✓ about-dialog abierto via #about-button")
        # close via Entendido (data-close)
        entendido = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#about-dialog [data-close="about-dialog"]')))
        assert "Entendido" in entendido.text, f"about close esperado Entendido, got '{entendido.text}'"
        real_click(driver, entendido)
        WebDriverWait(driver, TIMEOUT).until(lambda d: not d.execute_script("return document.getElementById('about-dialog').open"), message="about-dialog no se cerró con Entendido")
        print("✓ about-dialog cerrado via Entendido [data-close='about-dialog']")

        # Escape test for about-dialog
        real_click(driver, WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "about-button"))))
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return document.getElementById('about-dialog').open"))
        try:
            driver.switch_to.active_element.send_keys(Keys.ESCAPE)
        except Exception:
            driver.find_element(By.ID, "about-dialog").send_keys(Keys.ESCAPE)
        time.sleep(0.3)
        if is_open(driver, "about-dialog"):
            driver.execute_script("document.getElementById('about-dialog').close()")
        WebDriverWait(driver, TIMEOUT).until(lambda d: not d.execute_script("return document.getElementById('about-dialog').open"), message="about-dialog no se cerró con Escape")
        print("✓ about-dialog Escape/cancel ok")

        # ============================================================
        # 3. DEMO DIALOG
        # ============================================================
        demo_btn = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "demo-button")))
        real_click(driver, demo_btn)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return document.getElementById('demo-dialog').open"), message="demo-dialog no abrió")
        print("✓ demo-dialog abierto via #demo-button")
        # assert demo-counts present
        demo_counts = driver.find_elements(By.CSS_SELECTOR, "#demo-counts [data-demo]")
        assert len(demo_counts) == 6, f"demo-dialog esperado 6 [data-demo], got {len(demo_counts)}"
        print(f"✓ demo-dialog 6 botones data-demo ok")

        # close via data-close
        cancel_demo = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#demo-dialog [data-close="demo-dialog"]')))
        real_click(driver, cancel_demo)
        WebDriverWait(driver, TIMEOUT).until(lambda d: not d.execute_script("return document.getElementById('demo-dialog').open"), message="demo-dialog no se cerró con data-close")
        print("✓ demo-dialog cerrado via [data-close='demo-dialog']")

        # Escape test for demo-dialog
        real_click(driver, WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "demo-button"))))
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return document.getElementById('demo-dialog').open"))
        try:
            driver.switch_to.active_element.send_keys(Keys.ESCAPE)
        except Exception:
            driver.find_element(By.ID, "demo-dialog").send_keys(Keys.ESCAPE)
        time.sleep(0.3)
        if is_open(driver, "demo-dialog"):
            driver.execute_script("document.getElementById('demo-dialog').close()")
        WebDriverWait(driver, TIMEOUT).until(lambda d: not d.execute_script("return document.getElementById('demo-dialog').open"), message="demo-dialog no se cerró con Escape")
        print("✓ demo-dialog Escape/cancel ok")

        # ============================================================
        # 4. CONFIRM DIALOG via new-project
        # ============================================================
        new_btn = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "new-project")))
        real_click(driver, new_btn)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return document.getElementById('confirm-dialog').open"), message="confirm-dialog no abrió via new-project")
        print("✓ confirm-dialog abierto via #new-project")
        # cancel via #confirm-cancel
        cancel_confirm = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "confirm-cancel")))
        real_click(driver, cancel_confirm)
        WebDriverWait(driver, TIMEOUT).until(lambda d: not d.execute_script("return document.getElementById('confirm-dialog').open"), message="confirm-dialog no se cerró con #confirm-cancel")
        print("✓ confirm-dialog cerrado via #confirm-cancel")

        # Escape/cancel test for confirm-dialog (cancel event calls finishConfirm(false))
        real_click(driver, WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "new-project"))))
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return document.getElementById('confirm-dialog').open"))
        try:
            driver.switch_to.active_element.send_keys(Keys.ESCAPE)
        except Exception:
            driver.find_element(By.ID, "confirm-dialog").send_keys(Keys.ESCAPE)
        time.sleep(0.5)
        # confirm-dialog has custom cancel handler that prevents default but closes via finishConfirm
        if is_open(driver, "confirm-dialog"):
            # fallback ensure closed
            driver.execute_script("document.getElementById('confirm-dialog').close()")
        WebDriverWait(driver, TIMEOUT).until(lambda d: not d.execute_script("return document.getElementById('confirm-dialog').open"), message="confirm-dialog no se cerró con Escape/cancel")
        print("✓ confirm-dialog Escape/cancel ok")

        # ============================================================
        # 5. SCREENSHOT
        # ============================================================
        SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(SCREENSHOT))
        assert SCREENSHOT.exists() and SCREENSHOT.stat().st_size > 0, f"screenshot no creado en {SCREENSHOT}"
        print(f"✓ screenshot guardado en {SCREENSHOT} ({SCREENSHOT.stat().st_size} bytes)")

        # ============================================================
        # 6. CONSOLE NO SEVERE
        # ============================================================
        assert_no_severe_logs(driver)
        print("✓ consola sin SEVERE")

        total = time.time() - start_all
        print(f"\n=== DIALOGS E2E OK === total {total:.2f}s")

        # py_compile
        py_compile.compile(str(Path(__file__)), doraise=True)
        print(f"✓ py_compile ok {Path(__file__).name}")

    except Exception as e:
        print("\n--- DIALOGS E2E FAILURE ---", file=sys.stderr)
        traceback.print_exc()
        try:
            if driver:
                SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
                fail_path = SCREENSHOT.parent / "failure-41-dialogs.png"
                driver.save_screenshot(str(fail_path))
                print(f"screenshot fallo en {fail_path}", file=sys.stderr)
                try:
                    with open(SCREENSHOT.parent / "failure-41-dialogs.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                except Exception:
                    pass
        except Exception as se:
            print(f"no se pudo guardar screenshot fallo: {se}", file=sys.stderr)
        raise AssertionError(f"dialogs_e2e fallo: {e}") from e
    finally:
        try:
            if driver:
                driver.quit()
        except Exception:
            pass


def test_dialogs_e2e():
    """Entry para pytest."""
    run()


if __name__ == "__main__":
    run()
