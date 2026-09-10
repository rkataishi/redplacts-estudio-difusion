#!/usr/bin/env python3
"""
E2E controles de participantes — people_controls_e2e.
- Reutiliza helpers de ui_smoke (_driver, real_click, wait_js, _write_solid_png, assert_no_severe_logs, BASE_URL, get_state)
- Fresh state (localStorage/IndexedDB clear + reload + whenReady)
- Abre Participantes, ejercita name/description/counter
- Agrega expositores hasta 6 y verifica #add-speaker disabled
- Mueve último arriba/abajo y verifica orden por state y DOM
- Elimina expositores hasta 1 (guard: botón eliminar disabled y click no cambia state)
- Moderadores: 0→2 (disabled) →0
- Upload foto pequeña, crop x/y/zoom por state y .crop-controls, quitar foto
- Keyboard Enter en trigger [data-upload-trigger] con JS click-counter + preventDefault (no abre picker nativo)
- screenshot /tmp/ui-e2e/20-people.png; console sin SEVERE; py_compile ok
"""
import os
import sys
import time
import traceback
import tempfile
import base64
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# helpers desde ui_smoke con fallback mínimo
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
        TIMEOUT_FB = 15
        def _driver():
            o = _Options()
            o.add_argument("--headless=new")
            o.add_argument("--no-sandbox")
            o.add_argument("--disable-dev-shm-usage")
            o.add_argument("--disable-gpu")
            o.add_argument("--window-size=1280,900")
            try:
                o.set_capability("goog:loggingPrefs", {"browser": "ALL"})
            except Exception:
                pass
            d = _webdriver.Chrome(options=o)
            d.set_window_size(1280, 900)
            return d
        def wait_js(driver, js_predicate, timeout=TIMEOUT_FB, msg=""):
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
            assert not severe, f"Console SEVERE: {severe}"
        def get_state(driver):
            return driver.execute_script("return window.PLACTSStudio.getState()")
        def _write_solid_png(path, width=2400, height=1600, rgb=(180,180,190)):
            def _chunk(t, data):
                c = t + data
                return _struct.pack(">I", len(data)) + c + _struct.pack(">I", _zlib.crc32(c) & 0xffffffff)
            sig = b"\x89PNG\r\n\x1a\n"
            ihdr = _chunk(b"IHDR", _struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            row = b"\x00" + bytes(rgb) * width
            raw = row * height
            comp = _zlib.compress(raw)
            idat = _chunk(b"IDAT", comp)
            iend = _chunk(b"IEND", b"")
            with open(path, "wb") as f:
                f.write(sig + ihdr + idat + iend)

TIMEOUT = 15
SCREENSHOT = Path("/tmp/ui-e2e/20-people.png")

def js_set_value(driver, selector, value):
    driver.execute_script(
        """
        const sel=arguments[0], val=arguments[1];
        const el=document.querySelector(sel);
        if(!el) throw new Error('selector no encontrado: '+sel);
        el.focus();
        if(el.tagName==='SELECT'){ el.value=val; el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); }
        else if(el.type==='checkbox'){ el.checked=Boolean(val); el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); el.dispatchEvent(new Event('click',{bubbles:true})); }
        else { el.value=val; el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); }
        """, selector, value)

def wait_state(driver, js_pred, msg="", timeout=TIMEOUT):
    wait_js(driver, js_pred, timeout=timeout, msg=msg)

def ensure_person_open(driver, person_id):
    # abre details si no está open
    details = WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'[data-person="{person_id}"]')))
    if details.get_attribute("open") is None:
        summary = details.find_element(By.CSS_SELECTOR, "summary")
        real_click(driver, summary)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.CSS_SELECTOR, f'[data-person="{person_id}"][open]') is not None)
    return details

def run():
    driver = None
    tmp_small = None
    start = time.time()
    try:
        driver = _driver()
        # fresh state
        driver.get(BASE_URL)
        WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState === 'complete'"))
        driver.execute_script("try{localStorage.clear();}catch(e){} try{sessionStorage.clear();}catch(e){}")
        try:
            driver.execute_async_script(
                """
                const cb=arguments[arguments.length-1];
                (async()=>{
                    try{
                        if(window.indexedDB && indexedDB.databases){
                            const dbs=await indexedDB.databases();
                            for(const db of dbs){ try{ indexedDB.deleteDatabase(db.name);}catch(e){} }
                        } else {
                            try{ indexedDB.deleteDatabase('redplacts-estudio-v2');}catch(e){}
                            try{ indexedDB.deleteDatabase('redplacts-estudio');}catch(e){}
                        }
                    }catch(e){}
                    try{localStorage.clear();}catch(e){}
                    try{sessionStorage.clear();}catch(e){}
                    cb(true);
                })();
                """
            )
        except Exception:
            pass
        driver.get(BASE_URL)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return !!(window.PLACTSStudio && window.PLACTSStudio.whenReady)"))
        driver.execute_async_script("const cb=arguments[arguments.length-1]; window.PLACTSStudio.whenReady().then(()=>cb(true)).catch(e=>cb('error:'+e));")
        assert driver.execute_script("return !!(window.PLACTSStudio)"), "PLACTSStudio no existe tras whenReady"
        assert_no_severe_logs(driver)
        print("✓ fresh state ready")

        # estado inicial
        wait_js(driver, "window.PLACTSStudio.getState().speakers.length===1", msg="speakers inicial !=1")
        wait_js(driver, "window.PLACTSStudio.getState().moderators.length===0", msg="moderators inicial !=0")
        st0 = get_state(driver)
        assert len(st0["speakers"])==1 and len(st0["moderators"])==0
        print(f"✓ estado inicial speakers=1 moderators=0 id={st0['speakers'][0]['id'][:6]}")

        # abrir people
        tab_people = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "tab-people")))
        real_click(driver, tab_people)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "panel-people").is_displayed())
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.ID, "tab-people").get_attribute("aria-selected") == "true")
        print("✓ tab Participantes abierto")

        # --- name/description/counter ---
        st = get_state(driver)
        pid = st["speakers"][0]["id"]
        ensure_person_open(driver, pid)
        # name
        name_sel = f"#name-{pid}"
        new_name = "Expositora E2E Prueba"
        js_set_value(driver, name_sel, new_name)
        wait_state(driver, f"window.PLACTSStudio.getState().speakers.find(x=>x.id==='{pid}').name===`{new_name}`", msg="name no reflejado")
        assert get_state(driver)["speakers"][0]["name"]==new_name
        # caption actualizar
        cap = driver.find_element(By.CSS_SELECTOR, f'[data-person="{pid}"] .person-caption strong').text
        assert new_name in cap, f"caption no actualizó: {cap}"
        print(f"✓ name edit ok '{new_name}' -> state y caption")

        # description + counter
        desc_sel = f"#description-{pid}"
        new_desc = "Investigadora · Red PLACTS · E2E people controls"
        js_set_value(driver, desc_sel, new_desc)
        wait_state(driver, f"window.PLACTSStudio.getState().speakers.find(x=>x.id==='{pid}').description===`{new_desc}`", msg="description no reflejado")
        counter_el = driver.find_element(By.CSS_SELECTOR, f'[data-person="{pid}"] .person-counter')
        exp_counter = f"{len(new_desc)}/200"
        # esperar counter actualización
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.find_element(By.CSS_SELECTOR, f'[data-person="{pid}"] .person-counter').text.strip()==exp_counter)
        assert counter_el.text.strip()==exp_counter, f"counter esperado {exp_counter} got {counter_el.text}"
        print(f"✓ description edit ok len {len(new_desc)} counter {exp_counter}")

        # verificar maxlength atributos 80/200 existen
        assert driver.find_element(By.ID, f"name-{pid}").get_attribute("maxlength")=="80"
        assert driver.find_element(By.ID, f"description-{pid}").get_attribute("maxlength")=="200"
        print("✓ maxlength name 80 / description 200 verificado")

        # --- add speakers hasta 6 disabled ---
        for expected in range(2, 7):
            add_btn = WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.ID, "add-speaker")))
            assert add_btn.is_enabled(), f"add-speaker debería estar enabled antes de {expected}"
            real_click(driver, add_btn)
            wait_state(driver, f"window.PLACTSStudio.getState().speakers.length==={expected}", msg=f"speakers no llegó a {expected}")
            # count label
            cnt_text = driver.find_element(By.ID, "speakers-count").text
            assert f"{expected} / 6" in cnt_text, f"speakers-count esperado {expected} / 6 got {cnt_text}"
            print(f"✓ add speaker -> {expected}/6 count label ok")
        # verificar disabled en 6
        add_speaker = driver.find_element(By.ID, "add-speaker")
        is_disabled = add_speaker.get_attribute("disabled") is not None or not add_speaker.is_enabled()
        assert is_disabled, f"add-speaker debe estar disabled en 6, disabled={add_speaker.get_attribute('disabled')} enabled={add_speaker.is_enabled()}"
        # intentar click no cambia
        try:
            driver.execute_script("arguments[0].click();", add_speaker)
        except Exception:
            pass
        time.sleep(0.4)
        assert len(get_state(driver)["speakers"])==6, "click en add-speaker disabled no debe agregar más"
        print("✓ speakers 6/6 alcanzado y #add-speaker disabled (guard)")

        # --- mover último arriba/abajo y verificar orden ---
        st6 = get_state(driver)
        ids_before = [p["id"] for p in st6["speakers"]]
        assert len(ids_before)==6
        last_id = ids_before[-1]
        prev_id = ids_before[-2]
        print(f"  orden antes mover: {[i[:4] for i in ids_before]} last={last_id[:4]} prev={prev_id[:4]}")
        # asegurar detalles abiertos para visualizar? no necesario, pero buscamos el card del último
        # mover último arriba (-1)
        last_card = driver.find_element(By.CSS_SELECTOR, f'[data-person="{last_id}"]')
        # scroll a controles
        up_btn = last_card.find_element(By.CSS_SELECTOR, '[data-move="-1"]')
        down_btn = last_card.find_element(By.CSS_SELECTOR, '[data-move="1"]')
        assert up_btn.is_enabled(), "up del último debe estar enabled"
        assert not down_btn.is_enabled() or down_btn.get_attribute("disabled") is not None, "down del último debe estar disabled"
        real_click(driver, up_btn)
        # esperar state orden cambiado: last debe quedar en penúltima posición
        def order_swapped(d):
            s = d.execute_script("return window.PLACTSStudio.getState().speakers.map(p=>p.id)")
            return s[-2]==last_id and s[-1]==prev_id
        WebDriverWait(driver, TIMEOUT).until(order_swapped, message="orden no cambió tras mover último arriba")
        st_after_up = get_state(driver)
        ids_after_up = [p["id"] for p in st_after_up["speakers"]]
        assert ids_after_up[-2]==last_id and ids_after_up[-1]==prev_id, f"orden tras up incorrecto: {ids_after_up} esperado swap {last_id[:4]}/{prev_id[:4]}"
        # verificar DOM order también
        dom_ids = driver.execute_script("return [...document.querySelectorAll('#speakers-list [data-person]')].map(el=>el.dataset.person)")
        assert dom_ids==ids_after_up, f"DOM order no coincide con state tras up: dom {dom_ids} vs state {ids_after_up}"
        print(f"✓ move up ok: last {last_id[:4]} subió -> orden {[i[:4] for i in ids_after_up][-3:]}")

        # mover el mismo (ahora penúltimo) abajo (+1) para restaurar
        # relocalizar card porque render cambió
        moved_card = driver.find_element(By.CSS_SELECTOR, f'[data-person="{last_id}"]')
        down_btn2 = moved_card.find_element(By.CSS_SELECTOR, '[data-move="1"]')
        assert down_btn2.is_enabled(), "down del movido debe estar enabled para bajar"
        real_click(driver, down_btn2)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return window.PLACTSStudio.getState().speakers.map(p=>p.id).join(',')") == ",".join(ids_before), message="orden no restaurado tras mover abajo")
        st_restored = get_state(driver)
        ids_restored = [p["id"] for p in st_restored["speakers"]]
        assert ids_restored==ids_before, f"orden debería restaurar original {ids_before} got {ids_restored}"
        dom_restored = driver.execute_script("return [...document.querySelectorAll('#speakers-list [data-person]')].map(el=>el.dataset.person)")
        assert dom_restored==ids_before
        print(f"✓ move down ok: restaurado orden original {[i[:4] for i in ids_restored][-3:]}")

        # --- eliminar speakers hasta quedar 1 con guard ---
        # eliminar hasta 1 (dejamos el last_id como sobreviviente o cualquiera)
        while True:
            st_cur = get_state(driver)
            n = len(st_cur["speakers"])
            if n<=1:
                break
            # elegir primer id que no sea el que queremos conservar? eliminar primero para simplificar
            to_remove = st_cur["speakers"][0]["id"]
            # si solo queda uno después, este loop dejará 1 igualmente; no importa cuál quede
            btn = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'#speakers-list [data-remove-person="{to_remove}"]')))
            real_click(driver, btn)
            wait_state(driver, f"window.PLACTSStudio.getState().speakers.length==={n-1}", msg=f"speakers no bajó a {n-1}")
        st_one = get_state(driver)
        assert len(st_one["speakers"])==1, f"debe quedar 1 speaker, got {len(st_one['speakers'])}"
        sole_id = st_one["speakers"][0]["id"]
        cnt_one = driver.find_element(By.ID, "speakers-count").text
        assert "1 / 6" in cnt_one
        # guard: botón eliminar disabled
        sole_btn = driver.find_element(By.CSS_SELECTOR, f'#speakers-list [data-remove-person="{sole_id}"]')
        disabled_rm = sole_btn.get_attribute("disabled") is not None or not sole_btn.is_enabled()
        assert disabled_rm, f"botón eliminar último speaker debe estar disabled, attrs disabled={sole_btn.get_attribute('disabled')} enabled={sole_btn.is_enabled()}"
        try:
            driver.execute_script("arguments[0].click();", sole_btn)
        except Exception:
            pass
        time.sleep(0.4)
        assert len(get_state(driver)["speakers"])==1, "guard falló: se eliminó último speaker"
        # add vuelve a estar enabled
        assert driver.find_element(By.ID, "add-speaker").is_enabled(), "#add-speaker debe volver a enabled con 1"
        print(f"✓ delete guard ok: speakers 6→1, último {sole_id[:4]} protegido (disabled), add-speaker re-enabled")

        # --- moderadores hasta 2 disabled luego eliminar hasta 0 ---
        # asegurar moderators 0 inicial
        assert len(get_state(driver)["moderators"])==0
        mod_count0 = driver.find_element(By.ID, "moderators-count").text
        assert "0 / 2" in mod_count0
        add_mod = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "add-moderator")))
        real_click(driver, add_mod)
        wait_state(driver, "window.PLACTSStudio.getState().moderators.length===1", msg="moderators no llegó a 1")
        assert "1 / 2" in driver.find_element(By.ID, "moderators-count").text
        print("✓ add moderator ->1/2")
        add_mod2 = driver.find_element(By.ID, "add-moderator")
        real_click(driver, add_mod2)
        wait_state(driver, "window.PLACTSStudio.getState().moderators.length===2", msg="moderators no llegó a 2")
        assert "2 / 2" in driver.find_element(By.ID, "moderators-count").text
        add_mod_final = driver.find_element(By.ID, "add-moderator")
        is_mod_disabled = add_mod_final.get_attribute("disabled") is not None or not add_mod_final.is_enabled()
        assert is_mod_disabled, "add-moderator debe estar disabled en 2"
        # intentar 3er click no cambia
        try:
            driver.execute_script("arguments[0].click();", add_mod_final)
        except Exception:
            pass
        time.sleep(0.4)
        assert len(get_state(driver)["moderators"])==2
        print("✓ moderators 2/2 alcanzado y #add-moderator disabled")

        # eliminar hasta 0 (moderadores no tienen guard de mínimo, sí se puede llegar a 0)
        st_mod = get_state(driver)
        for mid in [p["id"] for p in st_mod["moderators"]]:
            btn_m = WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'#moderators-list [data-remove-person="{mid}"]')))
            real_click(driver, btn_m)
            # esperar decremento
            # el count puede variar, esperamos que ese id ya no esté
            WebDriverWait(driver, TIMEOUT).until(lambda d, _mid=mid: _mid not in d.execute_script("return window.PLACTSStudio.getState().moderators.map(p=>p.id)"))
        wait_state(driver, "window.PLACTSStudio.getState().moderators.length===0", msg="moderators no llegó a 0 tras eliminar")
        assert "0 / 2" in driver.find_element(By.ID, "moderators-count").text
        assert driver.find_element(By.ID, "add-moderator").is_enabled(), "#add-moderator debe volver a enabled tras 0"
        print("✓ moderators 2→0 eliminados, add-moderator re-enabled")

        # --- upload foto pequeña, crop x/y/zoom, remove photo ---
        # re-obtener sole speaker (sigue siendo 1)
        sole_id = get_state(driver)["speakers"][0]["id"]
        ensure_person_open(driver, sole_id)
        # localizar input photo
        photo_input = WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'input[data-photo="{sole_id}"]')))
        # asegurar trigger visible
        trigger_label = driver.find_element(By.CSS_SELECTOR, f'label[for="photo-{sole_id}"]')
        assert "upload-trigger" in trigger_label.get_attribute("class") or trigger_label.get_attribute("data-upload-trigger")==sole_id
        # crear PNG pequeño 200x200 sólido
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
            tmp_small = tf.name
        _write_solid_png(tmp_small, 200, 200, rgb=(40, 180, 80))
        assert os.path.exists(tmp_small) and os.path.getsize(tmp_small)>0
        print(f"✓ trigger upload foto small: input data-photo {sole_id[:4]} localizado, PNG 200x200 creado")
        photo_input.send_keys(os.path.abspath(tmp_small))
        # esperar photo.data
        WebDriverWait(driver, 30).until(lambda d: d.execute_script("const id=arguments[0]; const s=window.PLACTSStudio.getState(); const p=s.speakers.find(x=>x.id===id)||s.moderators.find(x=>x.id===id); return !!(p && p.photo && p.photo.data);", sole_id), message="timeout esperando photo.data tras upload small")
        st_photo = get_state(driver)
        person_photo = next((p for p in st_photo["speakers"] if p["id"]==sole_id), None)
        assert person_photo and person_photo.get("photo"), "photo null tras upload small"
        assert person_photo["photo"].get("data","").startswith("data:image")
        w = person_photo["photo"].get("width"); h = person_photo["photo"].get("height")
        assert w and h and max(w,h) <= 1100, f"foto small no redimensionada <=1100 got {w}x{h}"
        print(f"✓ upload foto small ok: {w}x{h} data url presente")
        # verificar que crop controls aparecieron
        ensure_person_open(driver, sole_id)
        crop_x_input = WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'input[data-crop-id="{sole_id}"][data-crop-axis="x"]')))
        crop_y_input = driver.find_element(By.CSS_SELECTOR, f'input[data-crop-id="{sole_id}"][data-crop-axis="y"]')
        crop_zoom_input = driver.find_element(By.CSS_SELECTOR, f'input[data-crop-id="{sole_id}"][data-crop-axis="zoom"]')
        assert crop_x_input.is_displayed() and crop_y_input.is_displayed() and crop_zoom_input.is_displayed()
        # verificar Quitar foto botón aparece
        quit_btn = WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'[data-remove-photo="{sole_id}"]')))
        assert quit_btn.is_displayed()
        # thumb img existe con object-position
        thumb_img = driver.find_element(By.CSS_SELECTOR, f'[data-person="{sole_id}"] .person-thumb img')
        assert thumb_img is not None
        print("✓ crop controls y Quitar foto visibles tras upload")

        # mover crop x a 25
        driver.execute_script(
            """
            const sel=arguments[0], val=arguments[1];
            const el=document.querySelector(sel);
            el.value=val; el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true}));
            """, f'input[data-crop-id="{sole_id}"][data-crop-axis="x"]', "25")
        wait_state(driver, f"window.PLACTSStudio.getState().speakers.find(x=>x.id==='{sole_id}').crop.x===25", msg="crop x no 25")
        assert get_state(driver)["speakers"][0]["crop"]["x"]==25
        out_x = driver.find_element(By.CSS_SELECTOR, f'input[data-crop-id="{sole_id}"][data-crop-axis="x"] + output').text.strip()
        assert out_x=="25", f"output x esperado 25 got {out_x}"
        print("✓ crop x 50→25 state y output ok")

        # crop y a 75
        driver.execute_script(
            """
            const sel=arguments[0], val=arguments[1];
            const el=document.querySelector(sel);
            el.value=val; el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true}));
            """, f'input[data-crop-id="{sole_id}"][data-crop-axis="y"]', "75")
        wait_state(driver, f"window.PLACTSStudio.getState().speakers.find(x=>x.id==='{sole_id}').crop.y===75", msg="crop y no 75")
        assert get_state(driver)["speakers"][0]["crop"]["y"]==75
        out_y = driver.find_element(By.CSS_SELECTOR, f'input[data-crop-id="{sole_id}"][data-crop-axis="y"] + output').text.strip()
        assert out_y=="75"
        print("✓ crop y 50→75 state y output ok")

        # zoom a 150 (=1.5)
        driver.execute_script(
            """
            const sel=arguments[0], val=arguments[1];
            const el=document.querySelector(sel);
            el.value=val; el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true}));
            """, f'input[data-crop-id="{sole_id}"][data-crop-axis="zoom"]', "150")
        wait_state(driver, f"Math.abs(window.PLACTSStudio.getState().speakers.find(x=>x.id==='{sole_id}').crop.zoom-1.5)<0.001", msg="crop zoom no 1.5")
        zoom_val = get_state(driver)["speakers"][0]["crop"]["zoom"]
        assert abs(zoom_val-1.5) < 0.001, f"zoom esperado 1.5 got {zoom_val}"
        out_z = driver.find_element(By.CSS_SELECTOR, f'input[data-crop-id="{sole_id}"][data-crop-axis="zoom"] + output').text.strip()
        assert out_z=="150", f"output zoom esperado 150 got {out_z}"
        print("✓ crop zoom 100→150 (1.5) state y output ok")

        # quitar foto
        remove_photo_btn = driver.find_element(By.CSS_SELECTOR, f'[data-remove-photo="{sole_id}"]')
        real_click(driver, remove_photo_btn)
        wait_state(driver, f"window.PLACTSStudio.getState().speakers.find(x=>x.id==='{sole_id}').photo===null", msg="photo no se quitó")
        # verificar controles desaparecen
        time.sleep(0.3)
        assert len(driver.find_elements(By.CSS_SELECTOR, f'input[data-crop-id="{sole_id}"]'))==0, "crop inputs deberían desaparecer tras quitar foto"
        assert len(driver.find_elements(By.CSS_SELECTOR, f'[data-remove-photo="{sole_id}"]'))==0
        assert "Sin foto" in driver.find_element(By.CSS_SELECTOR, f'[data-person="{sole_id}"] .person-caption small').text
        print("✓ remove photo ok: state null, crop quitados, caption Sin foto")

        # --- keyboard Enter en trigger con JS click counter / preventDefault ---
        # tras quitar foto, photo es null. Re-localizar trigger y input
        trigger = WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'label[for="photo-{sole_id}"][data-upload-trigger="{sole_id}"]')))
        input_file = driver.find_element(By.ID, f"photo-{sole_id}")
        # instalar contador y preventDefault en el input para no abrir picker nativo
        driver.execute_script(
            """
            window.__peopleTriggerClicks = 0;
            window.__peopleInputClicks = 0;
            const input = arguments[0];
            const trigger = arguments[1];
            // remover listeners previos si existen
            if (window.__peopleInputHandler) { try{ input.removeEventListener('click', window.__peopleInputHandler);}catch(e){} }
            window.__peopleInputHandler = (e) => {
                window.__peopleInputClicks = (window.__peopleInputClicks||0)+1;
                e.preventDefault();
                e.stopPropagation();
            };
            input.addEventListener('click', window.__peopleInputHandler, true);
            // también contador en trigger por si se propaga
            if (window.__peopleTriggerHandler) { try{ trigger.removeEventListener('click', window.__peopleTriggerHandler);}catch(e){} }
            window.__peopleTriggerHandler = () => { window.__peopleTriggerClicks = (window.__peopleTriggerClicks||0)+1; };
            trigger.addEventListener('click', window.__peopleTriggerHandler);
            """, input_file, trigger)
        # enfocar trigger y enviar Enter
        driver.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].focus();", trigger)
        WebDriverWait(driver, TIMEOUT).until(lambda d: d.execute_script("return document.activeElement === arguments[0]", trigger))
        trigger.send_keys(Keys.ENTER)
        time.sleep(0.6)
        # verificar que el input recibió click vía delegado (handler hizo input.click())
        input_clicks = driver.execute_script("return window.__peopleInputClicks")
        # trigger click también puede haber sido contado, pero input es esencial
        assert input_clicks==1, f"Enter en trigger debería disparar input.click exactamente 1 vez, got input_clicks={input_clicks}"
        # photo debe seguir null porque preventDefault evitó picker y upload
        assert driver.execute_script(f"return window.PLACTSStudio.getState().speakers.find(x=>x.id==='{sole_id}').photo===null"), "photo debería seguir null tras Enter con preventDefault"
        print(f"✓ keyboard Enter en trigger: input.click counter={input_clicks} preventDefault ok, photo sigue null, no abre picker")
        # limpieza listeners
        driver.execute_script(
            """
            const input=arguments[0], trigger=arguments[1];
            try{ input.removeEventListener('click', window.__peopleInputHandler, true);}catch(e){}
            try{ trigger.removeEventListener('click', window.__peopleTriggerHandler);}catch(e){}
            """, input_file, trigger)

        # screenshot
        SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(SCREENSHOT))
        assert SCREENSHOT.exists() and SCREENSHOT.stat().st_size>0, f"screenshot no creado en {SCREENSHOT}"
        print(f"✓ screenshot guardado en {SCREENSHOT} ({SCREENSHOT.stat().st_size} bytes)")

        assert_no_severe_logs(driver)
        print("✓ consola sin SEVERE")

        total = time.time()-start
        print(f"\n=== PEOPLE CONTROLS E2E OK === total {total:.2f}s")
        print(f"state final speakers={len(get_state(driver)['speakers'])} moderators={len(get_state(driver)['moderators'])}")
        print(f"screenshot {SCREENSHOT} preserved")

    except Exception as e:
        print("\n--- PEOPLE CONTROLS E2E FAILURE ---", file=sys.stderr)
        traceback.print_exc()
        try:
            if driver:
                SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
                fail = SCREENSHOT.parent / "failure-people.png"
                driver.save_screenshot(str(fail))
                print(f"screenshot fallo en {fail}", file=sys.stderr)
                try:
                    with open(SCREENSHOT.parent / "failure-people.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                except Exception:
                    pass
        except Exception as se:
            print(f"no se pudo guardar screenshot fallo: {se}", file=sys.stderr)
        raise AssertionError(f"people_controls_e2e fallo: {e}") from e
    finally:
        if tmp_small and os.path.exists(tmp_small):
            try:
                os.unlink(tmp_small)
            except Exception:
                pass
        try:
            if driver:
                driver.quit()
        except Exception:
            pass

def test_people_controls_e2e():
    run()

if __name__=="__main__":
    run()
