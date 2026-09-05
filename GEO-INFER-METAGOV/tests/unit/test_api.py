"""Behavioral tests for the GovernanceAPI / StakeholderAPI surface."""

import pytest

from geo_infer_metagov.api import GovernanceAPI, StakeholderAPI


@pytest.fixture
def api() -> GovernanceAPI:
    return GovernanceAPI()


@pytest.fixture
def structure_id(api: GovernanceAPI) -> str:
    response = api.create_governance_structure(
        spatial_scope={'name': 'Bay Area', 'area_km2': 18000},
        stakeholder_groups=[
            {'id': 'g1', 'name': 'Water Agency'},
            {'id': 'g2', 'name': 'Farmers'},
        ],
        decision_domains=['water_allocation', 'flood_management'],
    )
    assert response.status == 'success'
    assert response.code == 201
    assert response.timestamp is not None
    data = response.data
    assert isinstance(data, dict)
    return data['governance_id']


class TestGovernanceAPICrud:
    def test_created_structure_stored_with_defaults(
        self, api: GovernanceAPI, structure_id: str
    ) -> None:
        stored = api.governance_structures[structure_id]
        assert stored['status'] == 'active'
        assert stored['governance_levels'] == ['local', 'regional', 'national']
        assert stored['spatial_scope']['name'] == 'Bay Area'

    def test_get_returns_created_structure(
        self, api: GovernanceAPI, structure_id: str
    ) -> None:
        response = api.get_governance_structure(structure_id)
        assert response.status == 'success'
        assert response.code == 200
        assert response.data is api.governance_structures[structure_id]

    def test_get_unknown_returns_404(self, api: GovernanceAPI) -> None:
        response = api.get_governance_structure('gov_missing')
        assert response.status == 'error'
        assert response.code == 404

    def test_list_with_filter_and_pagination(
        self, api: GovernanceAPI, structure_id: str
    ) -> None:
        api.create_governance_structure(
            spatial_scope={'name': 'Delta'},
            stakeholder_groups=[],
            decision_domains=['habitat'],
            governance_levels=['local', 'watershed'],
        )
        response = api.list_governance_structures(
            filter_by={'governance_levels': ['local', 'watershed']}
        )
        assert response.status == 'success'
        data = response.data
        assert isinstance(data, dict)
        assert data['total'] == 1
        assert data['items'][0]['spatial_scope']['name'] == 'Delta'

        paginated = api.list_governance_structures(limit=1, offset=1)
        paginated_data = paginated.data
        assert isinstance(paginated_data, dict)
        assert paginated_data['total'] == 2
        assert len(paginated_data['items']) == 1

    def test_update_and_delete_roundtrip(
        self, api: GovernanceAPI, structure_id: str
    ) -> None:
        response = api.update_governance_structure(
            structure_id, {'status': 'suspended'}
        )
        assert response.status == 'success'
        assert api.governance_structures[structure_id]['status'] == 'suspended'
        assert 'updated_at' in api.governance_structures[structure_id]

        deleted = api.delete_governance_structure(structure_id)
        assert deleted.status == 'success'
        assert structure_id not in api.governance_structures
        assert api.get_governance_structure(structure_id).code == 404

    def test_update_unknown_returns_404(self, api: GovernanceAPI) -> None:
        response = api.update_governance_structure('gov_missing', {'status': 'x'})
        assert response.code == 404

    def test_analyze_comprehensive_pins_metrics_and_recommendations(
        self, api: GovernanceAPI, structure_id: str
    ) -> None:
        response = api.analyze_governance_structure(structure_id)
        assert response.status == 'success'
        data = response.data
        assert isinstance(data, dict)
        metrics = data['metrics']
        assert metrics['entity_count'] == 2.0
        assert metrics['domain_count'] == 2.0
        assert metrics['level_count'] == 3.0
        assert 0.0 <= metrics['efficiency'] <= 1.0
        # Two stakeholder groups and two domains should trigger both recommendations
        recommendations = data['recommendations']
        assert "Consider including more stakeholder groups" in recommendations
        assert any('Streamline' in r or 'Enhance' in r or 'Define' in r for r in recommendations)
        # Result cached
        assert structure_id in api.analysis_cache

    def test_analyze_unknown_returns_404(self, api: GovernanceAPI) -> None:
        response = api.analyze_governance_structure('gov_missing')
        assert response.code == 404

    def test_health_status_reflects_state(
        self, api: GovernanceAPI, structure_id: str
    ) -> None:
        response = api.get_health_status()
        assert response.status == 'success'
        data = response.data
        assert isinstance(data, dict)
        assert data['status'] == 'healthy'
        assert data['structures_count'] == 1


class TestStakeholderAPI:
    def test_create_get_and_filter(self) -> None:
        api = StakeholderAPI()
        created = api.create_stakeholder(
            name='Water Agency', category='government',
            interests=['water_rights'], decision_power=0.9,
        )
        assert created.status == 'success'
        assert created.code == 201
        stakeholder = created.data
        assert isinstance(stakeholder, dict)
        stakeholder_id = stakeholder['stakeholder_id']
        assert stakeholder['decision_power'] == 0.9
        assert stakeholder['interests'] == ['water_rights']

        fetched = api.get_stakeholder(stakeholder_id)
        assert fetched.status == 'success'
        assert fetched.data is not None
        assert fetched.data['name'] == 'Water Agency'  # type: ignore[index]

        api.create_stakeholder(name='Farmers', category='business')

        all_listed = api.list_stakeholders()
        assert all_listed.data is not None
        assert all_listed.data['count'] == 2  # type: ignore[index]

        filtered = api.list_stakeholders(category='government')
        assert filtered.data is not None
        assert filtered.data['count'] == 1  # type: ignore[index]
        assert filtered.data['items'][0]['category'] == 'government'  # type: ignore[index]

    def test_get_unknown_returns_404(self) -> None:
        api = StakeholderAPI()
        response = api.get_stakeholder('sh_missing')
        assert response.status == 'error'
        assert response.code == 404


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
