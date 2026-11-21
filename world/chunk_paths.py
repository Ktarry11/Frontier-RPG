"""Where a baked map chunk really is on disk.

Every baked chunk used to be a JPEG (ground_<cx>_<cy>.jpg), except the sky maps, whose see-through chunks are WebP with
alpha. On 21 Nov 2026 every opaque chunk was converted to WebP too (Kyle: "how is this 2.4gb....can we clean up some old
useless bloat"; tools/convert_chunks_webp.py), which took about a third off the maps. The zone modules still name their
chunks ground_<cx>_<cy>.jpg in a hundred places, so everything that registers or checks a chunk goes through here and
gets whichever file actually exists: .webp, .jpg or .png. If a rebake leaves two side by side, the newer one wins.
"""
import os

EXTS = (".webp", ".jpg", ".png")


def _variants(path):
    stem, _ext = os.path.splitext(str(path))
    return [stem + e for e in EXTS]


def resolve(path):
    """The chunk file that exists for `path`, whatever extension it was named with (newest if there are several);
    `path` unchanged if none does."""
    found = [p for p in _variants(path) if os.path.exists(p)]
    if not found:
        return str(path)
    if len(found) == 1:
        return found[0]
    return max(found, key=os.path.getmtime)


def exists(path):
    """True if the chunk exists under any of its extensions."""
    return any(os.path.exists(p) for p in _variants(path))
