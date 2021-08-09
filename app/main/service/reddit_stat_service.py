from app.main import db
from app.main.model.reddit_query import RedditQuery, SearchType
from app.main.model.reddit_stat import RedditStat
from typing import Dict, Tuple
from flask import current_app
from app.main.util.gcp import GcpStorage, PubSub
from app.main.util.helper import get_first_day_of_month
from app.main.util.reddit_psaw import PSAW
from dateutil.relativedelta import relativedelta
from urllib.parse import urlencode, parse_qsl
from datetime import datetime
from glob import glob
import json
import re
import pdb


"""
query reddit stat, if doesnt exist, then publish to do reddit query
"""
def query_reddit_stat(data: Dict[str, str])-> Tuple[Dict[str, str], int]:
  prefix = "query_reddit_stat:: "
  current_app.logger.info(f'{prefix} start')

  reddit_stat = RedditStat.query.filter_by(query_=data['query']).first()
  resp = PubSub(current_app.config.get('YETI_REDDIT_QUERY_TOPIC')).send_messages([
    urlencode(dict(
      query=data['query'],
      before=datetime.utcnow()
    ))]
  )
  PubSub(current_app.config.get('YETI_REDDIT_STAT_TOPIC')).send_messages(
    [data['query']]
  )
  current_app.logger.info(f'{prefix} end')
  return reddit_stat if reddit_stat is not None else {}, 201



def load_json(f):
  try:
    return json.load(f)
  except:
    return []

def get_snippet(text, pattern, size=500):
  pos = text.find(pattern)
  if pos < 0:
    return text[:size]
  else:
    return text[max(pos - size//2, 0): min(pos + len(text) // 2 + size//2, len(text))]

def get_submissions(submissions, pattern):
  return [{'full_link': s['full_link'], 'snippet': get_snippet(s['selftext'], pattern)} for s in submissions]

def get_comments(comments, pattern):
  return [{'id': s['id'], 'body': get_snippet(s['body'], pattern)} for s in comments]

"""
1. decode message
2. sync files from query 
3. calculate stats
4. save to db
"""
def handle_reddit_stat_pubsub(data: Dict[str, str]) -> Tuple[Dict[str, str], int]:
  prefix = "handle_reddit_stat_pubsub:: "
  current_app.logger.info(f'{prefix} start')
  PubSub.decode(data)
  query = data['message']['data']
  tmp_dir = GcpStorage().download_batch(query)

  # calculate stats
  comments = []
  em_comments = []
  for fn in glob(f"{ tmp_dir }/*&search_type=COMMENT&*.json"):
    with open(fn) as f:
      items = load_json(f)
      comments += items
      em_comments += [c for c in items if query in c['body']]
  submissions = []
  em_submissions = []
  for fn in glob(f"{ tmp_dir }/*&search_type=SUBMISSION&*.json"):
    with open(fn) as f:
      items = load_json(f)
      submissions += items
      em_submissions += [s for s in items if query in s['selftext']]
  for ls in [comments, em_comments, submissions, em_submissions]:
    sorted(ls, key=lambda x: x['score'])
  stat = {
    'submission': {
      'count': len(submissions),
      'max_score': submissions[-1]['score'] if len(submissions) > 0 else 0,
      'min_score': submissions[0]['score'] if len(submissions) > 0 else 0,
      'avg_score': (sum([s['score'] for s in submissions]) / len(submissions))  if len(submissions) > 0 else 0,
      'top_links': get_submissions(submissions[-5:], query),
      'bottom_links': get_submissions(submissions[:5], query),

      'em_count': len(em_submissions),
      'em_max_score': em_submissions[-1]['score'] if len(em_submissions) > 0 else 0,
      'em_min_score': em_submissions[0]['score'] if len(em_submissions) > 0 else 0,
      'em_avg_score': (sum([s['score'] for s in em_submissions]) / len(em_submissions)) if len(em_submissions) > 0 else 0,
      'em_top_links': get_submissions(em_submissions[-5:], query),
      'em_bottom_links': get_submissions(em_submissions[:5], query),
    },
    'comment': {
      'count': len(comments),
      'max_score': comments[-1]['score'] if len(comments) > 0 else 0,
      'min_score': comments[0]['score'] if len(comments) > 0 else 0,
      'avg_score': (sum([s['score'] for s in comments]) / len(comments)) if len(comments) > 0 else 0,
      'top_links': get_comments(comments[-5:], query),
      'bottom_links': get_comments(comments[:5], query),

      'em_count': len(em_comments),
      'em_max_score': em_comments[-1]['score'] if len(em_comments) > 0 else 0,
      'em_min_score': em_comments[0]['score'] if len(em_comments) > 0 else 0,
      'em_avg_score': (sum([s['score'] for s in em_comments]) / len(em_comments)) if len(em_comments) > 0 else 0, 
      'em_top_links': get_comments(em_comments[-5:], query),
      'em_bottom_links': get_comments(em_comments[:5], query),
    },
    'metadata': {
      'comment_rq_count': len(list(glob(f"{ tmp_dir }/*&search_type=COMMENT&*.json"))),
      'submission_rq_count': len(list(glob(f"{ tmp_dir }/*&search_type=SUBMISSION&*.json")))
    }
  }
  
  # save/update in database
  reddit_stat = RedditStat.query.filter_by(query_=query).first()
  if reddit_stat:
    reddit_stat.stat = stat
    update_changes(reddit_stat)
  else:
    new_reddit_stat = RedditStat(
          query_=query,
          stat=stat
        )
    save_changes(new_reddit_stat)

  db.session.commit()
  current_app.logger.info(f'{prefix} end')

  return {}, 201


def update_changes(data, commit=False) -> None:
  data.updated_at = datetime.utcnow()
  if commit:
    db.session.commit()

def save_changes(data, commit=False) -> None:
  db.session.add(data)
  if commit:
    db.session.commit()

    