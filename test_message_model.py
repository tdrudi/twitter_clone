import os
from unittest import TestCase
from models import db, User, Message, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    """Test views for messages"""
    def setUp(self):
        db.drop_all()
        db.create_all()

        self.uid = 12345
        u = User.signup("TestUser", "test@test.com", "password", None)
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_msg_model(self):
        m = Message(
            text = "Test Message", 
            user_id=self.uid)
        db.session.add(m)
        db.session.commit()

        #There should be one msg
        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, "Test Message")


    def test_msg_like(self):
        #Test liking msgs
        m1 = Message(
                text = "First Test Message", 
                user_id=self.uid)
        m2 = Message(
                text = "This is my second message.", 
                user_id=self.uid)    

        uid = 99999
        u = User.signup("SecondTest", "test2@test.com", "password", None)
        u.id = uid
        db.session.commit()

        u.likes.append(m1)
        db.session.commit()

        likes = Likes.query.filter(Likes.user_id == uid).all()
        self.assertEqual(len(likes), 1)
        self.assertEqual(likes[0].message_id, m1.id)
