from datetime import datetime
from typing import Union
import pdb


def get_first_day_of_month(dt: Union[str, datetime]) -> datetime:
  if isinstance(dt, str):
    try:
      dt = datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
      try: 
        dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
      except ValueError:
        dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S.%f')

  return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
