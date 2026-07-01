import pandas as pd
import pytest

from crm.pages.customers import _find_customer_by_id
from crm.pages.sales import build_pricing_payload


class _Ctx:
    user_id = "u1"
    company_id = "co1"


def test_build_pricing_payload_valid():
    payload = build_pricing_payload(_Ctx(), "c1", "Takjobb", 12500, "Notat")
    assert payload["customer_id"] == "c1"
    assert payload["job_type"] == "Takjobb"
    assert payload["calculated_price"] == 12500.0


@pytest.mark.parametrize(
    "customer_id,job_type",
    [
        ("", "Takjobb"),
        ("c1", ""),
    ],
)
def test_build_pricing_payload_requires_fields(customer_id, job_type):
    with pytest.raises(ValueError):
        build_pricing_payload(_Ctx(), customer_id, job_type, 1000)


def test_find_customer_by_id():
    customers_df = pd.DataFrame(
        [
            {"id": "c1", "name": "Alpha"},
            {"id": "c2", "name": "Beta"},
        ]
    )
    selected = _find_customer_by_id(customers_df, "c2")
    assert selected["name"] == "Beta"
