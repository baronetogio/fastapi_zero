from http import HTTPStatus

from tests.conftest import TodoFactory


def test_crete_todo(client, token):
    response = client.post(
        '/todo',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Test todo',
            'description': 'Test todo description',
            'state': 'draft',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['title']
    assert response.json()['created_at']


def test_todo_list_should_return_5_todos(session, client, user, token):
    expected = 5
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()

    response = client.get(
        '/todo/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected


def test_todo_list_pagination_should_return_2_todos(
    session, user, client, token
):
    expected = 2
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()

    response = client.get(
        '/todo/?offset=1&limit=2', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['todos']) == expected


def test_todo_list_with_title_query_must_return_5(
    session, user, client, token
):
    expected = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(5, user_id=user.id, title='Test todo 1')
    )
    session.commit()

    response = client.get(
        '/todo/?title=Test',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected


def test_todo_list_with_state_query_must_return_5(
    session, user, client, token
):
    expected = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(5, user_id=user.id, state='draft')
    )
    session.commit()  # PESQUISAR PARAMETRIZE

    response = client.get(
        '/todo/?state=draft',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected


def test_delete_unexisting_todo(client, token):
    response = client.delete(
        '/todo/10', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


def test_delete_todo(client, session, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()

    response = client.delete(
        f'/todo/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Task has been deleted successfully'}


def test_patch_todo(client, token, user, session):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()
    session.refresh(todo)

    response = client.patch(
        f'/todo/{todo.id}',
        json={
            'title': 'Patch Title Test',
            'description': 'Patch Description Test',
            'state': 'trash',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title']
    assert response.json()['created_at']


def test_patch_unexisting_todo(client, token):
    response = client.patch(
        '/todo/10',
        json={},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}
