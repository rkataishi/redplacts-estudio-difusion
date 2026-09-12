#!/usr/bin/env python3
"""Captura reproducible de la geometría inicial de la auditoría 01."""

import json
import sys
import time
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.ui_smoke import BASE_URL, TIMEOUT, _driver, assert_no_severe_logs, real_click


OUTPUT = ROOT / ".audit" / "baseline"
MEASUREMENTS = ROOT / ".audit" / "measurements" / "baseline.json"
VIEWPORTS = [(1920, 1080), (1440, 900), (1280, 757), (768, 1024), (390, 844)]
TABS = ["content", "people", "images", "meeting", "share"]


def ready(driver):
    driver.get(BASE_URL)
    WebDriverWait(driver, TIMEOUT).until(
        lambda d: d.execute_script("return !!(window.PLACTSStudio && window.PLACTSStudio.whenReady)")
    )
    driver.execute_async_script(
        "const done=arguments[arguments.length-1]; window.PLACTSStudio.whenReady().then(()=>done(true));"
    )


def clear_state(driver):
    driver.get(BASE_URL)
    driver.execute_script("localStorage.clear(); sessionStorage.clear();")
    driver.execute_async_script(
        """
        const done=arguments[arguments.length-1];
        (async()=>{
          if(indexedDB.databases){for(const db of await indexedDB.databases()) indexedDB.deleteDatabase(db.name)}
          done(true);
        })();
        """
    )
    ready(driver)


def geometry(driver, label):
    return driver.execute_script(
        """
        const label=arguments[0];
        const rect=(sel)=>{
          const el=document.querySelector(sel); if(!el) return null;
          const r=el.getBoundingClientRect();
          return {top:r.top,right:r.right,bottom:r.bottom,left:r.left,width:r.width,height:r.height};
        };
        const scroll=document.querySelector('#form-scroll');
        return {
          label,
          viewport:{width:innerWidth,height:innerHeight,dpr:devicePixelRatio},
          document:{scrollWidth:document.documentElement.scrollWidth,scrollHeight:document.documentElement.scrollHeight},
          editor:rect('.editor'), formScroll:scroll ? {rect:rect('#form-scroll'),scrollTop:scroll.scrollTop,scrollHeight:scroll.scrollHeight,clientHeight:scroll.clientHeight}:null,
          editorFoot:rect('.editor-foot'), compileButton:rect('#compile-button'),
          stage:rect('#stage'), stageTop:rect('.stage-top'), previewTitle:rect('#collection-title'), resolution:rect('#export-scale'),
          canvas:rect('.poster-card.is-selected canvas'), overview:rect('#overview'), overviewGrid:rect('#overview-grid'),
          selectedVariant:document.querySelector('[data-variant-select][aria-pressed="true"]')?.dataset.variantSelect ?? null,
          selectedTab:document.querySelector('.step[aria-selected="true"]')?.id ?? null,
          speakerCount:window.PLACTSStudio.getState().speakers.length
        };
        """,
        label,
    )


def screenshot(driver, name, measurements):
    path = OUTPUT / f"{name}.png"
    driver.save_screenshot(str(path))
    assert path.exists() and path.stat().st_size > 0
    measurements.append(geometry(driver, name))


def set_viewport(driver, width, height):
    driver.execute_cdp_cmd(
        "Emulation.setDeviceMetricsOverride",
        {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": width <= 710},
    )
    time.sleep(0.25)


def load_demo(driver):
    real_click(driver, WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.ID, "demo-button"))))
    real_click(driver, WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-demo="2"]'))))
    time.sleep(0.3)
    if driver.execute_script("return document.getElementById('confirm-dialog').open"):
        real_click(driver, driver.find_element(By.ID, "confirm-ok"))
    WebDriverWait(driver, TIMEOUT).until(
        lambda d: d.execute_script("return window.PLACTSStudio.getState().speakers.length===2")
    )


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    MEASUREMENTS.parent.mkdir(parents=True, exist_ok=True)
    measurements = []
    driver = _driver()
    try:
        clear_state(driver)
        for width, height in VIEWPORTS:
            set_viewport(driver, width, height)
            screenshot(driver, f"empty-{width}x{height}", measurements)

        set_viewport(driver, 1280, 757)
        load_demo(driver)
        for width, height in VIEWPORTS:
            set_viewport(driver, width, height)
            screenshot(driver, f"demo-{width}x{height}", measurements)

        set_viewport(driver, 1280, 757)
        for tab in TABS:
            real_click(driver, driver.find_element(By.ID, f"tab-{tab}"))
            driver.execute_script("document.getElementById('form-scroll').scrollTop=0")
            screenshot(driver, f"section-{tab}-1280x757", measurements)

        real_click(driver, driver.find_element(By.ID, "tab-people"))
        add = driver.find_element(By.ID, "add-speaker")
        while not add.get_attribute("disabled"):
            real_click(driver, add)
        driver.execute_script("document.getElementById('form-scroll').scrollTop=0")
        screenshot(driver, "people-max-top-1280x757", measurements)
        driver.execute_script("const el=document.getElementById('form-scroll'); el.scrollTop=el.scrollHeight")
        screenshot(driver, "people-max-bottom-1280x757", measurements)
        assert_no_severe_logs(driver)
    finally:
        driver.quit()

    MEASUREMENTS.write_text(json.dumps(measurements, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"baseline screenshots={len(measurements)} measurements={MEASUREMENTS}")


if __name__ == "__main__":
    run()
