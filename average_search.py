def average_search(select_date, args, cursor):
    val = ({'mes': select_date, 'cp_curr': args[0], 'curr': args[1]})
    select_query = '''SELECT price FROM bitcoin WHERE date_trunc('day', DATE_TIME) = %(mes)s AND CP_CURR = %(cp_curr)s AND CURR = %(curr)s'''
    cursor.execute(select_query, val)
    result = cursor.fetchall()
    list_res = []
    for el in result:
        list_res.append(el[0])
    response = sum(list_res)/len(list_res)
    return response