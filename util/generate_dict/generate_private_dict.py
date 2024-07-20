"""Update the _private_dict.py file using data from the GDCM private dict."""

import xml.etree.ElementTree as ET
from urllib.request import urlopen
from pathlib import Path
from collections import defaultdict


GDCM_PRIVATE_DICT = (
    r"https://raw.githubusercontent.com/malaterre/GDCM/"
    r"master/Source/DataDictionary/privatedicts.xml"
)
PYDICOM_DICT_NAME = (
    "private_dictionaries: dict[str, dict[str, tuple[str, str, str, str]]]"
)
_PKG_DIRECTORY = Path(__file__).parent.parent.parent / "src" / "pydicom"
PYDICOM_DICT_FILENAME = _PKG_DIRECTORY / "_private_dict.py"
PYDICOM_DICT_DOCSTRING = """DICOM private dictionary auto-generated by generate_private_dict.py.

Data generated from GDCM project\'s private dictionary.

The outer dictionary key is the Private Creator name ("owner"), while the inner
dictionary key is a map of DICOM tag to (VR, VM, name, is_retired).
"""


# Manual additions for the autogenerated dict
ADDITIONS = {
    "ELSCINT1": {
        # Philips Access CT DICOM Conformance Statement (May 2015)
        "00E11021": ("DS", "1", "DLP"),
        "00E11037": ("DS", "1", "Total Saving Dose"),
        "00E1103E": ("IS", "1", "Split Is Dual Surview"),
        "00E11050": ("DS", "1", "Acquisition Duration"),
        "00E110C4": ("DS", "1", "Abs Bed Pos"),
        "01E11017": ("UI", "1", "ECG Reference UID"),
        "01E11026": ("CS", "1", "Phantom Type"),
        "01F11001": ("CS", "1", "Acquisition Type"),
        "01F11002": ("CS", "1", "Resolution"),
        "01F11004": ("CS", "1", "Angular Sampling"),
        "01F11008": ("DS", "1", "Scan Length"),
        "01F1100C": ("DS", "1", "Scanner Relative Center"),
        "01F1100E": ("FL", "1", "Recon Enhancement"),
        "01F11026": ("FD", "1", "Pitch"),
        "01F11027": ("DS", "1", "Rotation Time"),
        "01F11028": ("DS", "1", "Table Increment"),
        "01F11032": ("CS", "1", "View Convention"),
        "01F11033": ("DS", "1", "Cycle Time"),
        "01F11041": ("LO", "1", "Gating Delay"),
        "01F11045": ("IS", "1", "Initial Heart Rate"),
        "01F11049": ("DS", "1", "Planned mAs"),
        "01F1104B": ("SH", "1", "Collimation"),
        "01F1104C": ("SH", "1", "DOSE Right DOM"),
        "01F1104D": ("SH", "1", "Adaptive Filter"),
        "01F1104E": ("SH", "1", "Scan Type"),
        "01F7109B": ("IS", "1", "iDose Level"),
        "01F91001": ("LO", "1", "Mar Filter"),
        "01F91002": ("DS", "1", "Recon Increment"),
        "01F91003": ("DS", "1", "CTDIw"),
        "01F91004": ("IS", "1", "Couch Direction"),
        "01F91005": ("IS", "1", "Series No In Acquisition"),
        "01F91007": ("SH", "1", "Dose Right ACS"),
        "01F91008": ("DS", "1", "Left DMS Tmp Diff"),
        "01F91009": ("DS", "1", "Right DMS Tmp Diff"),
        "01F91010": ("LO", "1", "Dose Right Noise"),
        "01F91011": ("DS", "1", "Zero Position"),
        "01F91012": ("DS", "1", "Show Couch Position"),
        "01F91013": ("IS", "1", "Recon Mode"),
        "01F91014": ("DS", "1", "Water Size"),
        "01F91015": ("DS", "1", "Digital Tilt"),
        "01F91016": ("DS", "1", "Scan Arc"),
    },
}


def parse_private_docbook(doc_root):
    """Return a dict containing the private dictionary data"""
    # Excerpt for understanding formatting, from GDCM file taken 2023-09
    # <?xml version="1.0" encoding="UTF-8"?>
    # <dict>
    # <entry group="0021" element="0010" vr="SQ" vm="1" name="?" owner="SIEMENS MR FMRI"/>
    # ...first "xx" element
    # <entry owner="1.2.840.113663.1" group="0029" element="xx00" vr="US" vm="1" name="?"/>
    # ...last element
    # <entry owner="syngoDynamics" group="0021" element="xxae" vr="OB" vm="1" name="?"/>
    # </dict>

    entries = defaultdict(dict)
    for entry in root:
        owner = entry.attrib["owner"]
        tag = entry.attrib["group"].upper() + entry.attrib["element"].upper()
        tag = tag.replace("XX", "xx")
        vr = entry.attrib["vr"]
        vm = entry.attrib["vm"]
        name = entry.attrib["name"].replace("\\", "\\\\")  # escape backslashes

        # Convert unknown element names to 'Unknown'
        if name == "?":
            name = "Unknown"

        entries[owner][tag] = (vr, vm, name)

    return entries


def write_dict(fp, dict_name, dict_entries):
    """Write the `dict_name` dict to file `fp`.

    Dict Format
    -----------
    private_dictionaries = {
        'CREATOR_1' : {
            '0029xx00': ('US', '1', 'Unknown', ''),
            '0029xx01': ('US', '1', 'Unknown', ''),
        },
        ...
        'CREATOR_N' : {
            '0029xx00': ('US', '1', 'Unknown', ''),
            '0029xx01': ('US', '1', 'Unknown', ''),
        },
    }

    Parameters
    ----------
    fp : file
        The file to write the dict to.
    dict_name : str
        The name of the dict variable.
    attributes : list of str
        List of attributes of the dict entries.
    """
    fp.write(f"\n{dict_name} = {{\n")
    for owner in sorted(dict_entries):
        fp.write(f"    '{owner}': {{\n")
        for tag in sorted(dict_entries[owner]):
            vr, vm, name = dict_entries[owner][tag]
            quote = '"' if "'" in name else "'"
            fp.write(
                f"""        '{tag}': ('{vr}', '{vm}', {quote}{name}{quote}, ''),\n"""
            )
        fp.write("    },\n")
    fp.write("}\n")


if __name__ == "__main__":
    with urlopen(GDCM_PRIVATE_DICT) as response:
        root = ET.fromstring(response.read().decode("utf-8"))

    entries = parse_private_docbook(root)
    for creator in ADDITIONS:
        entries[creator].update(ADDITIONS[creator])

    with open(PYDICOM_DICT_FILENAME, "w", encoding="utf8") as py_file:
        py_file.write('"""' + PYDICOM_DICT_DOCSTRING + '"""')
        py_file.write("\n\n")
        write_dict(py_file, PYDICOM_DICT_NAME, entries)
