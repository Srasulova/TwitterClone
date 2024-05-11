from datetime import datetime
import os
from unittest import TestCase

from models import db, User, Message
from sqlalchemy.exc import IntegrityError

os.environ['DATABASE_URL'] = 'postgresql://postgres:Milagros@localhost/warbler-test'
from app import app

with app.app_context():
    db.drop_all()
    db.create_all()
 

class MessageModelTestCase(TestCase):
    """Test cases for the Message model."""

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            self.client = app.test_client()

    def test_message_create_valid_input(self):
        """Does Message successfully create a new message given valid input?"""
        with app.app_context():
            # Create a test user
            user = User(
                username="testuser56",
                email="testuser56@test.com",
                password="testpassword",
                image_url="testimageurl"
            )
            db.session.add(user)
            db.session.commit()

            message_text = "This is a test message."
            new_message = Message(
                user_id=user.id,
                text=message_text
            )
            db.session.add(new_message)
            db.session.commit()

            # Check if the new message exists in the database
            self.assertIsNotNone(new_message)
            self.assertEqual(new_message.user_id, user.id)
            self.assertEqual(new_message.text, message_text)

    def test_message_create_text_limit_exceeded(self):
        """Does Message fail to create a new message if the text exceeds the character limit?"""
        with app.app_context():
            # Create a test user
            user = User(
                username="testuser34",
                email="testuser34@test.com",
                password="testpassword",
                image_url="testimageurl"
            )
            db.session.add(user)
            db.session.commit()
    
            long_message_text = "a" * 141  # This exceeds the 140-character limit
            new_message = Message(
                user_id=user.id,
                text=long_message_text
            )
            db.session.add(new_message)

            # Try committing the session and handle the exception
            try:
                db.session.commit()
            except IntegrityError as e:
                # Check that the IntegrityError is due to the text length exceeding the limit
                self.assertIn("value too long for type character varying(140)", str(e))
                db.session.rollback()
            finally:
                # Check that no message was created
                self.assertEqual(Message.query.count(), 0)
                



    def test_message_create_empty_text(self):
        """Does Message fail to create a new message if the text field is empty or missing?"""
        with app.app_context():
            # Create a test user
            user = User(
                username="testuser48",
                email="testuser48@test.com",
                password="testpassword",
                image_url="testimageurl"
            )
            db.session.add(user)
            db.session.commit()
    
            initial_empty_messages_count = Message.query.filter_by(text="").count()
    
            try:
                # Try to create a new message with an empty text field
                new_message = Message(
                    user_id=user.id,
                    text=""
                )
                db.session.add(new_message)
                db.session.commit()
            except IntegrityError:
                # If an IntegrityError is raised due to an empty text field, the test passes
                db.session.rollback()
                final_empty_messages_count = Message.query.filter_by(text="").count()
                

            # Assert that no empty text messages were added to the database
            self.assertEqual(initial_empty_messages_count, final_empty_messages_count)
            self.assertEqual(Message.query.count(), 0)  # Ensure no message was added




