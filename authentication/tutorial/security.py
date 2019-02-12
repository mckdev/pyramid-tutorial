import bcrypt


def hash_password(pw):
    pwhash = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
    return pwhash.decode('utf-8')


def check_password(pw, hashed_pw):
    expected_hash = hashed_pw.encode('utf-8')
    return bcrypt.checkpw(pw.encode('utf-8'), expected_hash)


USERS = {'editor': hash_password('editor'),
         'viewer': hash_password('viewer')}
GROUPS = {'editor': ['group:editors']}


def groupfinder(userid, request):
    if userid in USERS:
        return GROUPS.get(userid, [])
