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
        const state = window.PLACTSStudio.makeExample(count);
        const source = document.createElement('canvas');
        source.width = source.height = 16;
        const sourceCtx = source.getContext('2d');
        sourceCtx.fillStyle = '#e21c62'; sourceCtx.fillRect(0, 0, 8, 16);
        sourceCtx.fillStyle = '#18a76b'; sourceCtx.fillRect(8, 0, 8, 16);
        const image = {data: source.toDataURL('image/png'), name: 'speaker.png', width: 16, height: 16, crop: {x: 50, y: 50, zoom: 1}};
        state.speakers.forEach(person => { person.photo = image; person.crop = {x: 50, y: 50, zoom: 1}; });
        window.PLACTSStudio.replace(state)
          .then(() => done(true))
          .catch(error => done('error:' + error.message));
        """,
        count,
    )
    assert result is True, result
    WebDriverWait(driver, TIMEOUT).until(
        lambda current: len(current.execute_script("return window.PLACTSStudio.getPlans()")) == 9
    )


def render_options(driver, selected=3, social_photos=True, qr=False, opacity=32, background=True, hero=False, url="https://redplacts.org/encuentro", box_group="speaker", box_style="transparent", box_color="default", accent="#0062ad", font_scale=100, type_scale=115):
    result = driver.execute_async_script(
        """
        const [selected, socialPhotos, qr, opacity, background, hero, url, boxGroup, boxStyle, boxColor, accent, fontScale, typeScale] = arguments;
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
          state.options.typeScale = typeScale;
          state.options.boxes[boxGroup] = {style: boxStyle, color: boxColor, accent, fontScale};
          state.event.url = url;
          state.event.urlLabel = '';
          await PLACTSStudio.replace(state);
          document.querySelector(`[data-variant-select="${selected}"]`).click();
          const canvas = document.querySelector('.poster-card.is-selected canvas');
          const pixels = canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height).data;
          let hash = 2166136261;
          for (let i = 0; i < pixels.length; i += 388) {
            hash = Math.imul(hash ^ pixels[i], 16777619) >>> 0;
            hash = Math.imul(hash ^ pixels[i + 1], 16777619) >>> 0;
            hash = Math.imul(hash ^ pixels[i + 2], 16777619) >>> 0;
          }
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
        box_group,
        box_style,
        box_color,
        accent,
        font_scale,
        type_scale,
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
        assert driver.execute_script("return window.PLACTSStudio.makeExample().speakers.every(person => person.crop.y === 20)")
        assert driver.execute_script("const state=window.PLACTSStudio.makeExample();state.speakers.forEach(person=>delete person.crop);return window.PLACTSStudio.validateProject(state).speakers.every(person=>person.crop.y===20)")
        defaults = driver.execute_script("return window.PLACTSStudio.makeExample().options")
        assert defaults["font"] == "Lato"
        assert defaults["typeScale"] == 115
        assert set(defaults["boxes"]) == {"title", "speaker", "moderator", "meeting"}

        def centered(items, top, height, tolerance=2):
            visible = [item for item in items if item.get("h")]
            group_top = min(item["y"] for item in visible)
            group_bottom = max(item["y"] + item["h"] for item in visible)
            return abs((group_top + group_bottom) / 2 - (top + height / 2)) <= tolerance

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
                text_sizes = [item["size"] for item in plan["audit"] if item.get("size")]
                assert text_sizes and min(text_sizes) >= 17, (count, index, min(text_sizes))
                labels = {item["label"]: item for item in plan["audit"]}
                assert labels["event-type"]["size"] >= 23
                assert labels["event-series"]["text"] == "ENCUENTROS VIRTUALES DE LA RED PLACTS"
                assert "website" not in labels
                assert "footer-logo" in labels
                assert all(f"footer-network-{i}" in labels and f"footer-handle-{i}" in labels for i in range(4))
                assert [(labels[f"footer-network-{i}"]["text"], labels[f"footer-handle-{i}"]["text"]) for i in range(4)] == [("Instagram", "@redplacts"), ("X", "@PlactsRed"), ("Facebook", "@redplacts"), ("YouTube", "@RedPLACTS")]
                meeting = labels["meeting-box"]
                assert centered([labels[name] for name in ("meeting-date", "meeting-time", "meeting-zone")], meeting["y"], meeting["h"])
                for speaker in range(count):
                    assert f"speaker-affiliation-{speaker}" in labels
                    card, photo = labels[f"speaker-card-{speaker}"], labels.get(f"speaker-photo-{speaker}")
                    content = [item for item in plan["audit"] if item["label"] in {f"speaker-name-{speaker}", f"speaker-affiliation-{speaker}", f"speaker-description-{speaker}"}]
                    text_top = photo["y"] + photo["h"] if photo and abs(photo["y"] - card["y"]) < 2 else card["y"]
                    assert centered(content, text_top, card["y"] + card["h"] - text_top, 3), (count, index, speaker, content, card, photo)
                if index == 0:
                    title = labels["event-title"]
                    assert title["h"] <= title["size"] * 1.08
                    assert title["size"] >= 66
                if index == 4:
                    assert all(labels[f"speaker-photo-{i}"]["h"] >= labels[f"speaker-card-{i}"]["h"] * .59 for i in range(count))
                if index == 5:
                    assert min(labels[f"speaker-name-{i}"]["size"] for i in range(count)) >= 24
                if index == 6:
                    assert labels["moderator-box"]["h"] >= 120
                    assert labels["mod-photo-0"]["h"] >= 52
                if index in (7, 8):
                    assert labels["title-box"]["w"] >= plan["width"] * .84
                if index == 8 and "hero-image" in labels:
                    assert labels["title-box"]["y"] < labels["hero-image"]["y"] + labels["hero-image"]["h"] / 2
                rows = {}
                for item in cards:
                    rows.setdefault(round(item["y"], 3), 0)
                    rows[round(item["y"], 3)] += 1
                if index in (3, 4, 6, 7) and count in (2, 3):
                    assert len(rows) == 1, (count, index, rows)
                if count == 4:
                    assert sorted(rows.values()) in ([2, 2], [4]), (count, index, rows)
                geometries[count, index] = tuple(
                    (round(item["x"], 3), round(item["y"], 3), round(item["w"], 3), round(item["h"], 3))
                    for item in cards
                )
            driver.save_screenshot(str(CAPTURE_DIR / f"{count}-speakers.png"))

        no_descriptions = driver.execute_async_script(
            """
            const done=arguments[arguments.length-1], state=PLACTSStudio.makeExample(3);
            state.speakers.forEach(person => person.description='');
            PLACTSStudio.replace(state).then(()=>done(PLACTSStudio.getPlans())).catch(error=>done({error:error.message}));
            """
        )
        assert not isinstance(no_descriptions, dict), no_descriptions
        for plan in no_descriptions:
            labels = {item["label"]: item for item in plan["audit"]}
            assert not any(label.startswith("speaker-description-") for label in labels)
            for speaker in range(3):
                card, photo = labels[f"speaker-card-{speaker}"], labels.get(f"speaker-photo-{speaker}")
                content = [labels[f"speaker-name-{speaker}"], labels[f"speaker-affiliation-{speaker}"]]
                text_top = photo["y"] + photo["h"] if photo and abs(photo["y"] - card["y"]) < 2 else card["y"]
                assert centered(content, text_top, card["y"] + card["h"] - text_top, 3)

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
        hero_title = next(item for item in hero_on["plans"][8]["audit"] if item["label"] == "title-box")
        hero_image = next(item for item in hero_on["plans"][8]["audit"] if item["label"] == "hero-image")
        assert hero_title["y"] < hero_image["y"] + hero_image["h"] / 2
        assert next(item for item in hero_off["plans"][8]["audit"] if item["label"] == "title-box")["y"] == 132

        box_hashes = {
            (style, color): render_options(driver, box_style=style, box_color=color)["hash"]
            for style in ("vibrant", "transparent", "gradient")
            for color in ("default", "dark", "accent")
        }
        assert len(set(box_hashes.values())) == 9, box_hashes
        accent_hashes = {
            accent: render_options(driver, box_color="accent", accent=accent)["hash"]
            for accent in ("#009542", "#0062ad", "#8b4c78")
        }
        assert len(set(accent_hashes.values())) == 3, accent_hashes
        for group in ("title", "speaker", "moderator", "meeting"):
            scaled = render_options(driver, box_group=group, font_scale=135)
            base = render_options(driver, box_group=group, font_scale=100)
            assert scaled["hash"] != base["hash"], group
            assert all(plan["valid"] and not plan["issues"] for plan in scaled["plans"]), group

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
