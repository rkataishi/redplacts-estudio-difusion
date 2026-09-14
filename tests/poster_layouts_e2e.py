#!/usr/bin/env python3
"""Verify the 27 poster contracts through the public browser API."""

import sys
import time
from pathlib import Path

from selenium.webdriver.support.ui import WebDriverWait

try:
    from tests.ui_smoke import BASE_URL, _driver, assert_no_severe_logs
except ImportError:
    from ui_smoke import BASE_URL, _driver, assert_no_severe_logs


TIMEOUT = 20
CAPTURE_DIR = Path("/tmp/ui-e2e/poster-layouts")


def replace_with_example(driver, count):
    result = driver.execute_async_script(
        """
        const count = arguments[0];
        const done = arguments[arguments.length - 1];
        window.PLACTSStudio.replace(window.PLACTSStudio.makeExample(count))
          .then(() => done(true))
          .catch(error => done('error:' + error.message));
        """,
        count,
    )
    assert result is True, result
    WebDriverWait(driver, TIMEOUT).until(
        lambda current: len(current.execute_script("return window.PLACTSStudio.getPlans()")) == 9
    )


def render_options(driver, selected=3, social_photos=True, qr=False, opacity=32, background=True, hero=False, url="https://redplacts.org/encuentro"):
    result = driver.execute_async_script(
        """
        const [selected, socialPhotos, qr, opacity, background, hero, url] = arguments;
        const done = arguments[arguments.length - 1];
        (async () => {
          const state = PLACTSStudio.makeExample(3);
          const source = document.createElement('canvas');
          source.width = source.height = 16;
          const sourceCtx = source.getContext('2d');
          sourceCtx.fillStyle = '#e21c62'; sourceCtx.fillRect(0, 0, 8, 16);
          sourceCtx.fillStyle = '#18a76b'; sourceCtx.fillRect(8, 0, 8, 16);
          const image = {data: source.toDataURL('image/png'), name: 'contract.png', width: 16, height: 16, crop: {x: 50, y: 50, zoom: 1}};
          state.images.background = background ? image : null;
          state.images.hero = hero ? image : null;
          state.speakers.forEach(person => { person.photo = image; person.crop = {x: 50, y: 50, zoom: 1}; });
          state.options.bgOpacity = opacity;
          state.options.socialPhotos = socialPhotos;
          state.options.showQR = qr;
          state.options.socialQR = qr;
          state.event.url = url;
          state.event.urlLabel = '';
          await PLACTSStudio.replace(state);
          document.querySelector(`[data-variant-select="${selected}"]`).click();
          const canvas = document.querySelector('.poster-card.is-selected canvas');
          const pixels = canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height).data;
          let hash = 2166136261;
          for (let i = 0; i < pixels.length; i += 388) hash = Math.imul(hash ^ pixels[i], 16777619) >>> 0;
          done({hash, plans: PLACTSStudio.getPlans()});
        })().catch(error => done({error: error.message}));
        """,
        selected,
        social_photos,
        qr,
        opacity,
        background,
        hero,
        url,
    )
    assert not result.get("error"), result
    return result


def run():
    driver = _driver()
    started = time.time()
    signatures = {index: [] for index in range(9)}
    geometries = {}
    try:
        CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
        driver.get(BASE_URL)
        WebDriverWait(driver, TIMEOUT).until(
            lambda current: current.execute_script(
                "return !!(window.PLACTSStudio && window.PLACTSStudio.whenReady)"
            )
        )
        driver.execute_async_script(
            "const done=arguments[arguments.length-1];"
            "window.PLACTSStudio.whenReady().then(()=>done(true)).catch(error=>done('error:'+error.message));"
        )
        assert len(driver.execute_script("return window.PLACTSStudio.makeExample().speakers")) == 3

        for count in (2, 3, 4):
            replace_with_example(driver, count)
            plans = driver.execute_script("return window.PLACTSStudio.getPlans()")
            assert len(plans) == 9
            for index, plan in enumerate(plans):
                assert plan["participants"] == count, (count, index, plan)
                assert plan["valid"], (count, index, plan)
                assert not plan["issues"], (count, index, plan["issues"])
                signature = plan.get("composition")
                assert signature, (count, index, "missing composition")
                signatures[index].append(signature)
                cards = [item for item in plan["audit"] if item["label"].startswith("speaker-card-")]
                assert len(cards) == count, (count, index, len(cards))
                sizes = {(round(item["w"], 3), round(item["h"], 3)) for item in cards}
                assert len(sizes) == 1, (count, index, sizes)
                geometries[count, index] = tuple(
                    (round(item["x"], 3), round(item["y"], 3), round(item["w"], 3), round(item["h"], 3))
                    for item in cards
                )
            driver.save_screenshot(str(CAPTURE_DIR / f"{count}-speakers.png"))

        for index, values in signatures.items():
            assert len(set(values)) == 3, (index, values)
        for count in (2, 3, 4):
            assert geometries[count, 5] != geometries[count, 8], (count, "variants 06 and 09 match")

        photos_on = render_options(driver, social_photos=True)
        photos_off = render_options(driver, social_photos=False)
        assert sum(item["label"].startswith("speaker-photo-") for item in photos_on["plans"][3]["audit"]) == 3
        assert not any(item["label"].startswith("speaker-photo-") for item in photos_off["plans"][3]["audit"])
        assert photos_on["hash"] != photos_off["hash"]

        qr_on = render_options(driver, qr=True)
        assert any(item["label"] == "meeting-qr" for item in qr_on["plans"][0]["audit"])
        assert any(item["label"] == "meeting-qr" for item in qr_on["plans"][3]["audit"])

        background_35 = render_options(driver, selected=0, opacity=35)
        background_60 = render_options(driver, selected=0, opacity=60)
        assert background_35["hash"] != background_60["hash"]

        background_0 = render_options(driver, selected=0, opacity=0)
        no_background = render_options(driver, selected=0, background=False)
        assert background_0["hash"] == no_background["hash"]

        long_url = "https://redplacts.org/" + "encuentro-federal-de-ciencia-y-tecnologia/" * 4
        long_url_qr = render_options(driver, qr=True, url=long_url)
        assert all(plan["valid"] and not plan["issues"] for plan in long_url_qr["plans"])

        hero_off = render_options(driver, selected=0, hero=False)
        hero_on = render_options(driver, selected=0, hero=True)
        assert not any(item["label"] == "hero-image" for item in hero_off["plans"][0]["audit"])
        assert any(item["label"] == "hero-image" for item in hero_on["plans"][0]["audit"])
        assert hero_off["hash"] != hero_on["hash"]
        assert next(item for item in hero_off["plans"][8]["audit"] if item["label"] == "event-title")["y"] == 150
        assert next(item for item in hero_on["plans"][8]["audit"] if item["label"] == "event-title")["y"] == 525

        assert_no_severe_logs(driver)
        print(f"POSTER_LAYOUTS_OK states=27 variants=9 elapsed={time.time()-started:.2f}s")
    finally:
        driver.quit()


if __name__ == "__main__":
    try:
        run()
    except Exception as error:
        print(f"POSTER_LAYOUTS_FAIL {error}", file=sys.stderr)
        raise
