from io import BytesIO
import pdfplumber
import re
import pandas as pd

EPIC_RE = re.compile(r"^[A-Z]{3}\d{7}$")


def extract_lines_from_bytes(file_bytes: bytes):
    lines = []
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for raw_line in text.splitlines():
                line = raw_line.strip()
                if line:
                    lines.append(line)
    return lines


# def extract_lines_from_bytes(file_bytes: bytes) -> list[str]:
#     lines: list[str] = []
#     with pdfplumber.open(file_bytes) as pdf:
#         for page in pdf.pages:
#             text = page.extract_text() or ""
#             for raw_line in text.splitlines():
#                 line = raw_line.strip()
#                 if line:
#                     lines.append(line)
#     return lines


def is_serial(line: str) -> bool:
    return re.fullmatch(r"\d+", line) is not None


def is_epic(line: str) -> bool:
    return EPIC_RE.fullmatch(line) is not None


def parse_part_from_bytes(
    file_bytes: bytes, part_no: int, ac_no: int = 14, section_no: int = 1
):
    lines = extract_lines_from_bytes(file_bytes)
    voters = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Serial number
        if is_serial(line):
            serial_no = int(line)
            epic_no = None
            block = []

            # Find EPIC
            j = i + 1
            while j < len(lines) and not is_epic(lines[j]):
                if is_serial(lines[j]):
                    break
                j += 1

            if j < len(lines) and is_epic(lines[j]):
                epic_no = lines[j]
                j += 1

            # Collect block
            while j < len(lines) and not is_serial(lines[j]):
                block.append(lines[j])
                j += 1

            # Extract fields
            name = None
            relation = None
            house_no = None
            age = None
            gender = None

            for bl in block:
                bl = bl.strip()

                if bl.startswith("ਨਾਮ"):
                    name = bl.replace("ਨਾਮ", "").strip()

                if bl.startswith("ਪਿਤਾ") or bl.startswith("ਪਤੀ"):
                    relation = bl.split(" ", 1)[-1].strip()

                if "ਮਕਾਨ" in bl:
                    house_no = bl.split(" ", 1)[-1].strip()

                if "ਉਮਰ" in bl:
                    age = int("".join(filter(str.isdigit, bl)))

                if "ਲਿੰਗ" in bl:
                    gender = bl.split(":")[-1].strip()

            voters.append(
                {
                    "ac_no": ac_no,
                    "part_no": part_no,
                    "section_no": section_no,
                    "serial_no": serial_no,
                    "epic_no": epic_no,
                    "name": name,
                    "relation_name": relation,
                    "house_no": house_no,
                    "age": age,
                    "gender": gender,
                }
            )

            i = j
        else:
            i += 1

    return pd.DataFrame(voters)


# def parse_part_from_bytes(file_bytes: bytes, part_no: int, ac_no: int = 14, section_no: int = 1) -> pd.DataFrame:
#     lines = extract_lines_from_bytes(file_bytes)
#     voters = []
#     i = 0

#     while i < len(lines):
#         line = lines[i]

#         if is_serial(line):
#             serial_no = int(line)
#             epic_no = None
#             block_lines: list[str] = []

#             j = i + 1
#             while j < len(lines) and not is_epic(lines[j]):
#                 if is_serial(lines[j]):
#                     break
#                 j += 1

#             if j < len(lines) and is_epic(lines[j]):
#                 epic_no = lines[j]
#                 j += 1

#             while j < len(lines) and not is_serial(lines[j]):
#                 block_lines.append(lines[j])
#                 j += 1

#             block_text = " ".join(block_lines)

#             house_no_match = re.search(r"(मराठ|ਮਕਾਨ)\s*ठं\.?\s*[:.]?\s*([0-9A-Za-z/]+)", block_text)
#             age_match = re.search(r"(विभव|वैभव|ਉਮਰ)\s*[:.]?\s*([0-9]+)", block_text)
#             gender_match = re.search(r"(लिंग|ਲਿੰਗ)\s*[:.]?\s*([^\s]+)", block_text)

#             house_no = house_no_match.group(2) if house_no_match else None
#             age = int(age_match.group(2)) if age_match else None
#             gender = gender_match.group(2) if gender_match else None

#             name = None
#             relation = None
#             for bl in block_lines:
#                 if bl.startswith(("ਠਾਮ", "ਨਾਮ")):
#                     parts = bl.split(" ", 1)
#                     if len(parts) > 1:
#                         name = parts[1].strip()
#                 if bl.startswith(("ਚਿਡ਼ਾ", "ਚਿਡਾ", "ਪਿਤਾ", "यूडी", "ਪਿਡਾ", "ਪਡੀ")):
#                     parts = bl.split(" ", 1)
#                     if len(parts) > 1:
#                         relation = parts[1].strip()

#             voters.append({
#                 "ac_no": ac_no,
#                 "part_no": part_no,
#                 "section_no": section_no,
#                 "serial_no": serial_no,
#                 "epic_no": epic_no,
#                 "house_no": house_no,
#                 "age": age,
#                 "gender": gender,
#                 "name": name,
#                 "relation_name": relation,
#             })

#             i = j
#         else:
#             i += 1

#     return pd.DataFrame(voters)
