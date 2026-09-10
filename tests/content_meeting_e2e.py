#!/usr/bin/env python3
"""
E2E Contenido + Fecha/acceso y navegación.
- Reutiliza helpers de ui_smoke (_driver, real_click, wait_js, assert_no_severe_logs, BASE_URL, get_state)
- Fresh state (localStorage/IndexedDB clear + reload + whenReady)
- Ejercita y assert state para event-type/title/subtitle/reinforcement; details socialTitle/socialSubtitle/socialReinforcement
- Tabs click + keyboard ArrowRight/Left/Home/End; previous/next + disabled; step-count
- Fecha,time,endTime,timezone,platform,url,urlLabel,location,showQR,socialQR
- Generar valid -> errors vacío; provoca endTime inválido y URL inválida -> errors; restaura
- preview siempre activo (auto-preview ausente, canvas cambia solo)
- screenshot /tmp/ui-e2e/10-content-meeting.png; console no severe; prints; py_compile ok
"""
import os
import sys
import time
import traceback
import tempfile
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

TIMEOUT = 15
SCREENSHOT = Path("/tmp/ui-e2e/10-content-meeting.png")


def js_set_value(driver, selector, value):
    """Set value via JS and dispatch input/change; works even if panel hidden."""
    driver.execute_script(
        """
        const sel = arguments[0], val = arguments[1];
        const el = document.querySelector(sel);
        if (!el) throw new Error('selector no encontrado: '+sel);
        el.focus();
        if (el.tagName === 'SELECT') {
            el.value = val;
            el.dispatchEvent(new Event('input', {bubbles:true}));
            el.dispatchEvent(new Event('change', {bubbles:true}));
        } else if (el.type === 'checkbox') {
            el.checked = Boolean(val);
            el.dispatchEvent(new Event('input', {bubbles:true}));
            el.dispatchEvent(new Event('change', {bubbles:true}));
            el.dispatchEvent(new Event('click', {bubbles:true}));
        } else {
            el.value = val;
            el.dispatchEvent(new Event('input', {bubbles:true}));
            el.dispatchEvent(new Event('change', {bubbles:true}));
        }
        """,
        selector, value,
    )


def wait_state(driver, js_predicate, msg="", timeout=TIMEOUT):
    wait_js(driver, js_predicate, timeout=timeout, msg=msg)


def run():
    driver = None
    start_all = time.time()
    try:
        driver = _driver()

        # Fresh state igual que ui_smoke / image_canvas_e2e
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
        assert driver.execute_script("return !!(window.PLACTSStudio)"), "window.PLACTSStudio no existe"
        assert_no_severe_logs(driver)
        print("✓ fresh state ready: storage limpio + whenReady")

        # --- Contenido: event-type ---
        # asegurar panel Contenido visible (step 0)
        wait_js(driver, "document.getElementById('tab-content').getAttribute('aria-selected')==='true'", msg="tab-content no seleccionado inicialmente")
        # type -> Charla
        js_set_value(driver, "#event-type", "Charla")
        wait_state(driver, "window.PLACTSStudio.getState().event.type==='Charla'", msg="event.type no se actualizó a Charla")
        st = get_state(driver)
        assert st["event"]["type"] == "Charla", f"event.type esperado Charla got {st['event']['type']}"
        print("✓ event-type Charla ok -> state")

        # title
        js_set_value(driver, "#event-title", "Título E2E Contenido")
        wait_state(driver, "window.PLACTSStudio.getState().event.title==='Título E2E Contenido'", msg="title no reflejado")
        assert get_state(driver)["event"]["title"] == "Título E2E Contenido"
        # subtitle
        js_set_value(driver, "#event-subtitle", "Subtítulo de prueba E2E")
        wait_state(driver, "window.PLACTSStudio.getState().event.subtitle==='Subtítulo de prueba E2E'", msg="subtitle no reflejado")
        # reinforcement
        js_set_value(driver, "#event-reinforcement", "Refuerzo breve E2E")
        wait_state(driver, "window.PLACTSStudio.getState().event.reinforcement==='Refuerzo breve E2E'", msg="reinforcement no reflejado")
        print("✓ Contenido title/subtitle/reinforcement ejercitados y assert state")

        # details social: abrir y ejercitar
        # details .social-copy-panel
        details = WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, "details.social-copy-panel")))
        if details.get_attribute("open") is None:
            summary = details.find_element(By.CSS_SELECTOR, "summary")
            real_click(driver, summary)
            WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.CSS_SELECTOR, "details.social-copy-panel").get_attribute("open") is not None)
        print("✓ details social abierto")
        # socialTitle
        js_set_value(driver, "#social-title", "Social Title E2E")
        wait_state(driver, "window.PLACTSStudio.getState().options.socialTitle==='Social Title E2E'", msg="socialTitle no reflejado")
        # socialSubtitle
        js_set_value(driver, "#social-subtitle", "Social Subtitle E2E")
        wait_state(driver, "window.PLACTSStudio.getState().options.socialSubtitle==='Social Subtitle E2E'", msg="socialSubtitle no reflejado")
        # socialReinforcement checkbox
        js_set_value(driver, "#social-reinforcement", True)
        wait_state(driver, "window.PLACTSStudio.getState().options.socialReinforcement===true", msg="socialReinforcement no true")
        # verificar toggle off luego lo dejamos true para seguir
        js_set_value(driver, "#social-reinforcement", False)
        wait_state(driver, "window.PLACTSStudio.getState().options.socialReinforcement===false", msg="socialReinforcement no false")
        js_set_value(driver, "#social-reinforcement", True)
        wait_state(driver, "window.PLACTSStudio.getState().options.socialReinforcement===true", msg="socialReinforcement no true tras restore")
        print("✓ socialTitle/socialSubtitle/socialReinforcement ok (details abierto, state assert)")

        # --- Tabs click ---
        # click Participantes
        tab_people = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "tab-people")))
        real_click(driver, tab_people)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-people").get_attribute("aria-selected") == "true")
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "panel-people").is_displayed())
        assert get_state(driver)  # state intacta
        print("✓ tab click Participantes -> aria-selected true y panel visible")
        # click Imágenes
        tab_images = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "tab-images")))
        real_click(driver, tab_images)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-images").get_attribute("aria-selected") == "true")
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "panel-images").is_displayed())
        print("✓ tab click Imágenes ok")
        # click Fecha y acceso
        tab_meeting = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "tab-meeting")))
        real_click(driver, tab_meeting)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-meeting").get_attribute("aria-selected") == "true")
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "panel-meeting").is_displayed())
        print("✓ tab click Fecha y acceso ok")
        # click Contenido para volver
        tab_content = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "tab-content")))
        real_click(driver, tab_content)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-content").get_attribute("aria-selected") == "true")
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "panel-content").is_displayed())
        print("✓ tab click Contenido (vuelta) ok")

        # --- Tabs keyboard ArrowRight/Left/Home/End ---
        # Focus en tab-content
        driver.execute_script("document.getElementById('tab-content').focus()")
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return document.activeElement.id==='tab-content'"))
        # ArrowRight -> Participantes
        driver.find_element(By.ID, "tab-content").send_keys(Keys.ARROW_RIGHT)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-people").get_attribute("aria-selected") == "true")
        print("✓ keyboard ArrowRight 0->1 ok")
        # ArrowRight -> Imágenes
        driver.execute_script("document.getElementById('tab-people').focus()")
        driver.find_element(By.ID, "tab-people").send_keys(Keys.ARROW_RIGHT)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-images").get_attribute("aria-selected") == "true")
        print("✓ keyboard ArrowRight 1->2 ok")
        # ArrowLeft -> Participantes
        driver.execute_script("document.getElementById('tab-images').focus()")
        driver.find_element(By.ID, "tab-images").send_keys(Keys.ARROW_LEFT)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-people").get_attribute("aria-selected") == "true")
        print("✓ keyboard ArrowLeft 2->1 ok")
        # Home -> Contenido
        driver.execute_script("document.getElementById('tab-people').focus()")
        driver.find_element(By.ID, "tab-people").send_keys(Keys.HOME)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-content").get_attribute("aria-selected") == "true")
        print("✓ keyboard Home -> Contenido ok")
        # End -> Fecha y acceso
        driver.execute_script("document.getElementById('tab-content').focus()")
        driver.find_element(By.ID, "tab-content").send_keys(Keys.END)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-meeting").get_attribute("aria-selected") == "true")
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "panel-meeting").is_displayed())
        print("✓ keyboard End -> Fecha y acceso ok")
        # volver a Contenido via Home para siguiente sección
        driver.execute_script("document.getElementById('tab-meeting').focus()")
        driver.find_element(By.ID, "tab-meeting").send_keys(Keys.HOME)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-content").get_attribute("aria-selected") == "true")
        print("✓ keyboard navegación completa (ArrowRight/Left/Home/End)")

        # --- previous/next y disabled ---
        # en Paso 1
        step_count = driver.find_element(By.ID, "step-count").text
        assert "Paso 1" in step_count or "1 de 4" in step_count, f"step-count esperado Paso 1, got {step_count}"
        prev_btn = driver.find_element(By.ID, "previous-step")
        next_btn = driver.find_element(By.ID, "next-step")
        assert prev_btn.get_attribute("disabled") is not None or not prev_btn.is_enabled(), "previous debería estar disabled en paso 0"
        assert next_btn.get_attribute("disabled") is None and next_btn.is_enabled(), "next debería estar habilitado en paso 0"
        print(f"✓ step 0 previous disabled/next enabled ({step_count})")
        # next -> paso 2
        real_click(driver, next_btn)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-people").get_attribute("aria-selected") == "true")
        assert "Paso 2" in driver.find_element(By.ID, "step-count").text
        print("✓ next 1->2 ok")
        # next -> paso 3
        next_btn = driver.find_element(By.ID, "next-step")
        real_click(driver, next_btn)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-images").get_attribute("aria-selected") == "true")
        assert "Paso 3" in driver.find_element(By.ID, "step-count").text
        print("✓ next 2->3 ok")
        # next -> paso 4
        next_btn = driver.find_element(By.ID, "next-step")
        real_click(driver, next_btn)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-meeting").get_attribute("aria-selected") == "true")
        step4 = driver.find_element(By.ID, "step-count").text
        assert "Paso 4" in step4
        assert driver.find_element(By.ID, "next-step").get_attribute("disabled") is not None or not driver.find_element(By.ID, "next-step").is_enabled(), "next debe estar disabled en último paso"
        print(f"✓ next 3->4 ok y next disabled ({step4})")
        # previous -> paso 3
        prev_btn = driver.find_element(By.ID, "previous-step")
        assert prev_btn.is_enabled(), "previous debe estar habilitado en paso 3"
        real_click(driver, prev_btn)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-images").get_attribute("aria-selected") == "true")
        assert "Paso 3" in driver.find_element(By.ID, "step-count").text
        print("✓ previous 4->3 ok")
        # previous -> paso 2
        real_click(driver, driver.find_element(By.ID, "previous-step"))
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-people").get_attribute("aria-selected") == "true")
        print("✓ previous 3->2 ok")
        # previous -> paso 1
        real_click(driver, driver.find_element(By.ID, "previous-step"))
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-content").get_attribute("aria-selected") == "true")
        assert "Paso 1" in driver.find_element(By.ID, "step-count").text
        assert driver.find_element(By.ID, "previous-step").get_attribute("disabled") is not None
        print("✓ previous 2->1 ok y previous disabled")

        # navegar a Fecha y acceso para ejercitar esos controles
        real_click(driver, driver.find_element(By.ID, "tab-meeting"))
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "panel-meeting").is_displayed())
        print("✓ navegación a Fecha y acceso para controles de fecha/acceso")

        # --- Controles Fecha/acceso ---
        # fecha
        js_set_value(driver, "#event-date", "2026-09-28")
        wait_state(driver, "window.PLACTSStudio.getState().event.date==='2026-09-28'", msg="fecha no reflejada")
        # time
        js_set_value(driver, "#event-time", "19:00")
        wait_state(driver, "window.PLACTSStudio.getState().event.time==='19:00'", msg="time no reflejado")
        # endTime valid inicial
        js_set_value(driver, "#event-endTime", "20:30")
        wait_state(driver, "window.PLACTSStudio.getState().event.endTime==='20:30'", msg="endTime no reflejado")
        # timezone
        js_set_value(driver, "#event-timezone", "Argentina · UTC−3")
        wait_state(driver, "window.PLACTSStudio.getState().event.timezone==='Argentina · UTC−3'", msg="timezone no reflejado")
        # platform -> En vivo por YouTube
        js_set_value(driver, "#event-platform", "En vivo por YouTube")
        wait_state(driver, "window.PLACTSStudio.getState().event.platform==='En vivo por YouTube'", msg="platform no reflejado")
        # url
        js_set_value(driver, "#event-url", "https://www.youtube.com/@RedPLACTS")
        wait_state(driver, "window.PLACTSStudio.getState().event.url==='https://www.youtube.com/@RedPLACTS'", msg="url no reflejada")
        # urlLabel
        js_set_value(driver, "#event-urlLabel", "youtube.com/@RedPLACTS")
        wait_state(driver, "window.PLACTSStudio.getState().event.urlLabel==='youtube.com/@RedPLACTS'", msg="urlLabel no reflejado")
        # location
        js_set_value(driver, "#event-location", "Actividad abierta y gratuita")
        wait_state(driver, "window.PLACTSStudio.getState().event.location==='Actividad abierta y gratuita'", msg="location no reflejado")
        print("✓ fecha/time/endTime/timezone/platform/url/urlLabel/location ejercitados y assert state")

        # showQR
        js_set_value(driver, "#show-qr", True)
        wait_state(driver, "window.PLACTSStudio.getState().options.showQR===true", msg="showQR no true")
        print("✓ showQR true ok")
        # socialQR (en social-settings)
        js_set_value(driver, "#social-qr", True)
        wait_state(driver, "window.PLACTSStudio.getState().options.socialQR===true", msg="socialQR no true")
        print("✓ socialQR true ok")
        # dejar ambos true para valid QR
        # también desactivar y reactivar para cubrir toggle
        js_set_value(driver, "#show-qr", False)
        wait_state(driver, "window.PLACTSStudio.getState().options.showQR===false", msg="showQR no false")
        js_set_value(driver, "#show-qr", True)
        wait_state(driver, "window.PLACTSStudio.getState().options.showQR===true", msg="showQR no true restore")
        js_set_value(driver, "#social-qr", False)
        wait_state(driver, "window.PLACTSStudio.getState().options.socialQR===false", msg="socialQR no false")
        js_set_value(driver, "#social-qr", True)
        wait_state(driver, "window.PLACTSStudio.getState().options.socialQR===true", msg="socialQR no true restore")
        print("✓ showQR/socialQR toggle off/on ok")

        # --- Generar valid, errors vacío ---
        # asegurar título y fecha/time/timezone ya válidos; title ya seteado arriba
        # fixture: nombre obligatorio del expositor -> fijar Expositor E2E antes de Generar
        try:
            tab_people_fix = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "tab-people")))
            real_click(driver, tab_people_fix)
            WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "panel-people").is_displayed())
        except Exception:
            driver.execute_script("document.getElementById('tab-people')?.click()")
            WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "panel-people").is_displayed())
        speaker_id = driver.execute_script("return (window.PLACTSStudio.getState().speakers[0]||{}).id || null")
        assert speaker_id, "no se encontró primer speaker id para fijar nombre"
        driver.execute_script("const el=document.querySelector('[data-person=\"'+arguments[0]+'\"]'); if(el && !el.hasAttribute('open')) el.open=true;", speaker_id)
        js_set_value(driver, f"#name-{speaker_id}", "Expositor E2E")
        wait_state(driver, f"window.PLACTSStudio.getState().speakers.find(x=>x.id==='{speaker_id}').name==='Expositor E2E'", msg="speaker name Expositor E2E no reflejado en state")
        print(f"✓ checkpoint speaker name obligatorio 'Expositor E2E' fijado -> state id={speaker_id[:6]}")
        try:
            tab_meeting_fix = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "tab-meeting")))
            real_click(driver, tab_meeting_fix)
            WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "panel-meeting").is_displayed())
        except Exception:
            driver.execute_script("document.getElementById('tab-meeting')?.click()")
        # click Generar
        compile_btn = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "compile-button")))
        real_click(driver, compile_btn)
        # esperar que compile termine: errors hidden o valid plan? Revisar #errors hidden
        WebDriverWait(driver, 15).until(lambda d: d.execute_script("return document.getElementById('errors').hidden===true"))
        errors_hidden = driver.execute_script("return document.getElementById('errors').hidden")
        assert errors_hidden is True, f"errors debería estar hidden tras Generar válido, hidden={errors_hidden} html={driver.find_element(By.ID,'errors').get_attribute('innerHTML')[:300]}"
        # también validar via validationErrors vacio
        wait_state(driver, "window.PLACTSStudio.validationErrors(window.PLACTSStudio.getState()).length===0", msg="validationErrors no vacío tras Generar válido")
        print("✓ Generar válido -> errors vacío (hidden true y validationErrors 0)")

        # --- provocar endTime inválido ---
        js_set_value(driver, "#event-endTime", "18:00")  # <= time 19:00
        wait_state(driver, "window.PLACTSStudio.getState().event.endTime==='18:00'", msg="endTime invalido no reflejado")
        real_click(driver, driver.find_element(By.ID, "compile-button"))
        # esperar errors visible y contiene texto de finalización
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return document.getElementById('errors').hidden===false"))
        err_text = driver.find_element(By.ID, "errors").text
        assert "finalización" in err_text.lower() or "posterior al inicio" in err_text.lower(), f"errors endTime inválido esperado 'finalización debe ser posterior', got '{err_text}'"
        # también state error via validationErrors
        has_endtime_error = driver.execute_script("return window.PLACTSStudio.validationErrors().some(e=>e.field==='event-endTime')")
        assert has_endtime_error, "validationErrors debería contener event-endTime"
        print(f"✓ endTime inválido detectado -> errors visible: '{err_text[:120]}'")
        # restaurar endTime válido
        js_set_value(driver, "#event-endTime", "20:30")
        wait_state(driver, "window.PLACTSStudio.getState().event.endTime==='20:30'", msg="endTime restore no reflejado")

        # --- provocar URL inválida con QR activo ---
        # showQR y socialQR ya true, url inválida
        js_set_value(driver, "#event-url", "nota-url-invalida")
        wait_state(driver, "window.PLACTSStudio.getState().event.url==='nota-url-invalida'", msg="url invalida no reflejada")
        real_click(driver, driver.find_element(By.ID, "compile-button"))
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return document.getElementById('errors').hidden===false"))
        err_text2 = driver.find_element(By.ID, "errors").text
        assert "https://" in err_text2.lower() or "url" in err_text2.lower(), f"errors URL inválida esperado mención https/url, got '{err_text2}'"
        has_url_error = driver.execute_script("return window.PLACTSStudio.validationErrors().some(e=>e.field==='event-url')")
        assert has_url_error, "validationErrors debería contener event-url"
        print(f"✓ URL inválida detectada -> errors visible: '{err_text2[:120]}'")
        # restaurar URL válida
        js_set_value(driver, "#event-url", "https://www.youtube.com/@RedPLACTS")
        wait_state(driver, "window.PLACTSStudio.getState().event.url==='https://www.youtube.com/@RedPLACTS'", msg="url restore no reflejado")
        # generar de nuevo válido y verificar errors se vacía
        real_click(driver, driver.find_element(By.ID, "compile-button"))
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return document.getElementById('errors').hidden===true"))
        wait_state(driver, "window.PLACTSStudio.validationErrors().length===0", msg="validationErrors no vacío tras restaurar endTime y URL")
        print("✓ restaurado endTime y URL válidos -> errors vacío de nuevo")

        # --- preview siempre activo (auto-preview eliminado) ---
        # assert #auto-preview ya no existe en el DOM
        assert not driver.execute_script("return !!document.getElementById('auto-preview')"), "#auto-preview should not exist in DOM"
        print("✓ #auto-preview ausente en DOM (eliminado)")

        # capturar fingerprint actual del canvas seleccionado
        fp1 = driver.execute_script("""
            var c = document.querySelector('.poster-card canvas');
            if (!c) return null;
            return c.toDataURL('image/png').substring(0, 120);
        """)
        assert fp1, "canvas no encontrado antes de cambiar título"
        print(f"  canvas fingerprint inicial: {fp1[:60]}...")

        # cambiar título -> preview debe regenerarse automáticamente sin click en Generate
        js_set_value(driver, "#event-title", "Título auto-preview check")
        wait_state(driver, "window.PLACTSStudio.getState().event.title==='Título auto-preview check'", msg="title no reflejado")
        # esperar hasta que el fingerprint del canvas cambie
        WebDriverWait(driver, 15).until(lambda d: d.execute_script(
            "var c = document.querySelector('.poster-card canvas');"
            "if (!c) return false;"
            "var fp = c.toDataURL('image/png').substring(0, 120);"
            f"return fp !== '{fp1}';"
        ))
        fp2 = driver.execute_script("""
            var c = document.querySelector('.poster-card canvas');
            return c.toDataURL('image/png').substring(0, 120);
        """)
        assert fp2 != fp1, f"canvas no cambió tras modificar título: {fp2}"
        print(f"  canvas cambió automáticamente tras título -> {fp2[:60]}...")

        # restaurar título y verificar que canvas cambia de nuevo
        js_set_value(driver, "#event-title", "Título E2E Contenido Final")
        wait_state(driver, "window.PLACTSStudio.getState().event.title==='Título E2E Contenido Final'", msg="title restore no reflejado")
        WebDriverWait(driver, 15).until(lambda d: d.execute_script(
            "var c = document.querySelector('.poster-card canvas');"
            "if (!c) return false;"
            "var fp = c.toDataURL('image/png').substring(0, 120);"
            f"return fp !== '{fp2}';"
        ))
        fp3 = driver.execute_script("""
            var c = document.querySelector('.poster-card canvas');
            return c.toDataURL('image/png').substring(0, 120);
        """)
        assert fp3 != fp2, f"canvas no cambió tras restaurar título: {fp3}"
        print(f"  canvas cambió automáticamente tras restaurar título -> {fp3[:60]}...")
        print("✓ preview siempre activo verificado (sin #auto-preview, canvas se regenera solo)")

        # --- screenshot ---
        SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(SCREENSHOT))
        assert SCREENSHOT.exists() and SCREENSHOT.stat().st_size > 0, f"screenshot no creado en {SCREENSHOT}"
        print(f"✓ screenshot guardado en {SCREENSHOT} ({SCREENSHOT.stat().st_size} bytes)")

        # --- console no severe ---
        assert_no_severe_logs(driver)
        print("✓ consola sin SEVERE")

        total = time.time() - start_all
        print(f"\n=== CONTENT MEETING E2E OK === total {total:.2f}s")
        print(f"state final event.title='{get_state(driver)['event']['title']}' type='{get_state(driver)['event']['type']}' date={get_state(driver)['event']['date']} time={get_state(driver)['event']['time']} endTime={get_state(driver)['event']['endTime']}")
        print(f"screenshot {SCREENSHOT} preserved")

    except Exception as e:
        print("\n--- CONTENT MEETING E2E FAILURE ---", file=sys.stderr)
        traceback.print_exc()
        try:
            if driver:
                SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
                fail_path = SCREENSHOT.parent / "failure-content-meeting.png"
                driver.save_screenshot(str(fail_path))
                print(f"screenshot fallo en {fail_path}", file=sys.stderr)
                try:
                    with open(SCREENSHOT.parent / "failure-content-meeting.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                except Exception:
                    pass
        except Exception as se:
            print(f"no se pudo guardar screenshot fallo: {se}", file=sys.stderr)
        raise AssertionError(f"content_meeting_e2e fallo: {e}") from e
    finally:
        try:
            if driver:
                driver.quit()
        except Exception:
            pass


def test_content_meeting_e2e():
    """Entry para pytest."""
    run()


if __name__ == "__main__":
    run()
