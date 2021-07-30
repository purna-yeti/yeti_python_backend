import unittest
import datetime
from app.main import db
from app.test.base import BaseTestCase
import json
import pdb


class TestRedditQuery(BaseTestCase):

    def test_reddit_query(self):
      with self.client:
        resp = self.client.post('/reddit_query/',
                                  data=json.dumps(dict(
                                    query='https://www.coursera.org/learn/learning-how-to-learn',
                                    before="2021-07-30T04:22:57.004Z"
                                  )),
                                  content_type='application/json'
                                  )
                                
        print(resp.json)

if __name__ == '__main__':
  unittest.main()
