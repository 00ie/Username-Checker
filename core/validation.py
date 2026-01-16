import re 

class Validator :
    @staticmethod 
    def validate_format (username ):
        if not username :return False 
        if not re .match (r'^[a-zA-Z0-9._-]+$',username ):return False 
        return True 

    @staticmethod 
    def check_pinterest (username ):
        if len (username )<3 or len (username )>30 :return False 
        if not re .match (r'^[a-zA-Z0-9_]+$',username ):return False 
        if username .isdigit ():return False 
        return True 

    @staticmethod 
    def check_github (username ):
        if len (username )>39 :return False 
        if username .startswith ('-')or username .endswith ('-'):return False 
        if '--'in username :return False 
        if not re .match (r'^[a-zA-Z0-9-]+$',username ):return False 
        return True 

    @staticmethod 
    def check_instagram (username ):
        if len (username )>30 :return False 
        if username .startswith ('.')or username .endswith ('.'):return False 
        if '..'in username :return False 
        return True 
import re

class Validator:
    @staticmethod
    def validate_format(username):
        if not username: return False
        if not re.match(r'^[a-zA-Z0-9._-]+$', username): return False
        return True

    @staticmethod
    def check_pinterest(username):
        if len(username) < 3 or len(username) > 30: return False
        if not re.match(r'^[a-zA-Z0-9_]+$', username): return False
        if username.isdigit(): return False
        return True

    @staticmethod
    def check_github(username):
        if len(username) > 39: return False
        if username.startswith('-') or username.endswith('-'): return False
        if '--' in username: return False
        if not re.match(r'^[a-zA-Z0-9-]+$', username): return False
        return True

    @staticmethod
    def check_instagram(username):
        if len(username) > 30: return False
        if username.startswith('.') or username.endswith('.'): return False
        if '..' in username: return False
        return True
