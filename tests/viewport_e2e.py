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
                  return {vw:innerWidth,vh:innerHeight,scrollW:document.documentElement.scrollWidth,workspace:rect('.workspace'),editor:rect('.editor'),stage:rect('.stage'),grid:rect('.poster-grid'),frame:rect('.poster-frame'),canvas:rect('.poster-frame canvas'),overview:rect('.overview'),ratio:canvas.width/canvas.height,maxW:availableW};
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
                    assert result['frame']['bottom'] <= result['vh']+1, result
                    reachable = driver.execute_script('''
                      const frame=document.querySelector('.poster-frame');frame.scrollTop=frame.scrollHeight;
                      return frame.querySelector('canvas').getBoundingClientRect().bottom <= frame.getBoundingClientRect().bottom+1;
                    ''')
                    assert reachable, result
                else:
                    assert result['stage']['y'] >= result['editor']['bottom']-1, result
            driver.save_screenshot(str(captures / f'{width}x{height}.png'))
        # Long content and enlarged fonts must not let warnings consume the preview.
        driver.set_window_size(970, 650)
        driver.execute_async_script('''
          const done=arguments[0],state=PLACTSStudio.makeExample(4);
          state.options.typeScale=140;state.options.boxes.title.fontScale=140;
          state.event.title='Una conversacion latinoamericana sobre ciencia tecnologia desarrollo y soberania';
          state.speakers.forEach(p=>p.description='Descripcion extensa institucional para evaluar la distribucion y legibilidad de los textos del encuentro');
          PLACTSStudio.replace(state).then(()=>done(true));
        ''')
        for variant in range(9):
            driver.find_element('css selector', f'[data-variant-select="{variant}"]').click()
            result = driver.execute_script('''
              const warnings=document.querySelector('#warnings'),frame=document.querySelector('.poster-frame'),style=getComputedStyle(frame),canvas=frame.querySelector('canvas');
              const r=canvas.getBoundingClientRect(),overview=document.querySelector('.overview').getBoundingClientRect();
              return {warningVisible:!warnings.hidden,warningH:warnings.getBoundingClientRect().height,scroll: warnings.scrollHeight>warnings.clientHeight,
                w:r.width,h:r.height,frameBottom:frame.getBoundingClientRect().bottom,ratio:canvas.width/canvas.height,overviewBottom:overview.bottom,vh:innerHeight,
                maxW:frame.clientWidth-parseFloat(style.paddingLeft)-parseFloat(style.paddingRight)};
            ''')
            assert result['warningVisible'] and result['warningH'] <= 81 and result['scroll'], result
            assert result['w'] > 0 and result['h'] > 50 and abs(result['w']-result['maxW']) < 3, result
            assert abs(result['w']/result['h']-result['ratio']) < .01, result
            assert result['frameBottom'] <= result['vh']+1 and result['overviewBottom'] <= result['vh']+1, result
        driver.save_screenshot(str(captures / '970x650-content-warnings.png'))
        assert_no_severe_logs(driver)
        print('VIEWPORT_OK sizes=8 variants=9 resize=desktop-mobile-desktop content-warnings=9')
    finally:
        driver.quit()


if __name__ == '__main__':
    run()
