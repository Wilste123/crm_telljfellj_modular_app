from crm import data


def test_fetch_all_data_uses_company_scoped_cache_key(monkeypatch):
    calls = []

    def fake_fetch_table(cache_key, table_name, order_by=None, ascending=True, company_id=None):
        calls.append((cache_key, table_name, company_id))
        return []

    monkeypatch.setattr(data, "fetch_table", fake_fetch_table)

    result = data.fetch_all_data("user-1", "company-9")

    assert "leads" in result
    assert calls
    assert all(call[0] == "user-1:company-9" for call in calls)
    assert all(call[2] == "company-9" for call in calls)


def test_prepare_data_maps_lead_customer_name():
    dfs = data.prepare_data(
        {
            "customers": [{"id": "c1", "name": "Acme"}],
            "leads": [{"id": "l1", "customer_id": "c1", "status": "Ny"}],
            "projects": [],
            "pricing": [],
            "quotes": [],
            "project_logs": [],
            "equipment": [],
            "courses": [],
            "project_log_equipment": [],
            "equipment_service_logs": [],
            "documents": [],
        }
    )

    assert dfs["leads_df"].iloc[0]["customer_name"] == "Acme"
