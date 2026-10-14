"""studylist.py - which main-bank rows are NOT in the study list.

The columns skip / skip_reason are locked (they come from the input file). Rows found later to be duplicates or
Austria/Switzerland-only words are flagged in the free column `check` instead:
    check = "dup:B1234"  -> same word as row B1234, learn that one
    check = "drop?"      -> Austrian/Swiss variant: recognise it, but it is not needed in Germany
mark_not_in_list(rows) turns those flags into skip="yes" + skip_reason for the study page, the Excel file and the vault.
"""


def mark_not_in_list(rows):
    for r in rows:
        if r.get("skip"):
            continue
        ck = (r.get("check") or "").strip()
        if ck.startswith("dup:"):
            r["skip"], r["skip_reason"] = "yes", f"duplicate of {ck[4:]} (learn that entry)"
        elif ck == "drop?":
            r["skip"], r["skip_reason"] = "yes", "Austrian/Swiss word: recognise it, but Germany uses the standard word"
    return rows
