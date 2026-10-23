"""PROPOSED contract checks and a synthetic-only file roundtrip, never annotation."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import struct

from workspace_paths import REPOSITORY, load_local_config


def transform_point(point, transform, inverse=False):
    x0, y0, _, _ = transform["crop_xyxy"]
    sx, sy = transform["scale_xy"]
    px, py = transform["padding_left_top"]
    if sx <= 0 or sy <= 0:
        raise ValueError("Scales must be positive")
    x, y = point
    return ((x - px) / sx + x0, (y - py) / sy + y0) if inverse else (
        (x - x0) * sx + px, (y - y0) * sy + py)


def validate_contract(doc, mask_sizes=None):
    """Check references/states; this is not a GUI format or annotation-quality test."""
    width, height = doc["image"]["width"], doc["image"]["height"]
    if type(width) is not int or type(height) is not int or min(width, height) <= 0:
        raise ValueError("Original dimensions must be positive integers")
    people = {p["person_id"]: p for p in doc["persons"]}
    regions = {p["region_id"]: p for p in doc["regions"]}
    if len(people) != len(doc["persons"]) or len(regions) != len(doc["regions"]):
        raise ValueError("Image-local IDs must be unique")
    for person in people.values():
        if person["person_id"] == person.get("temporary_locator_ref"):
            raise ValueError("Temporary locator is not a Person ID")
    for region in regions.values():
        owner, state = region["person_id"], region["ownership_state"]
        if state not in {"known", "unknown"}:
            raise ValueError("Ownership state is not part of the proposed contract")
        if state == "known" and owner not in people:
            raise ValueError("Known owner must reference an image-local person")
        if state == "unknown" and owner is not None:
            raise ValueError("Unresolved owner must not become a guessed person")
    for attribute in doc["attributes"]:
        if attribute["region_ref"] not in regions:
            raise ValueError("Attribute region is missing")
        if attribute["value_state"] in {"unknown", "unobservable", "not_applicable"}:
            if attribute["value"] is not None or not attribute["reason"]:
                raise ValueError("Unknown/unobservable values retain null and a reason")
        elif attribute["value_state"] != "known" or attribute["value"] is None:
            raise ValueError("Known values must be explicit; unsupported states are rejected")
    evaluation = doc["evaluation"]
    if evaluation["disposition"] == "ignore" and not evaluation["policy_ref"]:
        raise ValueError("Ignore requires an explicit policy reference")
    for size in (mask_sizes or {}).values():
        if tuple(size) != (width, height):
            raise ValueError("Canonical mask dimensions differ from the original image")
    return True


def safe_output(path, config, repository=REPOSITORY):
    target = Path(path).resolve()
    if (not target.is_relative_to(Path(config["work_root"]).resolve())
            or target.is_relative_to(Path(config["dataset_root"]).resolve())
            or target.is_relative_to(Path(repository).resolve()) or target.exists()):
        raise ValueError("Use a fresh output directory inside external work_root")
    return target


def synthetic_roundtrip(output):
    """Exercise existing Pillow PNG and stdlib JSON only, using invented data."""
    from PIL import Image, ImageOps

    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    width, height = 12, 10
    semantic, instance, validity = [], [], []
    for y in range(height):
        for x in range(width):
            a, b = 2 <= x < 5 and 2 <= y < 8, 7 <= x < 10 and 3 <= y < 9
            semantic.append(17 if a else 42 if b else 0)
            instance.append(301 if a else 4097 if b else 0)
            validity.append(2 if (x, y) == (2, 2) else 3 if (x, y) == (8, 4) else 1)
    mask_values = {"semantic.png": semantic, "instance.png": instance, "validity.png": validity}
    for name, values in mask_values.items():
        data = struct.pack("<" + "H" * len(values), *values)
        Image.frombytes("I;16", (width, height), data).save(output / name)
    Image.new("RGB", (width, height), (70, 80, 90)).save(output / "synthetic_image.png")
    doc = {
        "artifact_type": "SYNTHETIC_ONLY_NOT_REAL_ANNOTATION",
        "schema_version": "0.1-PROPOSED", "guideline_version": "0.1-PROPOSED",
        "annotation_revision": "synthetic-r1",
        "image": {"image_id": "DEMO_IMAGE", "width": width, "height": height,
                  "coordinate_frame": "original_encoded_pixels", "orientation": 1},
        "persons": [{"person_id": "DEMO_PERSON_A", "raster_instance_id": 301,
                     "temporary_locator_ref": "DEMO_LOCATOR_LEFT"},
                    {"person_id": "DEMO_PERSON_B", "raster_instance_id": 4097,
                     "temporary_locator_ref": "DEMO_LOCATOR_RIGHT"}],
        "regions": [{"region_id": "DEMO_REGION_A", "person_id": "DEMO_PERSON_A",
                     "ownership_state": "known", "semantic_id_test_only": 17},
                    {"region_id": "DEMO_REGION_B", "person_id": "DEMO_PERSON_B",
                     "ownership_state": "known", "semantic_id_test_only": 42},
                    {"region_id": "DEMO_UNRESOLVED", "person_id": None,
                     "ownership_state": "unknown", "semantic_id_test_only": None}],
        "attributes": [{"region_ref": "DEMO_REGION_A", "name": "color",
                        "value_state": "unobservable", "value": None, "reason": "synthetic occlusion"},
                       {"region_ref": "DEMO_REGION_B", "name": "color",
                        "value_state": "known", "value": "DEMO_COLOR_A", "reason": None}],
        "annotation_state": "draft", "presence": "unknown", "observability": "partial",
        "evaluation": {"disposition": "ignore", "policy_ref": "synthetic-policy-only"},
        "validity_codes_test_only": {"1": "known", "2": "unknown", "3": "ignore"},
        "zero_meaning_test_only": "outside this support, not an automatic background decision",
        "display": {"palette_rgb": {"17": [0, 255, 0], "42": [255, 0, 255]}},
        "provenance": {"source": "generated synthetic fixture", "not_company_data": True}}
    validate_contract(doc)
    (output / "export.json").write_text(json.dumps(doc, indent=2) + "\n")
    restored = json.loads((output / "export.json").read_text())
    with Image.open(output / "synthetic_image.png") as image:
        image.load()
        if image.size != (restored["image"]["width"], restored["image"]["height"]):
            raise AssertionError("Image dimensions differ from contract dimensions")
    sizes = {}
    for name, expected in mask_values.items():
        with Image.open(output / name) as im:
            im.load()
            sizes[name] = im.size
            actual = list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") else list(im.getdata())
            if actual != expected:
                raise AssertionError("PNG IDs or validity values were lost")
    validate_contract(restored, sizes)
    assert restored == doc and restored["regions"][2]["person_id"] is None
    transform = {"crop_xyxy": [2, 1, 10, 9], "scale_xy": [2, 3], "padding_left_top": [3, 4]}
    for point in [(2, 1), (10, 9), (5.5, 4.5)]:
        back = transform_point(transform_point(point, transform), transform, inverse=True)
        assert all(math.isclose(a, b, abs_tol=1e-9) for a, b in zip(point, back))
    with Image.open(output / "semantic.png") as im:
        view = ImageOps.expand(im.crop((2, 1, 10, 9)).resize((16, 24), Image.Resampling.NEAREST),
                               border=(3, 4, 2, 1), fill=0)
        values = list(view.get_flattened_data()) if hasattr(view, "get_flattened_data") else list(view.getdata())
        assert set(values) <= set(semantic)
        view.save(output / "synthetic_label_display.png")
    # A downsample can lose a thin region; coordinate inversion cannot restore its pixels.
    thin = Image.new("I", (8, 8), 0)
    thin.putpixel((0, 0), 17)
    lost = thin.resize((1, 1), Image.Resampling.NEAREST)
    assert lost.getpixel((0, 0)) == 0
    changed = copy.deepcopy(restored)
    semantic_hash = hashlib.sha256((output / "semantic.png").read_bytes()).hexdigest()
    changed["display"]["palette_rgb"]["17"] = [255, 255, 0]
    assert changed["attributes"] == restored["attributes"]
    for name, record in [("display_before.png", restored), ("display_after.png", changed)]:
        rgb = Image.new("RGB", (width, height))
        rgb.putdata([tuple(record["display"]["palette_rgb"].get(str(v), [0, 0, 0])) for v in semantic])
        rgb.save(output / name)
    assert (output / "display_before.png").read_bytes() != (output / "display_after.png").read_bytes()
    assert semantic_hash == hashlib.sha256((output / "semantic.png").read_bytes()).hexdigest()
    report = {"result": "PASS", "artifact_type": "SYNTHETIC_ONLY_NOT_REAL_ANNOTATION",
              "png_dimensions_match": True, "uint16_ids_preserved": [301, 4097],
              "json_ownership_and_unknown_states_preserved": True,
              "validity_unknown_ignore_preserved": True,
              "crop_resize_padding_point_inverse_passed": True,
              "nearest_neighbor_did_not_invent_ids": True,
              "display_palette_did_not_change_clothing_attributes": True,
              "lossy_downsample_pixel_recovery_claimed": False,
              "annotation_GUI_export_import_tested": False,
              "annotation_quality_verified": False}
    (output / "SYNTHETIC_CHECK_REPORT.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-check", action="store_true", required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = load_local_config(args.config)
    target = safe_output(args.output, config)
    print(json.dumps(synthetic_roundtrip(target), indent=2))


if __name__ == "__main__":
    main()
