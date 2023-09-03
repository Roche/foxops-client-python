import pytest
from pytest import fixture

from foxops_client import (
    AuthenticationError,
    FoxopsApiError,
    FoxopsClient,
    IncarnationDoesNotExistError,
    MergeRequestStatus,
)


def test_verify_token(foxops_client: FoxopsClient):
    foxops_client.verify_token()


def test_verify_token_raises_unauthenticated_exception_when_using_an_invalid_token(foxops_client_invalid_token):
    with pytest.raises(AuthenticationError):
        foxops_client_invalid_token.verify_token()


def test_create_incarnation(gitlab_api_client, foxops_client: FoxopsClient, template, gitlab_project_factory):
    # GIVEN
    template_path = template
    incarnation_path = gitlab_project_factory(return_path=True)

    # WHEN
    incarnation = foxops_client.create_incarnation(
        incarnation_repository=incarnation_path,
        template_repository=template_path,
        template_repository_version="main",
        template_data={"input_variable": "foo"},
    )

    # THEN
    assert incarnation.id is not None

    assert incarnation.incarnation_repository == incarnation_path
    assert incarnation.template_repository == template_path
    assert incarnation.template_repository_version == "main"
    assert incarnation.template_data == {"input_variable": "foo"}


def test_create_incarnation_with_conflicting_existing_incarnation(incarnation, foxops_client):
    # WHEN
    with pytest.raises(FoxopsApiError) as e:
        foxops_client.create_incarnation(
            incarnation_repository=incarnation.incarnation_repository,
            template_repository=incarnation.template_repository,
            template_repository_version=incarnation.template_repository_version,
            template_data=incarnation.template_data,
        )

    # THEN
    assert e.value.message.find("already initialized") != -1


def test_delete_incarnation(incarnation, foxops_client: FoxopsClient):
    # WHEN
    foxops_client.delete_incarnation(incarnation.id)

    # THEN
    with pytest.raises(IncarnationDoesNotExistError):
        foxops_client.get_incarnation(incarnation.id)


def test_delete_incarnation_with_non_existing_incarnation(foxops_client):
    # WHEN
    with pytest.raises(IncarnationDoesNotExistError):
        foxops_client.delete_incarnation(9999999)


def test_get_incarnation(incarnation, foxops_client):
    # WHEN
    response = foxops_client.get_incarnation(incarnation.id)

    # THEN
    assert response == incarnation


def test_get_incarnation_with_non_existing_incarnation(foxops_client):
    # WHEN
    with pytest.raises(IncarnationDoesNotExistError):
        foxops_client.get_incarnation(9999999)


def test_list_incarnation(incarnation, foxops_client):
    # GIVEN
    assert incarnation

    # WHEN
    response = foxops_client.list_incarnations()

    # THEN
    assert len(response) >= 1


def test_list_incarnation_with_non_existing_incarnation(foxops_client):
    with pytest.raises(IncarnationDoesNotExistError):
        foxops_client.list_incarnations(incarnation_repository="nonexisting", target_directory=".")


def test_update_incarnation_with_template_data_change_and_no_automerge(incarnation, foxops_client):
    # WHEN
    response = foxops_client.update_incarnation(
        incarnation_id=incarnation.id,
        automerge=False,
        template_data={"input_variable": "bar"},
    )

    # THEN
    # because we didn't merge, the template data should be the same as in the original incarnation details
    assert response.template_data == incarnation.template_data

    assert response.commit_sha is not None
    assert response.commit_url is not None

    assert response.merge_request_id is not None
    assert response.merge_request_url is not None
    assert response.merge_request_status == MergeRequestStatus.OPEN


@fixture(name="incarnation")
def create_incarnation(template, gitlab_project_factory, foxops_client):
    template_path = template
    incarnation_path = gitlab_project_factory(return_path=True)

    incarnation = foxops_client.create_incarnation(
        incarnation_repository=incarnation_path,
        template_repository=template_path,
        template_repository_version="main",
        template_data={"input_variable": "foo"},
    )

    return incarnation
