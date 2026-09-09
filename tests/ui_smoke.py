#!/usr/bin/env python3
"""
UI smoke test - prueba funcional real en navegador.
Sirve raiz con `python -m http.server`, abre Chrome headless en http://127.0.0.1:8000,
limpia localStorage/IndexedDB, espera window.PLACTSStudio.whenReady(),
verifica tabs, speakers/moderators, imagenes, navegacion y console severe.
Guarda screenshot/page source solo al fallo en /tmp.
"""
import base64
import os
import sys
import tempfile
import time
import traceback
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.environ.get("PLACTS_BASE_URL", "http://127.0.0.1:8000")
TIMEOUT = 15
SCREENSHOT = "/tmp/ui-smoke-failure.png"
PAGESOURCE = "/tmp/ui-smoke-failure.html"

def _opts():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,900")
    # habilitar logs de browser para capturar SEVERE
    try:
        opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    except Exception:
        pass
    return opts

def _driver():
    opts = _opts()
    # Selenium Manager resuelve chromedriver automaticamente
    driver = webdriver.Chrome(options=opts)
    driver.set_window_size(1280, 900)
    return driver

def wait_js(driver, js_predicate, timeout=TIMEOUT, msg=""):
    """Espera a que js_predicate retorne truthy."""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script(f"return !!({js_predicate})"),
        message=msg or f"timeout esperando JS: {js_predicate}",
    )

def get_state(driver):
    return driver.execute_script("return window.PLACTSStudio.getState()")

def assert_no_severe_logs(driver):
    try:
        logs = driver.get_log("browser")
    except Exception:
        return  # driver sin soporte de logs
    severe = [l for l in logs if l.get("level") == "SEVERE"]
    # filtrar favicon 404 etc? exigente: cualquier SEVERE es fallo
    assert not severe, f"Console SEVERE detectado: {severe} | logs completos: {logs}"

def real_click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    time.sleep(0.15)
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)

def run():
    driver = _driver()
    tmp_png = None
    try:
        # 1) abrir y limpiar storage antes de prueba, recargar y esperar whenReady
        driver.get(BASE_URL)
        WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState === 'complete'"))
        # limpiar localStorage / sessionStorage
        driver.execute_script("try{localStorage.clear();}catch(e){} try{sessionStorage.clear();}catch(e){}")
        # limpiar IndexedDB / origin storage
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
        # recargar
        driver.get(BASE_URL)
        WebDriverWait(driver, TIMEOUT).until(
            lambda d: d.execute_script("return !!(window.PLACTSStudio && window.PLACTSStudio.whenReady)"),
            message="window.PLACTSStudio.whenReady no disponible tras recarga",
        )
        # esperar whenReady (promise)
        driver.execute_async_script(
            """
            const cb = arguments[arguments.length-1];
            window.PLACTSStudio.whenReady().then(()=>cb(true)).catch(e=>cb('error:'+e));
            """
        )
        # verificar que whenReady resolvio truthy
        assert driver.execute_script("return !!(window.PLACTSStudio)"), "window.PLACTSStudio no existe tras whenReady"
        # capturar console severe temprano
        assert_no_severe_logs(driver)

        # 2) verificar estado inicial speakers=1 moderators=0
        wait_js(driver, "window.PLACTSStudio.getState().speakers.length===1", msg="estado inicial speakers!=1")
        wait_js(driver, "window.PLACTSStudio.getState().moderators.length===0", msg="estado inicial moderators!=0")
        st = get_state(driver)
        assert len(st["speakers"]) == 1, f"speakers inicial esperado 1, got {len(st['speakers'])} state={st}"
        assert len(st["moderators"]) == 0, f"moderators inicial esperado 0, got {len(st['moderators'])}"

        # 3) click real tab Participantes + #add-speaker y esperar speakers=2
        tab_people = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "tab-people")))
        real_click(driver, tab_people)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "panel-people").get_attribute("hidden") is None or d.find_element(By.ID, "panel-people").is_displayed())
        # asegurar que tab quedo seleccionado
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-people").get_attribute("aria-selected") == "true")
        add_speaker = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "add-speaker")))
        real_click(driver, add_speaker)
        wait_js(driver, "window.PLACTSStudio.getState().speakers.length===2", msg="tras #add-speaker speakers!=2")
        st = get_state(driver)
        assert len(st["speakers"]) == 2, f"tras agregar expositor esperado 2, got {len(st['speakers'])}"

        # 4) click #add-moderator y esperar moderators=1; eliminar ese moderador y volver 0
        add_mod = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "add-moderator")))
        real_click(driver, add_mod)
        wait_js(driver, "window.PLACTSStudio.getState().moderators.length===1", msg="tras #add-moderator moderators!=1")
        st = get_state(driver)
        assert len(st["moderators"]) == 1, f"tras agregar moderador esperado 1, got {len(st['moderators'])}"
        # el moderador creado debe tener boton eliminar
        mod_id = st["moderators"][0]["id"]
        # localizar boton eliminar de ese moderador
        remove_btn = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f'#moderators-list [data-remove-person="{mod_id}"]'))
        )
        real_click(driver, remove_btn)
        wait_js(driver, "window.PLACTSStudio.getState().moderators.length===0", msg="tras eliminar moderador moderators!=0")
        st = get_state(driver)
        assert len(st["moderators"]) == 0, f"tras eliminar moderador esperado 0, got {len(st['moderators'])}"

        # 5) comprobar que no se puede eliminar ultimo speaker (boton disabled)
        st = get_state(driver)
        assert len(st["speakers"]) == 2, "precondicion: deben quedar 2 speakers antes de probar ultimo"
        # eliminar uno para dejar 1 (dejamos 1 para probar bloqueo)
        # identificar primer speaker id
        first_id = st["speakers"][0]["id"]
        # hay 2 speakers, eliminar uno cualquiera via UI
        btn_first = driver.find_element(By.CSS_SELECTOR, f'#speakers-list [data-remove-person="{first_id}"]')
        real_click(driver, btn_first)
        wait_js(driver, "window.PLACTSStudio.getState().speakers.length===1", msg="tras eliminar para dejar 1 speaker")
        st = get_state(driver)
        assert len(st["speakers"]) == 1, f"debe quedar 1 speaker, got {len(st['speakers'])}"
        last_id = st["speakers"][0]["id"]
        last_remove = driver.find_element(By.CSS_SELECTOR, f'#speakers-list [data-remove-person="{last_id}"]')
        # debe estar disabled
        is_disabled = last_remove.get_attribute("disabled") is not None or last_remove.get_attribute("aria-disabled") == "true" or not last_remove.is_enabled()
        assert is_disabled, f"el boton eliminar del ultimo speaker (id {last_id}) debe estar disabled, attrs disabled={last_remove.get_attribute('disabled')} enabled={last_remove.is_enabled()}"
        # intentar click y verificar que sigue 1
        try:
            # click no debe cambiar estado; usamos js click forzado no deberia tampoco por guard en removePerson
            driver.execute_script("arguments[0].click();", last_remove)
        except Exception:
            pass
        time.sleep(0.5)
        st = get_state(driver)
        assert len(st["speakers"]) == 1, f"no se debe poder eliminar ultimo speaker, speakers={len(st['speakers'])} tras intento"

        # 6) navegar tab Imagenes; comprobar CTA visible Cargar imagen de fondo/principal
        tab_images = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "tab-images")))
        real_click(driver, tab_images)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "panel-images").is_displayed())
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-images").get_attribute("aria-selected") == "true")
        # verificar CTAs
        # buscar span.btn dentro de #asset-background y #asset-hero que contienen texto
        bg_cta = WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#asset-background .btn")))
        hero_cta = WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#asset-hero .btn")))
        assert bg_cta.is_displayed(), "CTA Cargar imagen de fondo no visible"
        assert hero_cta.is_displayed(), "CTA Cargar imagen principal no visible"
        assert "Cargar imagen de fondo" in bg_cta.text, f"CTA fondo texto inesperado: '{bg_cta.text}'"
        assert "Cargar imagen principal" in hero_cta.text, f"CTA hero texto inesperado: '{hero_cta.text}'"
        # inputs existen
        bg_input = driver.find_element(By.ID, "image-background")
        hero_input = driver.find_element(By.ID, "image-hero")
        assert bg_input is not None, "#image-background no existe"
        assert hero_input is not None, "#image-hero no existe"

        # 7) crear PNG 1x1 temporal en Python, send_keys a #image-background, esperar state image y CTA Reemplazar
        png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR42mP4//8/AAX+Av6fQV8AAAAASUVORK5CYII="
        png_bytes = base64.b64decode(png_b64)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
            tf.write(png_bytes)
            tmp_png = tf.name
        # send_keys necesita path absoluto
        abs_png = os.path.abspath(tmp_png)
        bg_input.send_keys(abs_png)
        # esperar state
        wait_js(driver, "!!window.PLACTSStudio.getState().images.background", timeout=15, msg="state.images.background sigue null tras upload")
        wait_js(driver, "!!window.PLACTSStudio.getState().images.background.data", timeout=15, msg="background.data vacio")
        st = get_state(driver)
        assert st["images"]["background"] is not None, "images.background debe estar seteado tras upload"
        assert st["images"]["background"]["data"].startswith("data:image"), f"background.data no es data URL: {str(st['images']['background']['data'])[:60]}"
        # esperar CTA Reemplazar
        WebDriverWait(driver, TIMEOUT).until(lambda d: "Reemplazar" in d.find_element(By.CSS_SELECTOR, "#asset-background .btn").text)
        bg_cta_after = driver.find_element(By.CSS_SELECTOR, "#asset-background .btn")
        assert "Reemplazar" in bg_cta_after.text, f"tras upload CTA debe decir Reemplazar, got '{bg_cta_after.text}'"
        assert "Reemplazar imagen de fondo" in bg_cta_after.text, f"CTA tras upload inesperado: '{bg_cta_after.text}'"

        # 8) probar Siguiente/Anterior
        # actualmente en Imagenes (paso 3 de 4). Siguiente debe ir a Fecha y acceso
        next_btn = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "next-step")))
        prev_btn = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "previous-step")))
        # capturar step-count antes
        step_count_el = driver.find_element(By.ID, "step-count")
        assert "Paso 3" in step_count_el.text or "3 de 4" in step_count_el.text, f"en Imagenes step-count debe ser Paso 3 de 4, got '{step_count_el.text}'"
        real_click(driver, next_btn)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-meeting").get_attribute("aria-selected") == "true")
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "panel-meeting").is_displayed())
        step_count_after = driver.find_element(By.ID, "step-count").text
        assert "Paso 4" in step_count_after or "4 de 4" in step_count_after, f"tras Siguiente debe ser Paso 4 de 4, got '{step_count_after}'"
        assert driver.find_element(By.ID, "next-step").get_attribute("disabled") is not None or not driver.find_element(By.ID, "next-step").is_enabled(), "en ultimo paso Siguiente debe estar disabled"
        # Anterior vuelve a Imagenes
        real_click(driver, prev_btn)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-images").get_attribute("aria-selected") == "true")
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "panel-images").is_displayed())
        step_back = driver.find_element(By.ID, "step-count").text
        assert "Paso 3" in step_back or "3 de 4" in step_back, f"tras Anterior debe volver a Paso 3 de 4, got '{step_back}'"

        # 9) capturar browser console severe final
        assert_no_severe_logs(driver)

        print("UI smoke OK: speakers/moderators, CTA, upload y navegacion verificados")

    except Exception as e:
        # guardar screenshot/page source solo al fallo
        try:
            driver.save_screenshot(SCREENSHOT)
            print(f"screenshot guardado en {SCREENSHOT}", file=sys.stderr)
        except Exception as se:
            print(f"no se pudo guardar screenshot: {se}", file=sys.stderr)
        try:
            with open(PAGESOURCE, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"page source guardado en {PAGESOURCE}", file=sys.stderr)
        except Exception as pe:
            print(f"no se pudo guardar page source: {pe}", file=sys.stderr)
        # imprimir traceback y re-raise con mensaje claro
        print("\n--- UI SMOKE FAILURE ---", file=sys.stderr)
        traceback.print_exc()
        raise AssertionError(f"UI smoke fallo: {e}") from e
    finally:
        # cleanup tmp png
        if tmp_png and os.path.exists(tmp_png):
            try:
                os.unlink(tmp_png)
            except Exception:
                pass
        try:
            driver.quit()
        except Exception:
            pass


def test_ui_smoke():
    """Entry para pytest."""
    run()


if __name__ == "__main__":
    run()
