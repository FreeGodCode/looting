import os
import functools
from ip2region import Ip2Region, _ip2region


__all__ = ('ip2region')


_db_file = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'ip2region.db')
_ip2region_db = Ip2Region(_db_file)

ip2region = functools.partial(_ip2region, ip2region_db=_ip2region_db)
