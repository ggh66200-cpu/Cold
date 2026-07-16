import time, utils

def check_user(user_id):
    data = utils.get_data()
    uid = str(user_id)
    
    if uid not in data['users'] or not isinstance(data['users'][uid], dict):
        if uid not in data['users']:
            data['total_count'] += 1
        data['users'][uid] = {"join_date": time.time(), "lang": "ar"}
        utils.save_data(data)
        return True, data['total_count']
    
    user_record = data['users'][uid]
    if 'join_date' not in user_record:
        user_record['join_date'] = time.time()
        utils.save_data(data)
    
    # مفتوح دائمياً للفحص والتطوير حالياً
    return True, data['total_count']
