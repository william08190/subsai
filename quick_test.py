#!/usr/bin/env python
import sys
sys.path.insert(0, "/subsai/src")
from subsai.video_uniqueness import get_resolution_scale_params

print("="*70)
print("Test: Shortest Side Scaling Fix")
print("="*70 + "\n")

test_cases = [
    (606, 1080, 1080, "User reported 606x1080"),
    (1080, 1920, 1080, "Already 1080x1920"),
    (1920, 1080, 1080, "1920x1080 horizontal"),
    (720, 1280, 1080, "720x1280 vertical"),
]

for width, height, min_res, desc in test_cases:
    print("Test: " + desc)
    print("  Input: {}x{}, min_resolution: {}px".format(width, height, min_res))

    params = get_resolution_scale_params(width, height, min_res)
    output_min = min(params['target_width'], params['target_height'])

    print("  Need scale: {}".format(params['need_scale']))
    print("  Output: {}x{}".format(params['target_width'], params['target_height']))
    print("  Output min side: {}px".format(output_min))

    passed = False
    if params['need_scale'] and output_min >= min_res - 2:
        passed = True
    elif not params['need_scale'] and min(width, height) >= min_res:
        passed = True

    print("  Result: " + ("PASS" if passed else "FAIL"))
    print()

print("="*70)
print("Test completed!")
