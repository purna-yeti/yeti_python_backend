from psaw import PushshiftAPI
from app.main.service.reddit_query_service import SearchType
from typing import Dict, List
from datetime import datetime

class PSAW:
  def __init__(self):
    self.api = PushshiftAPI()

  def search(self, before: datetime, after: datetime, query_: str, search_type: SearchType, limit: int) -> List[Dict[str,str]]:
    if search_type == SearchType.SUBMISSION:
      resp = self.api.search_submissions(
        q=query_,
        limit=limit,
        before=before,
        after=after
      )
    else:
      resp = self.api.search_comments(
        q=query_,
        limit=limit,
        before=before,
        after=after
      )
    return [item.d_ for item in resp]

