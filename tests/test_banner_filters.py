"""Run with .venv/bin/python -m unittest discover -s tests."""
import os
import unittest
from datetime import datetime

os.environ.update(
    PSQL_USER='test', PSQL_PASS='test', PSQL_HOST='localhost', PSQL_DB='test',
    SESSION_KEY='test', TOKEN_SECRET='test', TOKEN_EXPIRATION='3600',
    O2_CLIENT_ID='test', O2_CLIENT_SECRET='test',
    BE_CLIENT_ID='test', BE_CLIENT_SECRET='test', LOG_FILE_SERVER=os.devnull,
)

from src import app, db
from src.models.models import BannerImg, Campus, User

app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI='sqlite:///:memory:')


class BannerFilterTest(unittest.TestCase):
    def test_filters_apply_before_pagination_and_preserve_staff_access(self):
        with app.app_context():
            db.create_all()
            try:
                db.session.add_all([
                    Campus(1, 'Singapore', 'Singapore', 'SG'),
                    Campus(2, 'Paris', 'Paris', 'FR'),
                    User(intra_id=1, login='alice', display_name='Alice', email='a@example.test', campus_id=1),
                    User(intra_id=2, login='bob', display_name='Bob', email='b@example.test', campus_id=2),
                    User(intra_id=3, login='alicia', display_name='Alicia', email='c@example.test', campus_id=2),
                ])
                # More than one page, with equal timestamps to exercise stable ordering.
                for number in range(1, 104):
                    banner = BannerImg(1 if number <= 101 else number - 100,
                                       f'https://example.test/{number}.png', 1, 1, 1)
                    banner.id = number
                    banner.created_at = datetime(2026, 1, 1)
                    db.session.add(banner)
                db.session.commit()
                client = app.test_client()
                self.assertEqual(client.get('/v2/banners/0').status_code, 302)
                with client.session_transaction() as session:
                    session.update(uid=1, staff=False)
                self.assertEqual(client.get('/v2/banners/0?campus_id=1').status_code, 403)
                with client.session_transaction() as session:
                    session['staff'] = True

                response = client.get('/v2/banners/0?campus_id=2&login=ALI')
                self.assertEqual(response.status_code, 200)
                self.assertEqual([b['id'] for b in response.json['data']], [103])
                self.assertEqual(response.json['data'][0]['user']['campus'], 'Paris')
                first = client.get('/v2/banners/0?campus_id=1').json['data']
                self.assertEqual([b['id'] for b in first], list(range(101, 1, -1)))
                second = client.get('/v2/banners/100?campus_id=1').json['data']
                self.assertEqual([b['id'] for b in second], [1])
                self.assertEqual(client.get('/v2/banners/101?campus_id=1').status_code, 204)
                self.assertEqual(len(client.get('/v2/banners/0').json['data']), 100)
                self.assertEqual(client.get('/v2/banners/0?login=%25').status_code, 204)
                self.assertEqual(client.get('/v2/banners/0?login=missing').status_code, 204)
                for url in ['/v2/banners/-1', '/v2/banners/nope',
                            '/v2/banners/0?campus_id=nope', '/v2/banners/0?campus_id=-1']:
                    self.assertEqual(client.get(url).status_code, 400, url)
                page = client.get('/imagery.php')
                self.assertEqual(page.status_code, 200)
                self.assertIn(b'Singapore', page.data)
                self.assertIn(b'Paris', page.data)
            finally:
                db.session.remove()
                db.drop_all()
