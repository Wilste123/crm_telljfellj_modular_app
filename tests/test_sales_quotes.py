from __future__ import annotations

from types import SimpleNamespace

import pandas as pd

from crm.pages import sales
from crm import quotes, utils


class _FakeContextManager:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _FakeStreamlit:
    def __init__(self):
        self.form_keys = []
        self.widget_keys = []
        self.tab_labels = []
        self.expander_labels = []

    def markdown(self, *args, **kwargs):
        return None

    def info(self, *args, **kwargs):
        return None

    def caption(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None

    def success(self, *args, **kwargs):
        return None

    def error(self, *args, **kwargs):
        return None

    def dataframe(self, *args, **kwargs):
        return None

    def rerun(self):
        return None

    def code(self, *args, **kwargs):
        return None

    def write(self, *args, **kwargs):
        return None

    def link_button(self, *args, **kwargs):
        return None

    def download_button(self, *args, **kwargs):
        self._register_key(kwargs.get("key"))
        return None

    def button(self, *args, **kwargs):
        self._register_key(kwargs.get("key"))
        return False

    def form(self, key, **kwargs):
        if key in self.form_keys:
            raise AssertionError(f"Duplicate form key: {key}")
        self.form_keys.append(key)
        return _FakeContextManager()

    def tabs(self, labels):
        self.tab_labels.append(list(labels))
        return [_FakeContextManager() for _ in labels]

    def columns(self, spec):
        count = spec if isinstance(spec, int) else len(spec)
        return [_FakeContextManager() for _ in range(count)]

    def expander(self, label):
        self.expander_labels.append(label)
        return _FakeContextManager()

    def selectbox(self, *args, **kwargs):
        self._register_key(kwargs.get("key"))
        options = args[1] if len(args) > 1 else kwargs.get("options", [])
        return options[0]

    def text_input(self, *args, **kwargs):
        self._register_key(kwargs.get("key"))
        return kwargs.get("value", "") or ""

    def text_area(self, *args, **kwargs):
        self._register_key(kwargs.get("key"))
        return kwargs.get("value", "") or ""

    def number_input(self, *args, **kwargs):
        self._register_key(kwargs.get("key"))
        return kwargs.get("value", kwargs.get("min_value", 0.0))

    def date_input(self, *args, **kwargs):
        self._register_key(kwargs.get("key"))
        return kwargs["value"]

    def form_submit_button(self, *args, **kwargs):
        return False

    def _register_key(self, key):
        if key is None:
            return
        if key in self.widget_keys:
            raise AssertionError(f"Duplicate widget key: {key}")
        self.widget_keys.append(key)


def test_scoped_key_is_deterministic():
    assert utils.scoped_key("sales:quotes", "new_quote_form") == "sales:quotes:new_quote_form"
    assert utils.scoped_key("sales:quotes:", ":existing_quote_select") == "sales:quotes:existing_quote_select"


def test_render_quotes_area_allows_multiple_namespaces(monkeypatch):
    fake_st = _FakeStreamlit()
    monkeypatch.setattr(quotes, "st", fake_st)

    customers_df = pd.DataFrame(
        [{"id": "cust-1", "name": "Acme", "email": "a@example.com", "phone": "123"}]
    )
    pricing_df = pd.DataFrame(
        [{"id": "price-1", "customer_name": "Acme", "job_type": "Takvask", "calculated_price": 1000}]
    )
    quotes_df = pd.DataFrame(
        [{"id": "quote-1", "quote_number": "T-1", "customer_id": "cust-1", "customer_name": "Acme", "total_amount": 1250}]
    )
    ctx = SimpleNamespace(show_internal_ids=False)

    quotes.render_quotes_area(ctx, customers_df, pricing_df, quotes_df, key_namespace="sales:quotes")
    quotes.render_quotes_area(ctx, customers_df, pricing_df, quotes_df, key_namespace="sales:quotes:secondary")

    assert "sales:quotes:new_quote_form" in fake_st.form_keys
    assert "sales:quotes:secondary:new_quote_form" in fake_st.form_keys


def test_sales_render_creates_kalkyle_and_tilbud_tabs(monkeypatch):
    fake_st = _FakeStreamlit()
    recorded_namespaces = []

    monkeypatch.setattr(sales, "st", fake_st)
    monkeypatch.setattr(sales, "section_title", lambda *args, **kwargs: None)
    monkeypatch.setattr(sales, "badge_html", lambda *args, **kwargs: "")
    monkeypatch.setattr(sales, "render_leads_workspace", lambda ctx, show_title=False: None)
    monkeypatch.setattr(
        sales,
        "render_quotes_module",
        lambda ctx, key_namespace="quotes": recorded_namespaces.append(key_namespace),
    )

    ctx = SimpleNamespace(
        global_search="",
        show_internal_ids=False,
        dfs={
            "quotes_df": pd.DataFrame(),
            "pricing_df": pd.DataFrame([{"id": "price-1", "customer_name": "Acme", "job_type": "Takvask", "calculated_price": 1000}]),
            "projects_df": pd.DataFrame(),
            "customers_df": pd.DataFrame(),
        },
    )

    sales.render(ctx)

    assert fake_st.tab_labels[0] == ["Kalkyle", "Tilbud", "Leads"]
    assert recorded_namespaces == ["sales:quotes"]
