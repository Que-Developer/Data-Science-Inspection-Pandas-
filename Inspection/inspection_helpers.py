"""Two small reporting functions used by Chapters 2, 3 and 4.

The notebooks explain the arguments and show this code in their reference section.
Inspection conditions remain in the notebooks. These functions count and save
results; they never change the original dataset or choose a cleaning treatment.
"""

from pathlib import Path
import pandas as pd


def summarise_check(check_id, check_name, total, flagged, untested=0):
    """Return one dictionary describing one record-level check.

    total: all imported records in the check's scope.
    flagged: records checked that need review.
    untested: records that lacked information required for this particular check.
    """
    total = int(total)
    flagged = int(flagged)
    untested = int(untested)
    checked = total - untested
    passed = checked - flagged

    # A positive flagged count needs review. No checked records means Untested.
    # Otherwise Passed refers to checked records; untested records stay visible.
    if flagged > 0:
        result = "Flagged"
    elif checked == 0:
        result = "Untested"
    else:
        result = "Passed"

    return {
        "Check ID": check_id,
        "Check": check_name,
        "Total records": total,
        "Checked records": checked,
        "Passed records": passed,
        "Flagged records": flagged,
        "Untested records": untested,
        "Check result": result,
    }


def save_check(check, evidence, finding, effect, next_action):
    """Save one check, its issue entry (if needed), and its complete evidence.

    check: the dictionary returned by summarise_check.
    evidence: original records selected in the notebook, with one row per concern.
    finding, effect, next_action: explanations written by the student.
    """
    check_id = check["Check ID"]
    check_folder = Path("Outputs/checks")
    issue_folder = Path("Outputs/issues")
    evidence_folder = Path("Outputs/evidence")
    preview_folder = Path("Outputs/previews")
    for folder in [check_folder, issue_folder, evidence_folder, preview_folder]:
        folder.mkdir(parents=True, exist_ok=True)

    # [check] is a list containing one dictionary: it creates one check-log row.
    check_table = pd.DataFrame([check])
    check_table.to_csv(check_folder / f"{check_id}.csv", index=False)

    # Preserve the original Pandas row label as a normal CSV column. It locates
    # a row in this unchanged import; it is not a fire ID or a physical line number.
    evidence_path = evidence_folder / f"{check_id}.csv"
    # Write to a temporary filename first. Publish the completed file only after
    # the CSV writer has closed it, so another reader cannot see a partial export.
    pending_evidence = evidence_path.with_suffix(".tmp")
    evidence.to_csv(pending_evidence, index=True, index_label="source_row")
    pending_evidence.replace(evidence_path)

    # A balanced preview shows both kinds of concern when both occur. These are
    # examples, not counts: keep up to five Flagged and five Untested records.
    flagged_examples = evidence.loc[evidence["Record outcome"] == "Flagged"].head(5)
    untested_examples = evidence.loc[evidence["Record outcome"] == "Untested"].head(5)
    preview = pd.concat([flagged_examples, untested_examples])
    preview.to_csv(preview_folder / f"{check_id}.csv", index=True, index_label="source_row")

    issue_columns = [
        "Check ID", "Finding", "Flagged records", "Untested records",
        "Effect on analysis", "Next action", "Evidence CSV",
    ]
    # Missing prerequisites can limit analysis even when tested records passed.
    # A fully passed check needs no issue. Its saved issue file then has headings
    # and zero rows, so rerunning a check also replaces any older issue entry.
    if check["Flagged records"] > 0 or check["Untested records"] > 0:
        issue = {
            "Check ID": check_id,
            "Finding": finding,
            "Flagged records": check["Flagged records"],
            "Untested records": check["Untested records"],
            "Effect on analysis": effect,
            "Next action": next_action,
            "Evidence CSV": evidence_path.as_posix(),
        }
        issue_table = pd.DataFrame([issue], columns=issue_columns)
    else:
        issue_table = pd.DataFrame(columns=issue_columns)
    issue_table.to_csv(issue_folder / f"{check_id}.csv", index=False)

    # This summary keeps the scope and the saved evidence count visible in class.
    print(f"{check_id}: {check['Check result']} for {check['Checked records']:,} checked records")
    print(f"Flagged: {check['Flagged records']:,}; Untested: {check['Untested records']:,}")
    print(f"Complete evidence rows saved: {len(evidence):,} -> {evidence_path}")
