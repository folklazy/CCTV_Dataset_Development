"""Measure visible mask extent; never infer camera distance or annotation quality."""
import argparse
import hashlib
import json
from pathlib import Path


def measure_scale(path, expected_size, evidence_stage):
    from PIL import Image
    if evidence_stage not in {'draft', 'human_reviewed'}:
        raise ValueError('Declare draft or human_reviewed provenance')
    if len(expected_size) != 2 or any(type(v) is not int or v <= 0 for v in expected_size):
        raise ValueError('Expected original image dimensions must be positive integers')
    data = Path(path).read_bytes()
    import io
    with Image.open(io.BytesIO(data)) as im:
        im.load()
        if im.mode not in {'1', 'L'} or im.size != tuple(expected_size):
            raise ValueError('Require original-grid single-channel binary mask')
        values = {value for count, value in im.getcolors(maxcolors=256)}
        if not values.issubset({0, 1}) and not values.issubset({0, 255}):
            raise ValueError('Reject multiclass or antialiased masks')
        binary = im.point(lambda x: 255 if x else 0).convert('L')
        area = binary.histogram()[255]
        bbox = binary.getbbox()
    width, height = expected_size
    bw, bh = (bbox[2]-bbox[0], bbox[3]-bbox[1]) if bbox else (None, None)
    return {'schema': 'visible-scale-1', 'mask_sha256': hashlib.sha256(data).hexdigest(),
            'evidence_stage': evidence_stage, 'image_size_wh': [width, height],
            'visible_area_px': area, 'visible_area_fraction': area/(width*height),
            'visible_bbox_xyxy_exclusive': list(bbox) if bbox else None,
            'bbox_width_px': bw, 'bbox_height_px': bh,
            'bbox_width_fraction': bw/width if bbox else None,
            'bbox_height_fraction': bh/height if bbox else None,
            'extent_state': 'measured_visible_support' if bbox else 'empty_support_not_absence',
            'distance_m': None, 'distance_basis': 'not_calibrated',
            'acceptance_granted_by_measurement': False}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mask', type=Path, required=True)
    p.add_argument('--width', type=int, required=True)
    p.add_argument('--height', type=int, required=True)
    p.add_argument('--stage', choices=['draft','human_reviewed'], required=True)
    a = p.parse_args()
    print(json.dumps(measure_scale(a.mask, [a.width,a.height], a.stage), allow_nan=False))
