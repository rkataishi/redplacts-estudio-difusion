#!/usr/bin/env python3
"""
E2E proyecto: Nuevo/Abrir/Guardar/importar/Cargar ejemplo.
- Driver downloads dir. Fresh (localStorage/IndexedDB clear + reload + whenReady)
- demo-button open/close, reopen data-demo2 and confirm if needed, assert 2 speakers
- new-project confirm cancel preserves then confirm resets 1/0
- save-project download JSON
- open-project click intercepted counts project-file.click
- import saved JSON via project-file, confirm and state restored
- Ctrl/Cmd+S download JSON
- screenshot 40-project.png; console sin SEVERE; py_compile ok
"""
import os
import sys
import time
import glob
import json
import traceback
import tempfile
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
            assert not severe, f"Console SEVERE: {severe}"
        def get_state(driver):
            return driver.execute_script("return window.PLACTSStudio.getState()")
        def _write_solid_png(path, width=2400, height=1600, rgb=(180,180,190)):
            def _chunk(t, data):
                c=t+data
                return _struct.pack(">I", len(data))+c+_struct.pack(">I", _zlib.crc32(c)&0xffffffff)
            sig=b"\x89PNG\r\n\x1a\n"
            ihdr=_chunk(b"IHDR", _struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            row=b"\x00"+bytes(rgb)*width
            raw=row*height
            comp=_zlib.compress(raw)
            idat=_chunk(b"IDAT", comp)
            iend=_chunk(b"IEND", b"")
            with open(path,"wb") as f:
                f.write(sig+ihdr+idat+iend)

import py_compile

TIMEOUT = 15
SCREENSHOT = Path("/tmp/ui-e2e/40-project.png")
DOWNLOAD_DIR = Path("/tmp/ui-e2e/downloads-project")

def wait_state(driver, js_pred, msg="", timeout=TIMEOUT):
    wait_js(driver, js_pred, timeout=timeout, msg=msg)

def _pre_files(pattern):
    return set(glob.glob(str(DOWNLOAD_DIR / pattern)))

def _wait_new_file(pattern, before, label, timeout=10, min_size=50):
    deadline = time.time()+timeout
    while time.time()<deadline:
        new = set(glob.glob(str(DOWNLOAD_DIR / pattern))) - before
        if new:
            p = new.pop()
            sz = os.path.getsize(p)
            assert sz>min_size, f"{label}: archivo demasiado pequeño ({sz} bytes) {p}"
            return p, sz
        time.sleep(0.5)
    raise AssertionError(f"{label}: no apareció archivo nuevo ({pattern}) en {timeout}s")

def run():
    driver=None
    start_all=time.time()
    try:
        driver=_driver()
        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        # clean previous downloads (only project jsons for deterministic wait)
        for f in DOWNLOAD_DIR.glob("*"):
            try:
                f.unlink()
            except Exception:
                pass
        try:
            driver.execute_cdp_cmd("Page.setDownloadBehavior", {"behavior":"allow","downloadPath": str(DOWNLOAD_DIR)})
        except Exception as e:
            print(f"warn: setDownloadBehavior no disponible: {e}", file=sys.stderr)

        # --- fresh state ---
        driver.get(BASE_URL)
        WebDriverWait(driver,10).until(lambda d: d.execute_script("return document.readyState === 'complete'"))
        driver.execute_script("try{localStorage.clear();}catch(e){} try{sessionStorage.clear();}catch(e){}")
        try:
            driver.execute_async_script(
                """
                const cb=arguments[arguments.length-1];
                (async()=>{
                    try{
                        if(window.indexedDB && indexedDB.databases){
                            const dbs=await indexedDB.databases();
                            for(const db of dbs){ try{indexedDB.deleteDatabase(db.name);}catch(e){}}
                        } else { try{indexedDB.deleteDatabase('redplacts-estudio-v2');}catch(e){} try{indexedDB.deleteDatabase('redplacts-estudio');}catch(e){}}
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
        WebDriverWait(driver,TIMEOUT).until(lambda d: d.execute_script("return !!(window.PLACTSStudio && window.PLACTSStudio.whenReady)"), message="PLACTSStudio.whenReady no disponible")
        driver.execute_async_script("const cb=arguments[arguments.length-1]; window.PLACTSStudio.whenReady().then(()=>cb(true)).catch(e=>cb('error:'+e));")
        assert driver.execute_script("return !!(window.PLACTSStudio)"), "PLACTSStudio no existe"
        assert_no_severe_logs(driver)
        print("✓ fresh state ready")

        wait_state(driver, "window.PLACTSStudio.getState().speakers.length===1", msg="speakers inicial !=1")
        wait_state(driver, "window.PLACTSStudio.getState().moderators.length===0", msg="moderators inicial !=0")
        st0=get_state(driver)
        assert len(st0["speakers"])==1 and len(st0["moderators"])==0
        print(f"✓ estado inicial speakers=1 moderators=0")

        # ============================================================
        # 1. DEMO-BUTTON open/close
        # ============================================================
        demo_btn = WebDriverWait(driver,TIMEOUT).until(EC.element_to_be_clickable((By.ID,"demo-button")))
        real_click(driver, demo_btn)
        WebDriverWait(driver,TIMEOUT).until(lambda d: d.execute_script("return document.getElementById('demo-dialog').open===true"), message="demo-dialog no abrió")
        print("✓ demo-button → demo-dialog open")
        # close via Cancel button
        cancel_demo = WebDriverWait(driver,TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#demo-dialog [data-close='demo-dialog']")))
        real_click(driver, cancel_demo)
        WebDriverWait(driver,TIMEOUT).until(lambda d: not d.execute_script("return document.getElementById('demo-dialog').open"))
        print("✓ demo-dialog close via Cancel → cerrado")

        # ============================================================
        # 2. REOPEN data-demo2 and confirm if needed, assert 2 speakers
        # ============================================================
        real_click(driver, demo_btn)
        WebDriverWait(driver,TIMEOUT).until(lambda d: d.execute_script("return document.getElementById('demo-dialog').open===true"))
        btn_demo2 = WebDriverWait(driver,TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-demo="2"]')))
        real_click(driver, btn_demo2)
        # demo-dialog should close immediately
        WebDriverWait(driver,TIMEOUT).until(lambda d: not d.execute_script("return document.getElementById('demo-dialog').open"), message="demo-dialog no se cerró tras data-demo2")
        # if confirm needed (state.example was false), confirm-dialog appears
        time.sleep(0.4)
        confirm_open = driver.execute_script("return document.getElementById('confirm-dialog').open===true")
        if confirm_open:
            # confirm dialog for "¿Reemplazar por un ejemplo?"
            title_txt = driver.execute_script("return document.getElementById('confirm-title').textContent")
            print(f"  confirm requerido tras data-demo2: '{title_txt}'")
            # must confirm
            confirm_ok = WebDriverWait(driver,TIMEOUT).until(EC.element_to_be_clickable((By.ID,"confirm-ok")))
            real_click(driver, confirm_ok)
            WebDriverWait(driver,TIMEOUT).until(lambda d: not d.execute_script("return document.getElementById('confirm-dialog').open"))
            print("✓ confirm 'Reemplazar por un ejemplo' → Continuar")
        else:
            print("  no confirm necesario (state.example already true)")

        # wait speakers 2
        wait_state(driver, "window.PLACTSStudio.getState().speakers.length===2", msg="speakers no llegó a 2 tras demo2")
        st_demo = get_state(driver)
        assert len(st_demo["speakers"])==2, f"demo2 esperado 2 speakers got {len(st_demo['speakers'])}"
        assert st_demo.get("example") is True, "demo2 debe dejar state.example true"
        print(f"✓ demo data-demo2 → speakers=2 (moderators={len(st_demo['moderators'])}) example=true")

        # ============================================================
        # 3. NEW-PROJECT confirm cancel preserves then confirm resets 1/0
        # ============================================================
        new_btn = WebDriverWait(driver,TIMEOUT).until(EC.element_to_be_clickable((By.ID,"new-project")))
        # cancel path
        real_click(driver, new_btn)
        WebDriverWait(driver,TIMEOUT).until(lambda d: d.execute_script("return document.getElementById('confirm-dialog').open===true"), message="confirm-dialog no abrió tras new-project")
        conf_title = driver.execute_script("return document.getElementById('confirm-title').textContent")
        assert "Crear un nuevo" in conf_title or "nuevo encuentro" in conf_title.lower(), f"confirm title inesperado tras new-project: {conf_title}"
        print(f"✓ new-project → confirm-dialog open '{conf_title}'")
        cancel_btn = WebDriverWait(driver,TIMEOUT).until(EC.element_to_be_clickable((By.ID,"confirm-cancel")))
        real_click(driver, cancel_btn)
        WebDriverWait(driver,TIMEOUT).until(lambda d: not d.execute_script("return document.getElementById('confirm-dialog').open"))
        print("✓ new-project confirm Cancel → dialog cerrado")
        # state preserved
        st_after_cancel = get_state(driver)
        assert len(st_after_cancel["speakers"])==2, f"tras cancel preserves esperado 2 speakers got {len(st_after_cancel['speakers'])}"
        print("✓ new-project cancel preserves state (speakers 2)")

        # confirm resets
        real_click(driver, new_btn)
        WebDriverWait(driver,TIMEOUT).until(lambda d: d.execute_script("return document.getElementById('confirm-dialog').open===true"))
        ok_btn = WebDriverWait(driver,TIMEOUT).until(EC.element_to_be_clickable((By.ID,"confirm-ok")))
        real_click(driver, ok_btn)
        WebDriverWait(driver,TIMEOUT).until(lambda d: not d.execute_script("return document.getElementById('confirm-dialog').open"))
        # wait reset to blank
        wait_state(driver, "window.PLACTSStudio.getState().speakers.length===1", msg="tras new confirm speakers no 1")
        wait_state(driver, "window.PLACTSStudio.getState().moderators.length===0", msg="tras new confirm moderators no 0")
        st_reset = get_state(driver)
        assert len(st_reset["speakers"])==1 and len(st_reset["moderators"])==0, f"tras new confirm esperado 1/0 got {len(st_reset['speakers'])}/{len(st_reset['moderators'])}"
        # title should be empty after blank
        assert st_reset["event"]["title"]=="" or st_reset["event"]["title"] is None or st_reset["event"]["title"]=="", f"tras reset title esperado vacío got '{st_reset['event']['title']}'"
        print("✓ new-project Confirm → reset 1/0 ok (blankProject)")

        # For meaningful save/import, we will reload demo2 again and save that as reference,
        # unless spec expects save of blank. We need a saved JSON to import and assert restored.
        # Re-create demo2 state to have data to preserve across new-project reset.
        # We already have reset to blank; now reload demo2 to generate savable example.
        real_click(driver, demo_btn)
        WebDriverWait(driver,TIMEOUT).until(lambda d: d.execute_script("return document.getElementById('demo-dialog').open===true"))
        btn_demo2_b = WebDriverWait(driver,TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-demo="2"]')))
        real_click(driver, btn_demo2_b)
        WebDriverWait(driver,TIMEOUT).until(lambda d: not d.execute_script("return document.getElementById('demo-dialog').open"))
        # after reset, state.example is false again, so confirm will appear
        time.sleep(0.4)
        if driver.execute_script("return document.getElementById('confirm-dialog').open===true"):
            real_click(driver, WebDriverWait(driver,TIMEOUT).until(EC.element_to_be_clickable((By.ID,"confirm-ok"))))
            WebDriverWait(driver,TIMEOUT).until(lambda d: not d.execute_script("return document.getElementById('confirm-dialog').open"))
        wait_state(driver, "window.PLACTSStudio.getState().speakers.length===2", msg="re-demo2 speakers no 2")
        st_for_save = get_state(driver)
        print(f"✓ re-demo2 for save → speakers=2 listo para Guardar")

        # ============================================================
        # 4. SAVE-PROJECT download JSON
        # ============================================================
        before_json = _pre_files("*.json")
        save_btn = WebDriverWait(driver,TIMEOUT).until(EC.element_to_be_clickable((By.ID,"save-project")))
        real_click(driver, save_btn)
        json_path, json_sz = _wait_new_file("*.json", before_json, "save-project download", timeout=10, min_size=50)
        assert json_path.lower().endswith(".json")
        # validate JSON structure
        with open(json_path,"r",encoding="utf-8") as f:
            saved_data = json.load(f)
        assert "event" in saved_data and "speakers" in saved_data, f"JSON guardado sin keys esperadas: {list(saved_data.keys())[:5]}"
        assert len(saved_data["speakers"])==2, f"JSON guardado speakers esperado 2 got {len(saved_data['speakers'])}"
        saved_title = saved_data["event"].get("title","")
        print(f"✓ save-project download JSON ok: {Path(json_path).name} ({json_sz} bytes) title='{saved_title[:30]}' speakers=2")

        # Need to reset again to blank before import test, so import restores saved state
        real_click(driver, new_btn)
        WebDriverWait(driver,TIMEOUT).until(lambda d: d.execute_script("return document.getElementById('confirm-dialog').open===true"))
        real_click(driver, WebDriverWait(driver,TIMEOUT).until(EC.element_to_be_clickable((By.ID,"confirm-ok"))))
        WebDriverWait(driver,TIMEOUT).until(lambda d: not d.execute_script("return document.getElementById('confirm-dialog').open"))
        wait_state(driver, "window.PLACTSStudio.getState().speakers.length===1", msg="reset before import no 1")
        print("✓ reset to blank before import (1/0)")

        # ============================================================
        # 5. OPEN-PROJECT click intercepted counts project-file.click
        # ============================================================
        driver.execute_script(
            """
            window.__projectFileClicks=0;
            const inp=document.getElementById('project-file');
            if(!inp) throw new Error('project-file not found');
            inp.__origClick = inp.click.bind(inp);
            inp.click = function(){ window.__projectFileClicks=(window.__projectFileClicks||0)+1; };
            """
        )
        open_btn = WebDriverWait(driver,TIMEOUT).until(EC.element_to_be_clickable((By.ID,"open-project")))
        real_click(driver, open_btn)
        time.sleep(0.4)
        clicks = driver.execute_script("return window.__projectFileClicks")
        assert clicks==1, f"open-project debería disparar project-file.click 1 vez, got {clicks}"
        print(f"✓ open-project click intercepted → project-file.click count={clicks}")
        # restore original click
        driver.execute_script(
            """
            const inp=document.getElementById('project-file');
            if(inp && inp.__origClick){ inp.click = inp.__origClick; delete inp.__origClick; }
            """
        )
        print("✓ project-file.click restored")

        # ============================================================
        # 6. IMPORT saved JSON via project-file, confirm and state restored
        # ============================================================
        # ensure file exists abs
        abs_saved = os.path.abspath(json_path)
        assert os.path.exists(abs_saved)
        project_input = WebDriverWait(driver,TIMEOUT).until(EC.presence_of_element_located((By.ID,"project-file")))
        # hidden input: make interactable via JS? send_keys should work even hidden, but ensure not disabled
        driver.execute_script("document.getElementById('project-file').removeAttribute('hidden'); document.getElementById('project-file').style.display='block';")
        project_input.send_keys(abs_saved)
        # importProject will show confirm "¿Abrir este proyecto?"
        WebDriverWait(driver,TIMEOUT).until(lambda d: d.execute_script("return document.getElementById('confirm-dialog').open===true"), message="confirm-dialog no abrió tras importar JSON")
        import_title = driver.execute_script("return document.getElementById('confirm-title').textContent")
        assert "Abrir este proyecto" in import_title, f"confirm title import inesperado: {import_title}"
        print(f"✓ import via project-file → confirm '{import_title}'")
        # confirm
        imp_ok = WebDriverWait(driver,TIMEOUT).until(EC.element_to_be_clickable((By.ID,"confirm-ok")))
        real_click(driver, imp_ok)
        WebDriverWait(driver,TIMEOUT).until(lambda d: not d.execute_script("return document.getElementById('confirm-dialog').open"))
        # wait state restored to saved_data
        wait_state(driver, "window.PLACTSStudio.getState().speakers.length===2", msg="import state speakers no 2")
        st_imported = get_state(driver)
        assert len(st_imported["speakers"])==2, f"tras import esperado 2 speakers got {len(st_imported['speakers'])}"
        # title should match saved
        assert st_imported["event"]["title"]==saved_title, f"tras import title esperado '{saved_title}' got '{st_imported['event']['title']}'"
        # deeper: compare event json
        assert st_imported["event"]["subtitle"]==saved_data["event"]["subtitle"]
        print(f"✓ import saved JSON confirm → state restored speakers=2 title='{st_imported['event']['title'][:30]}'")

        # ============================================================
        # 7. Ctrl/Cmd+S download JSON
        # ============================================================
        before_json2 = _pre_files("*.json")
        # focus body
        driver.execute_script("document.body.focus();")
        time.sleep(0.2)
        body = driver.find_element(By.TAG_NAME,"body")
        is_mac = driver.execute_script("return (navigator.platform||'').toLowerCase().includes('mac')")
        mod = Keys.COMMAND if is_mac else Keys.CONTROL
        # send Ctrl+S
        body.send_keys(mod + "s")
        time.sleep(0.3)
        body.send_keys(Keys.NULL)
        json_path2, json_sz2 = _wait_new_file("*.json", before_json2, "Ctrl/Cmd+S download", timeout=10, min_size=50)
        assert json_path2.lower().endswith(".json")
        with open(json_path2,"r",encoding="utf-8") as f:
            data2 = json.load(f)
        assert len(data2["speakers"])==2, f"Ctrl+S JSON speakers esperado 2 got {len(data2['speakers'])}"
        print(f"✓ Ctrl/Cmd+S → download JSON ok: {Path(json_path2).name} ({json_sz2} bytes)")

        # ============================================================
        # 8. SCREENSHOT 40-project.png
        # ============================================================
        SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(SCREENSHOT))
        assert SCREENSHOT.exists() and SCREENSHOT.stat().st_size>0, f"screenshot no creado en {SCREENSHOT}"
        print(f"✓ screenshot {SCREENSHOT} ({SCREENSHOT.stat().st_size} bytes)")

        # ============================================================
        # 9. CONSOLE no SEVERE
        # ============================================================
        assert_no_severe_logs(driver)
        print("✓ consola sin SEVERE")

        total=time.time()-start_all
        print(f"\n=== PROJECT ACTIONS E2E OK === total {total:.2f}s")
        print(f"  downloads: {DOWNLOAD_DIR} jsons={[p.name for p in DOWNLOAD_DIR.glob('*.json')]}")
        # py_compile self
        py_compile.compile(str(Path(__file__)), doraise=True)
        print(f"✓ py_compile ok {Path(__file__).name}")

    except Exception as e:
        print("\n--- PROJECT ACTIONS E2E FAILURE ---", file=sys.stderr)
        traceback.print_exc()
        try:
            if driver:
                SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
                fail_path = SCREENSHOT.parent / "failure-40-project.png"
                driver.save_screenshot(str(fail_path))
                print(f"screenshot fallo en {fail_path}", file=sys.stderr)
                try:
                    with open(SCREENSHOT.parent / "failure-40-project.html","w",encoding="utf-8") as f:
                        f.write(driver.page_source)
                except Exception:
                    pass
        except Exception as se:
            print(f"no se pudo guardar screenshot fallo: {se}", file=sys.stderr)
        raise AssertionError(f"project_actions_e2e fallo: {e}") from e
    finally:
        try:
            if driver:
                driver.quit()
        except Exception:
            pass

def test_project_actions_e2e():
    """Entry para pytest."""
    run()

if __name__=="__main__":
    run()
