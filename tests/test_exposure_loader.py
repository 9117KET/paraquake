from paraquake.data.exposure_loader import load_exposure_portfolio


def test_loads_twenty_sites():
    sites = load_exposure_portfolio()
    assert len(sites) == 20


def test_site_ids_are_unique():
    sites = load_exposure_portfolio()
    ids = [s.site_id for s in sites]
    assert len(ids) == len(set(ids))


def test_includes_port_au_prince_for_haiti_case_study():
    sites = load_exposure_portfolio()
    names = {s.site_name for s in sites}
    assert "Port-au-Prince Critical Infrastructure" in names


def test_fields_are_well_typed_and_plausible():
    sites = load_exposure_portfolio()
    for s in sites:
        assert -90 <= s.latitude <= 90
        assert -180 <= s.longitude <= 180
        assert s.sum_insured_eur > 0
        assert s.max_payout_eur <= s.sum_insured_eur
        assert s.trigger_radius_km > 0
        assert s.construction_class in {"A", "B", "C"}
