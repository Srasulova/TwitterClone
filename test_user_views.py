"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = 'postgresql://postgres:Milagros@localhost/warbler-test'


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

with app.app_context():
   db.create_all()


# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""
    def setUp(self):
        with app.app_context():
            User.query.delete()
            Message.query.delete()

            self.testuser = User.signup(username="testuser",email="test@test.com",password="testuser",image_url=None)
            self.user1 = User.signup("user1", "user1@test.com", "password", None)
            self.user2 = User.signup("user2", "user2@test.com", "password", None)
            self.user3 = User.signup("user3", "user3@test.com", "password", None)
            self.user4 = User.signup("user4", "user4@test.com", "password", None)

            db.session.add(self.testuser)
            db.session.add(self.user1)
            db.session.add(self.user2)
            db.session.add(self.user3)
            db.session.add(self.user4)
            db.session.commit()

            self.client = app.test_client()

            self.setUpFollows()

    
    def tearDown(self):

        with app.app_context():
            db.session.rollback()

    
    def setUpFollows(self):

        with app.app_context():

            follow1 = Follows(user_being_followed_id= self.user1.id, user_following_id = self.testuser.id )
            follow2 = Follows(user_being_followed_id= self.user2.id, user_following_id = self.testuser.id )
            follow3 = Follows(user_being_followed_id= self.user3.id, user_following_id = self.testuser.id )
            follow4 = Follows(user_being_followed_id= self.user4.id, user_following_id = self.testuser.id )

            db.session.add_all([follow1, follow2, follow3, follow4])
            db.session.commit()


    def test_user_profile_route(self):
        """Test if user profile route responds with the code status 200"""

        with app.app_context():
            testuser = User.query.filter_by(username="testuser").first()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser.id

            resp = c.get(f"/users/{testuser.id}")
            self.assertEqual(resp.status_code, 200)

    
    def test_following_route(self):
        """Test if following route responds with the code status 200"""

        with app.app_context():
            testuser = User.query.filter_by(username="testuser").first()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser.id
            
            resp = c.get(f"/users/{testuser.id}/following")
            self.assertEqual(resp.status_code, 200)

            # Check if the usernames of the users the test user is following are present in the response data
            self.assertIn("user1", str(resp.data))
            self.assertIn("user2", str(resp.data))

    def test_followers_route(self):
        """Test if followers route responds with the code status 200"""

        with app.app_context():
            testuser = User.query.filter_by(username="testuser").first()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser.id
            
            resp = c.get(f"/users/{testuser.id}/followers")
            self.assertEqual(resp.status_code, 200)
    
    def test_unathorized_user_following_page(self):
        """Test if unauthorized user is disallowed from accessing following page."""
        with self.client as c:
            resp = c.get(f"/users/{self.testuser.id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))

    
    def test_unathorized_user_followers_page(self):
        """Test if unauthorized user is disallowed from accessing followers page."""
        with self.client as c:
            resp = c.get(f"/users/{self.testuser.id}/followers", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))

    
    def test_profile_route(self):
        """Test if update user profile page route responds with the code status 200"""

        with app.app_context():
            testuser = User.query.filter_by(username="testuser").first()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser.id
            
            resp = c.get(f"/users/profile/{testuser.id}")
            self.assertEqual(resp.status_code, 200)

    
    def test_delete_user_route(self):
        """Test if delete user route responds with the code status 302"""

        with app.app_context():
            testuser = User.query.filter_by(username="testuser").first()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser.id
            
            resp = c.post(f"/users/delete")
            self.assertEqual(resp.status_code, 302)