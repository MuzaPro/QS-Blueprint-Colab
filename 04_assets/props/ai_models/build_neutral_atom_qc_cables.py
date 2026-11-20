"""In-between version: the elegant neutral-atom QC plus only the cable spaghetti mess.

Run:  blender -b --factory-startup --python build_neutral_atom_qc_cables.py
Reads neutral_atom_qc.blend (elegant materials, user's cameras/lights/logo/bevels),
writes neutral_atom_qc_cables.blend. Uses the fugly builder with PARTS = cables only:
cable bundles, zip ties, power strip, plus the open rack door and the ajar sliding door
the bundles exit through. New objects live in collection NAQC_Cable_Mess.
"""
DIR = r"C:\Users\mrgav\Documents\GitHub\QS-Blueprint-Colab\04_assets\props\ai_models"
PARTS = ("cables",)
COLL_NAME = "NAQC_Cable_Mess"
OUT = globals().get("OUT", DIR + r"\neutral_atom_qc_cables.blend")
SAVE = globals().get("SAVE", True)
exec(open(DIR + r"\build_neutral_atom_qc_fugly.py").read())
