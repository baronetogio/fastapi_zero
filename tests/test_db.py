from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session):
    user = User(
        username='baronetogio',
        email='gio@test.com',
        password='123123123',
    )
    session.add(user)
    session.commit()

    result = session.scalar(select(User).where(User.email == 'gio@test.com'))

    assert result.username == 'baronetogio'
