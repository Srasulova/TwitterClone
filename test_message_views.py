"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

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


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        with app.app_context():

            User.query.delete()
            Message.query.delete()
    
            self.testuser = User.signup(username="testuser",
                                        email="test@test.com",
                                        password="testuser",
                                        image_url=None)
            
            db.session.add(self.testuser)
            db.session.commit()

            self.client = app.test_client()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with app.app_context():
            testuser = User.query.filter_by(username="testuser").first()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
    
    
    def test_unathorized_user_add_message(self):
        """Test if user not logged in can add messages"""
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))

    
    def test_messages_show_route(self):
        """Test if the /messages/<int:message_id> route responds with status code 200"""

        with app.app_context():
            testuser = User.query.filter_by(username="testuser").first()

            test_message = Message(text="Test message is here nope", user_id = testuser.id)
            db.session.add(test_message)
            db.session.commit()

            testMessage = Message.query.filter_by(user_id = testuser.id).first()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser.id

            resp = c.get(f"/messages/{testMessage.id}")
            self.assertEqual(resp.status_code, 200)

    
    def test_messages_add_like_route(self):
        """Test if the /user/add_like?<int:message_id> route responds with the status code 302"""

        with app.app_context():
            testuser = User.query.filter_by(username="testuser").first()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser.id

            resp = c.post("/users/add_like/1")
            self.assertEqual(resp.status_code, 302)
    
    def test_messages_show_likes_route(self):
        """Test if the /users/<int:user_id>/likes route respond with the status code 200"""

        with app.app_context():

            testuser = User.query.filter_by(username="testuser").first()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser.id
            
            resp = c.get(f"/users/{testuser.id}/likes")
            self.assertEqual(resp.status_code, 200)

    
    def test_messages_delete_message_route(self):
        """Test if the /message/<int:message_id>/delete route responds with the status code 302"""

        with app.app_context():
            testuser = User.query.filter_by(username="testuser").first()

            test_message = Message(text="Test message is here yesss", user_id = testuser.id)
            db.session.add(test_message)
            db.session.commit()

            message = Message.query.filter_by(user_id = testuser.id).first()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser.id
        
            resp = c.post(f"/messages/{message.id}/delete")
            self.assertEqual(resp.status_code, 302)


    def test_unathorized_user_delete_message(self):
        """Test if user not logged in can delete a messages"""
        with app.app_context():
            testuser = User.query.filter_by(username="testuser").first()

            test_message = Message(text="Test message is here yesss", user_id = testuser.id)
            db.session.add(test_message)
            db.session.commit()

            message = Message.query.filter_by(user_id = testuser.id).first()

        with self.client as c:
             resp = c.post(f"/messages/{message.id}/delete", follow_redirects= True)
             self.assertEqual(resp.status_code, 200)
             self.assertIn("Access unauthorized.", str(resp.data))

    def test_logged_in_user_adding_message_for_another_user(self):
        """Test if a current user can add a messages for other user"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 222

            resp = c.post("/messages/new", data={"text": "I really should not be adding a message for someone else, but I'm still trying to" }, follow_redirects= True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))


    def test_logged_in_user_deleting_message_for_another_user(self):
        """Test if a current user can delete a messages for other user"""
        with app.app_context():
            testuser = User.query.filter_by(username="testuser").first()

            test_message = Message(text="I'm trying to delete someone's message! Not nice :) ", user_id = testuser.id)
            db.session.add(test_message)
            db.session.commit()

            self.assertIsNotNone(test_message.id)
            print(f"Test user id is{testuser.id}")
            print(f"test message id is {test_message.id}")

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 333
        
            resp = c.post(f"/messages/{test_message.id}/delete", follow_redirects= True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))

        with app.app_context():
            msg = Message.query.get(test_message.id)
            self.assertIsNotNone(msg)

           
        


    
    