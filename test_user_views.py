import os
from unittest import TestCase
from models import db, connect_db, Message, User, Likes, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()
app.config['WTF_CSRF_ENABLED'] = False

class MessageViewTestCase(TestCase):
    """Create test and add data"""
    def setUp(self):
        db.drop_all()
        db.create_all()

        self.client = app.test_client()
        self.testuser = User.signup(username="testuser",
                                        email="test@test.com",
                                        password="testuser",
                                        image_url=None)
        self.testuser_id = 54321
        self.testuser.id = self.testuser_id

        self.user1 = User.signup(username="User1",
                                        email="test1@test.com",
                                        password="password",
                                        image_url=None)
        self.user1_id = 100
        self.user1.id = self.user1_id
        self.user2 = User.signup(username="User2",
                                        email="test2@test.com",
                                        password="password",
                                        image_url=None)
        self.user2_id = 56789
        self.user2.id = self.user2_id

        db.session.commit()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_user_index(self):
        with self.client as c:
            res = c.get("/users")
            
            self.assertIn("@testuser", str(res.data))
            self.assertIn("@User1", str(res.data))
            self.assertIn("@User2", str(res.data))

    def test_user_show(self):
         with self.client as c:
            res = c.get(f"/users/{self.testuser_id}")

            self.assertEqual(res.status_code, 200)
            self.assertIn("@testuSER", str(res.data))

    def setup_likes(self):
        m1 = Message(text="This is message one.", user_id=self.testuser_id)
        m2 = Message(text="Testing message 2.", user_id=self.testuser_id)
        m3 = Message(text="I dont know what to put here.", user_id=self.user1_id)
        
        db.session.add_all([m1,m2,m3])
        db.session.commit()

    def test_add_like(self):
        m = Message(id= 1111, text="Like this message!", user_id=self.user2_id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction as s:
                s[CURR_USER_KEY] = self.testuser_id
            
            res = c.post("/messages/1111/like",follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            
            likes = Likes.query.filter(Likes.message_id==1111).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.user2_id)

    def test_remove_like(self):
        self.setup_likes()
        
        m = Message.query.filter(Message.text == "This is message one.").one()
        self.assertIsNotNone(m)
        self.assertNotEqual(m.user_id, self.testuser_id)

        likes = Likes.query.filter(Likes.user_id == self.testuser_id 
                                   and Likes.message_id == m.id).one()
        self.assertIsNotNone(likes)

        with self.client as c:
            with c.session_transaction as s:
                s[CURR_USER_KEY] = self.testuser_id
            
            res = c.post(f"/messages/{m.id}/like",follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            likes = Likes.query.filter(Likes.message_id==m.id).all()
            self.assertEqual(len(likes), 0)

    def setup_followers(self):
        f1 = Follows(user_being_followed_id=self.user1_id, user_following_id=self.testuser_id)
        f2 = Follows(user_being_followed_id=self.user2_id, user_following_id=self.testuser_id)
        f3 = Follows(user_being_followed_id=self.testuser_id, user_following_id=self.user1_id)

        db.session.add_all([f1,f2,f3])
        db.session.commit()

    def test_show_following(self):
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as s:
                s[CURR_USER_KEY]=self.testuser_id
            
            res = c.get(f"/users/{self.User1_id}/following")
            self.assertEqual(res.status_code, 200)
            self.assertIn("@testuser", str(res.data))
            self.assertNotIn("@User2", str(res.data))
    
    def test_show_followers(self):
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as s:
                s[CURR_USER_KEY]=self.testuser_id
            
            res = c.get(f"/users/{self.testuser_id}/followers")
            self.assertEqual(res.status_code, 200)
            self.assertIn("@User1", str(res.data))
            self.assertNotIn("@User2", str(res.data))
    



