"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = 'postgresql://postgres:Milagros@localhost/warbler-test'


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data


with app.app_context():
   db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():

            User.query.delete()
            Message.query.delete()
            Follows.query.delete()

            self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        with app.app_context():

            u = User(
                email="aliyarodri@test.com",
                username="aliyarodri",
                password="HASHED_PASSWORD"
        )

            db.session.add(u)
            db.session.commit()

            # User should have no messages & no followers
            self.assertEqual(len(u.messages), 0)
            self.assertEqual(len(u.followers), 0)

            #Does the repr method work as expected?
            expected_repr = f"<User #{u.id}: {u.username}, {u.email}>"
            self.assertEqual(repr(u), expected_repr)

    def test_is_following(self):
        """Does is_following successfully detect when user1 is following user2?"""
        with app.app_context():
            user1 = User(
            email="user123@test.com",
            username="user123",
            password="HASHED_PASSWORD1"
        )
            user2 = User(
            email="user234@test.com",
            username="user234",
            password="HASHED_PASSWORD2"
        )

            db.session.add_all([user1, user2])
            db.session.commit()

            # Check if user1 is not following user2 initially
            self.assertFalse(user1.is_following(user2))

            # user1 follows user2
            user1.following.append(user2)
            db.session.commit()

            # Check if user1 is now following user2
            self.assertTrue(user1.is_following(user2))


    
    def test_user_authenticate_valid_credentials(self):
        """Does User.authenticate successfully return a user when given valid credentials?"""
        with app.app_context():
            # Create a user with valid credentials
            user = User.signup("testuser12", "testuser12@test.com", "testpassword", "testimageurl")
            db.session.commit()
    
            authenticated_user = User.authenticate("testuser12", "testpassword")
    
            self.assertEqual(authenticated_user, user)

    def test_user_authenticate_invalid_username(self):
        """Does User.authenticate fail to return a user when the username is invalid?"""
        with app.app_context():
            authenticated_user = User.authenticate("invalidusername1", "testpassword")

            self.assertFalse(authenticated_user)


    def test_user_authenticate_invalid_password(self):
        """Does User.authenticate fail to return a user when the password is invalid?"""
        with app.app_context():
            authenticated_user = User.authenticate("testuser12", "invalidpassword")
    
            self.assertFalse(authenticated_user)


