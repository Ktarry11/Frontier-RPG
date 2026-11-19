"""Wave 2 recruit text: the fields each Wave 1 profile changed, from tools/wave2/<recruit_id>.json.

Applied last by tools/rewrite_recruits.py, so it overlays every older batch field by field.
"""
from tools.wave2_text import recruit_text

BATCH = recruit_text()
