import sys
path = '/home/Peemkay/nass_portal'
if path not in sys.path:
    sys.path.append(path)

from nass_portal import create_app
application = create_app()