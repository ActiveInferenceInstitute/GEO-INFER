"""Tests for organization modeling: structure, roles, and budget allocation."""

import pytest
from geo_infer_org.core.organization import (
    OrganizationModel,
    OrgUnit,
    Role,
    OrgStructureType,
    RoleLevel,
)


@pytest.fixture
def org():
    model = OrganizationModel()
    model.add_unit(OrgUnit("root", "HQ", member_count=10, budget=100000))
    model.add_unit(OrgUnit("eng", "Engineering", parent_id="root", member_count=50, budget=500000))
    model.add_unit(OrgUnit("sales", "Sales", parent_id="root", member_count=30, budget=300000))
    model.add_unit(OrgUnit("fe", "Frontend", parent_id="eng", member_count=20, budget=200000))
    model.add_unit(OrgUnit("be", "Backend", parent_id="eng", member_count=30, budget=300000))
    return model


class TestOrganizationModel:
    def test_add_unit(self, org):
        assert org.get_unit("root").name == "HQ"
        assert org.get_unit("eng").parent_id == "root"

    def test_duplicate_unit_raises(self, org):
        with pytest.raises(ValueError, match="already exists"):
            org.add_unit(OrgUnit("root", "Duplicate"))

    def test_missing_parent_raises(self):
        model = OrganizationModel()
        with pytest.raises(ValueError, match="does not exist"):
            model.add_unit(OrgUnit("child", "Orphan", parent_id="nonexistent"))

    def test_get_children(self, org):
        children = org.get_children("root")
        names = {c.name for c in children}
        assert names == {"Engineering", "Sales"}

    def test_get_descendants(self, org):
        descendants = org.get_descendants("root")
        assert len(descendants) == 4  # eng, sales, fe, be

    def test_get_ancestors(self, org):
        ancestors = org.get_ancestors("fe")
        names = [a.name for a in ancestors]
        assert names == ["Engineering", "HQ"]

    def test_compute_depth(self, org):
        assert org.compute_depth("root") == 0
        assert org.compute_depth("eng") == 1
        assert org.compute_depth("fe") == 2

    def test_metrics(self, org):
        org.add_role(Role("ceo", "CEO", RoleLevel.EXECUTIVE, "root"))
        org.add_role(Role("vp_eng", "VP Engineering", RoleLevel.DIRECTOR, "eng", reports_to="ceo"))
        org.add_role(Role("fe_lead", "FE Lead", RoleLevel.LEAD, "fe", reports_to="vp_eng"))
        org.add_role(Role("dev1", "Developer", RoleLevel.INDIVIDUAL, "fe", reports_to="fe_lead"))

        metrics = org.compute_metrics()
        assert metrics.total_units == 5
        assert metrics.total_roles == 4
        assert metrics.max_depth == 2
        assert metrics.avg_span_of_control > 0

    def test_reporting_chain(self, org):
        org.add_role(Role("ceo", "CEO", RoleLevel.EXECUTIVE, "root"))
        org.add_role(Role("vp", "VP Eng", RoleLevel.DIRECTOR, "eng", reports_to="ceo"))
        org.add_role(Role("lead", "Lead", RoleLevel.LEAD, "fe", reports_to="vp"))

        chain = org.find_reporting_chain("lead")
        assert len(chain) == 2
        assert chain[0].role_id == "vp"
        assert chain[1].role_id == "ceo"

    def test_budget_equal(self, org):
        alloc = org.allocate_budget(100000, strategy="equal")
        assert len(alloc) == 5
        for val in alloc.values():
            assert val == 20000.0

    def test_budget_proportional(self, org):
        alloc = org.allocate_budget(100000, strategy="proportional")
        assert alloc["be"] > alloc["fe"]  # 30 members vs 20

    def test_budget_weighted(self, org):
        alloc = org.allocate_budget(100000, strategy="weighted")
        assert alloc["eng"] > alloc["root"]  # Higher existing budget

    def test_budget_negative_raises(self, org):
        with pytest.raises(ValueError, match="non-negative"):
            org.allocate_budget(-1000)

    def test_budget_unknown_strategy(self, org):
        with pytest.raises(ValueError, match="Unknown"):
            org.allocate_budget(100000, strategy="magic")

    def test_to_dict(self, org):
        result = org.to_dict()
        assert result["structure_type"] == "hierarchical"
        assert "root" in result["units"]
        assert len(result["units"]) == 5

    def test_role_not_found_raises(self, org):
        with pytest.raises(KeyError, match="not found"):
            org.find_reporting_chain("nonexistent")
