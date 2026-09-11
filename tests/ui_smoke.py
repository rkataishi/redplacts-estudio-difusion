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
import struct
import sys
import tempfile
import time
import traceback
import zlib
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


def _write_solid_png(path, width=2400, height=1600, rgb=(180, 180, 190)):
    """Helper con struct/zlib que escribe PNG sólido 2400x1600 (sin Pillow)."""
    # PNG chunk helper usando struct y zlib (requerido por spec)
    def _chunk(chunk_type, data):
        c = chunk_type + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr = _chunk(b"IHDR", ihdr_data)
    # raw: filtro 0 + RGB por pixel, sólido
    # construir por filas para no crear una cadena gigante innecesaria en memoria intermedia
    row = b"\x00" + bytes(rgb) * width
    raw = row * height
    compressed = zlib.compress(raw)
    idat = _chunk(b"IDAT", compressed)
    iend = _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(sig + ihdr + idat + iend)


def run():
    driver = _driver()
    tmp_png = None
    tmp_large = None
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
        print("✓ checkpoint 1/8: estado inicial ok (speakers=1 moderators=0)")

        # 3) abrir Participantes (base para regresión foto grande) + foto grande 2400x1600
        tab_people = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "tab-people")))
        real_click(driver, tab_people)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "panel-people").get_attribute("hidden") is None or d.find_element(By.ID, "panel-people").is_displayed())
        # asegurar que tab quedo seleccionado
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-people").get_attribute("aria-selected") == "true")
        print("✓ checkpoint Participantes abierto")

        # --- regresión foto grande 2400x1600 sin bloquear UI ---
        # después de estado inicial y abrir Participantes: crear temp con struct/zlib,
        # send_keys al primer input[data-photo], esperar hasta 30s photo.data,
        # validar max(width,height)<=1100, duración<30s, editar nombre del mismo speaker y validar state
        photo_input = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-photo]"))
        )
        # asegurar que es el de speakers-list (primer expositor)
        try:
            first_inputs = driver.find_elements(By.CSS_SELECTOR, "#speakers-list input[data-photo]")
            if first_inputs:
                photo_input = first_inputs[0]
        except Exception:
            pass
        person_id = photo_input.get_attribute("data-photo")
        assert person_id, "no se encontró data-photo en primer input de participante"
        print(f"✓ checkpoint foto grande: input localizado para speaker {person_id}")
        # crear PNG sólido 2400x1600 con helper struct/zlib
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
            tmp_large = tf.name
        _write_solid_png(tmp_large, 2400, 1600)
        abs_large = os.path.abspath(tmp_large)
        assert os.path.exists(abs_large) and os.path.getsize(abs_large) > 0, "PNG temporal grande no creado"
        t0 = time.time()
        photo_input.send_keys(abs_large)
        # esperar hasta 30s photo.data para ese speaker
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script(
                "const id=arguments[0]; const s=window.PLACTSStudio.getState(); const p=(s.speakers.find(x=>x.id===id)||s.moderators.find(x=>x.id===id)); return !!(p && p.photo && p.photo.data);",
                person_id,
            ),
            message=f"timeout esperando photo.data para {person_id} tras upload grande",
        )
        elapsed = time.time() - t0
        assert elapsed < 30, f"carga foto grande tardó {elapsed:.1f}s >=30s (bloqueo UI)"
        st = get_state(driver)
        person = next((p for p in (st["speakers"] + st["moderators"]) if p["id"] == person_id), None)
        assert person is not None, f"speaker {person_id} no encontrado en state tras upload"
        assert person.get("photo") is not None, f"photo null tras carga grande para {person_id}"
        assert person["photo"].get("data", "").startswith("data:image"), f"photo.data no es data URL para {person_id}"
        w = person["photo"].get("width")
        h = person["photo"].get("height")
        assert w and h, f"photo sin width/height: {person['photo']}"
        assert max(w, h) <= 1100, f"foto grande no redimensionada: {w}x{h} max>1100 (esperado <=1100)"
        print(f"✓ checkpoint foto grande ok: 2400x1600 → {w}x{h} en {elapsed:.1f}s (max<=1100, duración<30s)")
        # editar nombre del mismo speaker y validar state (no bloqueado)
        name_input = None
        try:
            name_input = driver.find_element(By.ID, f"name-{person_id}")
        except Exception:
            pass
        if not name_input or not name_input.is_displayed():
            # fallback selector dentro de data-person
            name_input = WebDriverWait(driver, TIMEOUT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-person="{person_id}"] input[data-person-field="name"]'))
            )
        WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable(name_input))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", name_input)
        time.sleep(0.15)
        name_input.click()
        name_input.clear()
        new_name = f"Foto Grande OK {person_id[:4]}"
        name_input.send_keys(new_name)
        # disparar input/change si es necesario
        driver.execute_script("arguments[0].dispatchEvent(new Event('input',{bubbles:true})); arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", name_input)
        WebDriverWait(driver, TIMEOUT).until(
            lambda d: d.execute_script(
                "const id=arguments[0]; const n=arguments[1]; const s=window.PLACTSStudio.getState(); const p=s.speakers.find(x=>x.id===id)||s.moderators.find(x=>x.id===id); return p && p.name===n;",
                person_id,
                new_name,
            ),
            message=f"nombre no actualizado en state tras editar {person_id} a '{new_name}'",
        )
        st2 = get_state(driver)
        person2 = next((p for p in (st2["speakers"] + st2["moderators"]) if p["id"] == person_id), None)
        assert person2["name"] == new_name, f"nombre esperado '{new_name}' got '{person2['name']}'"
        print(f"✓ checkpoint edición tras foto grande ok: nombre='{new_name}' state consistente, no bloqueado")

        # 3b) #add-speaker y esperar speakers=2 (continúa flujo existente)
        # ya estamos en Participantes, sólo agregar expositor
        add_speaker = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "add-speaker")))
        real_click(driver, add_speaker)
        wait_js(driver, "window.PLACTSStudio.getState().speakers.length===2", msg="tras #add-speaker speakers!=2")
        st = get_state(driver)
        assert len(st["speakers"]) == 2, f"tras agregar expositor esperado 2, got {len(st['speakers'])}"
        print("✓ checkpoint 2/8: add speaker ok (speakers=2)")

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
        print("✓ checkpoint 3/8: add moderator/remove ok (moderators 1→0)")

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
        print("✓ checkpoint 4/8: mínimo speaker protegido (botón disabled, speakers=1)")

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
        print("✓ checkpoint 5/8: CTAs vacíos ok (Cargar imagen de fondo/principal)")

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
        # esperar CTA Reemplazar — selector específico dentro de .upload-copy evita colisión con botón Quitar
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.CSS_SELECTOR, "#asset-background .upload-copy .btn").text.strip() == "Reemplazar imagen de fondo")
        bg_cta_after = driver.find_element(By.CSS_SELECTOR, "#asset-background .upload-copy .btn")
        assert bg_cta_after.text.strip() == "Reemplazar imagen de fondo", f"tras upload CTA debe decir exactamente 'Reemplazar imagen de fondo', got '{bg_cta_after.text}'"
        assert "Reemplazar imagen de fondo" in bg_cta_after.text, f"CTA tras upload inesperado: '{bg_cta_after.text}'"
        print("✓ checkpoint 6/8: upload+CTA ok (Reemplazar imagen de fondo visible en .upload-copy .btn)")

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
        print("✓ checkpoint 7/8: navegación ok (Paso 3→4→3, Siguiente/Anterior)")

        # 8b) editor ancho, referencias y preview único (antes de consola)
        # .editor ancho >=400
        editor_el = WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".editor")))
        editor_width = driver.execute_script("return arguments[0].getBoundingClientRect().width", editor_el)
        assert editor_width >= 400, f".editor width esperado >=400, got {editor_width}"
        print(f"✓ checkpoint editor ancho ok: .editor rect width={editor_width:.1f} >=400")

        # referencias eliminadas intencionalmente: field-location / placement-inline / photo-placement → count 0
        for sel in (".field-location", ".placement-inline", ".photo-placement"):
            count = len(driver.find_elements(By.CSS_SELECTOR, sel))
            assert count == 0, f"esperado 0 '{sel}' (eliminadas intencionalmente), got {count}"
        print("✓ checkpoint referencias inline ok: .field-location / .placement-inline / .photo-placement → count 0")
        # volver a Imagenes para preview único
        tab_images_inline = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "tab-images")))
        real_click(driver, tab_images_inline)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "panel-images").is_displayed())

        # exactamente una .poster-card.is-selected
        selected_cards = driver.find_elements(By.CSS_SELECTOR, ".poster-card.is-selected")
        assert len(selected_cards) == 1, f"esperado exactamente 1 .poster-card.is-selected, got {len(selected_cards)}"
        selected_card = selected_cards[0]
        initial_selected_val = selected_card.get_attribute("data-card")
        assert initial_selected_val is not None, ".poster-card.is-selected sin data-card"

        # exactamente 9 [data-variant-select] displayed
        variant_btns = driver.find_elements(By.CSS_SELECTOR, "[data-variant-select]")
        displayed_variants = [b for b in variant_btns if b.is_displayed()]
        assert len(displayed_variants) == 9, f"esperado exactamente 9 [data-variant-select] displayed, got {len(displayed_variants)}"
        variant_vals = [b.get_attribute("data-variant-select") for b in displayed_variants]
        assert len(set(variant_vals)) == 9, f"variantes duplicadas: {variant_vals}"

        # exactamente 9 #overview-grid .overview-card con data-card únicos 0..8
        overview_cards = driver.find_elements(By.CSS_SELECTOR, "#overview-grid .overview-card")
        assert len(overview_cards) == 9, f"esperado exactamente 9 #overview-grid .overview-card, got {len(overview_cards)}"
        overview_card_vals = sorted([c.get_attribute("data-overview") for c in overview_cards])
        expected_vals = [str(i) for i in range(9)]
        assert overview_card_vals == expected_vals, f"overview card values esperados {expected_vals}, got {overview_card_vals}"
        print(f"✓ checkpoint preview galería ok: 1 selected ({initial_selected_val}), 9 variant buttons, 9 overview cards 0..8")

        # click en otro variant cambia .is-selected y mantiene 9 cards
        current_variant = None
        for b in displayed_variants:
            if b.get_attribute("aria-pressed") == "true":
                current_variant = b
                break
        if current_variant is None:
            current_variant = displayed_variants[0]
        target_variant = next((b for b in displayed_variants if b != current_variant), None)
        assert target_variant is not None, "no se encontró otro variant para click"
        target_val = target_variant.get_attribute("data-variant-select")
        real_click(driver, target_variant)
        # esperar .is-selected cambie
        WebDriverWait(driver, TIMEOUT).until(
            lambda d: d.execute_script("return document.querySelector('.poster-card.is-selected')?.dataset.card") == target_val,
            message=f".is-selected no cambió a {target_val} tras click en variant"
        )
        WebDriverWait(driver, TIMEOUT).until(
            lambda d: d.execute_script("return document.querySelector('[data-variant-select][aria-pressed=\"true\"]')?.dataset.variantSelect") == target_val,
            message=f"aria-pressed no cambió a {target_val} tras click"
        )
        # verificar thumbnail / poster-card.is-selected refleja el cambio
        selected_after = driver.execute_script("return document.querySelector('.poster-card.is-selected')?.dataset.card")
        assert selected_after == target_val, f"tras click .is-selected esperado {target_val}, got {selected_after}"
        # mantener 9 overview cards tras cambio
        overview_cards_after = driver.find_elements(By.CSS_SELECTOR, "#overview-grid .overview-card")
        assert len(overview_cards_after) == 9, f"tras cambiar variant deben mantenerse 9 #overview-grid .overview-card, got {len(overview_cards_after)}"
        is_selected_count = len(driver.find_elements(By.CSS_SELECTOR, ".poster-card.is-selected"))
        assert is_selected_count == 1, f"debe haber exactamente 1 .is-selected tras click, got {is_selected_count}"
        print(f"✓ checkpoint variant click ok: click variant {target_val} cambió .is-selected {initial_selected_val}->{selected_after}, 9 cards maintained")

        driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
            "width": 390, "height": 844, "deviceScaleFactor": 1, "mobile": True,
        })
        for button_id in ("identity-button", "about-button"):
            button = driver.find_element(By.ID, button_id)
            assert button.is_displayed() and button.text.strip(), f"#{button_id} debe ser visible a 390 px"
        mobile_cards = driver.find_elements(By.CSS_SELECTOR, "#overview-grid .overview-card")
        assert all(driver.execute_script(
            "const l=arguments[0].querySelector('.overview-label').getBoundingClientRect();"
            "const d=arguments[0].querySelector('.overview-dims').getBoundingClientRect();"
            "return d.top >= l.bottom;", card
        ) for card in mobile_cards), "label y dimensiones deben ocupar líneas separadas a 390 px"
        assert driver.execute_script("return document.documentElement.scrollWidth <= innerWidth"), "overflow horizontal móvil"
        print("✓ checkpoint móvil ok: Identidad/Ayuda visibles y metadatos separados a 390 px")

        long_title = "Inteligencia artificial, soberanía tecnológica y políticas públicas para un desarrollo federal sostenible e inclusivo en toda la Argentina"
        social_plans = driver.execute_async_script(
            "const done=arguments[arguments.length-1],s=window.PLACTSStudio.getState();"
            "s.options.socialTitle=arguments[0];"
            "window.PLACTSStudio.replace(s).then(()=>done(window.PLACTSStudio.getPlans())).catch(e=>done({error:String(e)}));",
            long_title,
        )
        assert isinstance(social_plans, list), f"no se recompilaron variantes con título social largo: {social_plans}"
        assert all(social_plans[i]["valid"] and not social_plans[i]["issues"] for i in (3, 4, 6, 8)), \
            "el título social largo debe conservar composiciones válidas y sin overflow"
        print("✓ checkpoint título social largo ok: variantes 3, 4, 6 y 8 válidas")

        # 9) capturar browser console severe final
        assert_no_severe_logs(driver)
        print("✓ checkpoint 8/8: consola limpia sin SEVERE")

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
        # cleanup tmp pngs (1x1 y grande 2400x1600) en finally
        for _p in (tmp_png, tmp_large):
            if _p and os.path.exists(_p):
                try:
                    os.unlink(_p)
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
