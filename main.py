import requests
import time
import json
import os


def get_token():
    return '7b23e40ad10e08d3b7a8ec0956f2c57910c455e886b480b7d9fb59859870658c4a0b8fdc4dd494db19099'


# функция выполняющая произвольный метод API ВК
def vk_request(method, user_id, adds_param={}):
    try:
        # параметры для выполнения запросов к API по умолчанию
        params = {
                'access_token': get_token(),
                'v': 5.80,
            }
        # дополняем параметры используемые для отдельных методов
        params.update(adds_param)

        # если в качестве параметра идентификации пользователя не передается имя, то используем идентификацию по ID
        if not 'screen_name' in params:
            params['user_id'] = user_id

        # выполняем запрос
        response = requests.get(
            'https://api.vk.com/method/{}'.format(method), params
        )

        result = response.json()

        # включаем задержку в 1/3 секунды (максимальная частота запросов для ВК)
        time.sleep(0.34)
    except:
        result = {'error': {'error_code': -1, 'error_msg': 'Ошибка выполнения запроса'}}

    return result


def get_user_id(input_data):
    if input_data.isdigit():
        response_json = vk_request('users.get', input_data)
    else:
        response_json = vk_request('users.get', input_data, {'screen_name': input_data})

    if 'error' in response_json:
        if response_json['error']['error_code'] == 113:
            print('Введено неверное имя или ID пользователя ВК')
        else:
            print('Ошибка при получении данных пользователя: {} ({})'.format(response_json['error']['error_code'], response_json['error']['error_msg']))
        return ''

    print('Выбранный пользователь ВК: {} {}'.format(response_json['response'][0]['first_name'], response_json['response'][0]['last_name']))
    return response_json['response'][0]['id']


def groups_get(user_id):
    response_json = vk_request('groups.get', user_id) # , {'count': 1000}

    if 'error' in response_json:
        print('Ошибка при получении данных о группах пользователя (id {}): {} ({})'.format(user_id, response_json['error']['error_code'], response_json['error']['error_msg']))
        return list()

    return response_json['response']['items']


def members_groups_get(group_id):
    response_json = vk_request('groups.getMembers', 0, {'group_id': group_id, 'filter': 'friends'})

    if 'error' in response_json:
        print('Ошибка при получении данных об участниках группы (id {}): {} ({})'.format(group_id, response_json['error']['error_code'], response_json['error']['error_msg']))
        return list()

    return response_json['response']['count']


def info_groups_get(group_id):
    response_json = vk_request('groups.getById', 0, {'group_id': group_id, 'fields': 'members_count'})

    if 'error' in response_json:
        print('Ошибка при получении данных о группе (id {}): {} ({})'.format(group_id, response_json['error']['error_code'], response_json['error']['error_msg']))
        return list()

    return response_json['response'][0]


def write_json_file(secret_gropus):
    current_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        with open(os.path.join(current_dir, 'groups.json'), 'w', encoding='utf8') as json_file:
            json.dump(secret_gropus, json_file, ensure_ascii=False)
    except OSError:
        return False

    return True


def main():
    input_data = input('Введите имя или ID пользователя ВК: ')

    if not input_data:
        return

    user_id = get_user_id(input_data)

    if not user_id:
        return

    user_groups = groups_get(user_id)

    print()
    common_group_friend_count = input('Введите максимальное количество друзей для выбора общих групп: ')

    if not common_group_friend_count:
        common_group_friend_count = 0
    elif not common_group_friend_count.isdigit():
        common_group_friend_count = 0
    else:
        common_group_friend_count = int(common_group_friend_count)

    groups_count = len(user_groups)

    secret_groups = list()
    common_groups = list()

    print()
    print('Проверяем группы пользователя...')

    index = 0
    for group_id in user_groups:
        index += 1

        print('..'
              '{} из {}..'.format(index, groups_count))

        count_friends = members_groups_get(group_id)

        if count_friends == 0:
            info = info_groups_get(group_id)

            secret_groups.append(
                {
                    'gid': group_id,
                    'name': info['name'],
                    'members_count': info['members_count']
                }
            )
        elif count_friends > 0 and count_friends <= common_group_friend_count:
            info = info_groups_get(group_id)

            common_groups.append(
                {
                    'name': info['name'],
                    'friends_count': count_friends
                }
            )

    if len(secret_groups) > 0:
        print()
        print('Секретные группы:')
        for group_info in secret_groups:
            print('     "{}", участников: {}'.format(group_info['name'], group_info['members_count']))
        print('Всего секретных групп: {}'.format(len(secret_groups)))

        if write_json_file(secret_groups):
            print('Результат записан в файл: groups.json')

    if len(common_groups) > 0:
        print()
        print('Общие группы:')
        for group_info in common_groups:
            print('     "{}", друзей: {}'.format(group_info['name'], group_info['friends_count']))
        print('Всего общих групп: {}'.format(len(common_groups)))

    print()
    print('Работа завершена.')



print('Подсказки для проверки:')
print('     1594412 - мой ID')
print('     171691064 или eshmargunov - данные по дипломному заданию')
print()

main()
