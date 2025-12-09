from app.services.header_detector import detect_headers, detect_headers_simple_map


def test_header_detector_piping():
    columns = [
        "Candidate Name",
        "Contact No",
        "Email Address",
        "Designation",
        "Department",
        "Last Contacted"
    ]
    res = detect_headers(columns)
    assert res["Candidate Name"]["field"] == "NAME"
    assert res["Contact No"]["field"] == "PHONE"
    assert res["Email Address"]["field"] == "EMAIL"
    assert res["Designation"]["field"] == "DESIGNATION"
    assert res["Department"]["field"] == "DEPARTMENT"
    assert res["Last Contacted"]["field"] == "DATE"
    for v in res.values():
        assert v["score"] >= 0.75


def test_header_detector_quality():
    columns = [
        "Full Name",
        "Mobile",
        "E-Mail",
        "Role",
        "Functional Area",
        "Application Date"
    ]
    res = detect_headers(columns)
    assert res["Full Name"]["field"] == "NAME"
    assert res["Mobile"]["field"] == "PHONE"
    assert res["E-Mail"]["field"] == "EMAIL"
    assert res["Role"]["field"] == "DESIGNATION"
    assert res["Functional Area"]["field"] == "DEPARTMENT"
    assert res["Application Date"]["field"] == "DATE"
    for v in res.values():
        assert v["score"] >= 0.75


def test_header_detector_electrical():
    columns = [
        "First Name",
        "Phone Number",
        "Email ID",
        "Position",
        "Division",
        "Updated Date"
    ]
    res = detect_headers(columns)
    assert res["First Name"]["field"] == "NAME"
    assert res["Phone Number"]["field"] == "PHONE"
    assert res["Email ID"]["field"] == "EMAIL"
    assert res["Position"]["field"] == "DESIGNATION"
    assert res["Division"]["field"] == "DEPARTMENT"
    assert res["Updated Date"]["field"] == "DATE"
    for v in res.values():
        assert v["score"] >= 0.75
