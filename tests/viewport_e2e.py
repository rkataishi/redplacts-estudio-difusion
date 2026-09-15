#!/usr/bin/env python3
"""Check responsive viewport occupancy and maximum undistorted poster size."""

from pathlib import Path
from selenium.webdriver.support.ui import WebDriverWait
from ui_smoke import BASE_URL, _driver, assert_no_severe_logs


def run():
    driver = _driver()
    captures = Path('/tmp/ui-e2e/viewport')
    captures.mkdir(parents=True, exist_ok=True)
    try:
        driver.get(BASE_URL)
        WebDriverWait(driver, 20).until(lambda d: d.execute_script('return !!window.PLACTSStudio'))
        driver.execute_async_script('const done=arguments[0];PLACTSStudio.whenReady().then(()=>PLACTSStudio.replace(PLACTSStudio.makeExample(3))).then(()=>done(true));')
        toggle = driver.execute_script("return document.querySelector('#redplacts-review-layer')?.shadowRoot.querySelector('.panel:not(.collapsed) #toggle')")
        if toggle:
            toggle.click()
        for width, height in [(1920, 1200), (900, 800), (970, 800), (1280, 650), (2560, 1440), (899, 800), (390, 844), (1920, 1080)]:
            driver.execute_cdp_cmd('Emulation.clearDeviceMetricsOverride', {})
            driver.set_window_size(width, height)
            if width < 500:
                driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {'width': width, 'height': height, 'deviceScaleFactor': 1, 'mobile': True})
            WebDriverWait(driver, 10).until(lambda d: d.execute_script('return innerWidth===arguments[0]', width))
            for variant in range(9):
                driver.find_element('css selector', f'[data-variant-select="{variant}"]').click()
                result = driver.execute_script('''
                  const rect=s=>{const r=document.querySelector(s).getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom}};
                  const frame=document.querySelector('.poster-frame'),style=getComputedStyle(frame),canvas=document.querySelector('.poster-frame canvas');
                  const availableW=frame.clientWidth-parseFloat(style.paddingLeft)-parseFloat(style.paddingRight);
                  const availableH=frame.clientHeight-parseFloat(style.paddingTop)-parseFloat(style.paddingBottom);
                  return {vw:innerWidth,vh:innerHeight,scrollW:document.documentElement.scrollWidth,workspace:rect('.workspace'),editor:rect('.editor'),stage:rect('.stage'),grid:rect('.poster-grid'),canvas:rect('.poster-frame canvas'),overview:rect('.overview'),ratio:canvas.width/canvas.height,maxW:Math.min(availableW,availableH*canvas.width/canvas.height)};
                ''')
                assert result['scrollW'] <= result['vw'] + 1, result
                canvas = result['canvas']
                assert abs(canvas['w']/canvas['h']-result['ratio']) < .01, result
                if width >= 900:
                    assert driver.execute_script("return [...document.querySelectorAll('.top-actions button')].every(e=>{const r=e.getBoundingClientRect();return r.x>=0&&r.right<=innerWidth+1})"), result
                    workspace, editor, stage = (result[key] for key in ('workspace', 'editor', 'stage'))
                    assert abs(workspace['x']) < 1 and abs(workspace['right']-result['vw']) < 1, result
                    assert abs(workspace['y']-60) < 1 and abs(workspace['bottom']-result['vh']) < 1, result
                    assert editor['right'] < stage['x'] and editor['bottom'] <= result['vh']+1, result
                    assert stage['bottom'] <= result['vh']+1 and result['overview']['bottom'] <= result['vh']+1, result
                    assert abs(result['grid']['w']-stage['w']) < 2, result
                    assert canvas['w'] > 0 and canvas['h'] > 0 and abs(canvas['w']-result['maxW']) < 3, result
                else:
                    assert result['stage']['y'] >= result['editor']['bottom']-1, result
            driver.save_screenshot(str(captures / f'{width}x{height}.png'))
        assert_no_severe_logs(driver)
        print('VIEWPORT_OK sizes=8 variants=9 resize=desktop-mobile-desktop')
    finally:
        driver.quit()


if __name__ == '__main__':
    run()
