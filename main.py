import requests
import time
import json
import os
from pprint import pprint


def get_token():
    return '7b23e40ad10e08d3b7a8ec0956f2c57910c455e886b480b7d9fb59859870658c4a0b8fdc4dd494db19099'


def vk_request(method, adds_param={}):
    try:
        params = {
                'access_token': get_token(),
                'v': 5.80,
            }
        params.update(adds_param)

        response = requests.get(
            'https://api.vk.com/method/{}'.format(method), params
        )

        result = response.json()

        time.sleep(0.34)
    except:
        result = {'error': {'error_code': -1, 'error_msg': 'Ошибка выполнения запроса'}}

    return result


def get_user_id(input_data):
    if input_data.isdigit():
        response_json = vk_request('users.get', {'user_id': input_data})
    else:
        response_json = vk_request('users.get', {'screen_name': input_data})

    if 'error' in response_json:
        if response_json['error']['error_code'] == 113:
            print('Введено неверное имя или ID пользователя ВК')
        else:
            print('Ошибка при получении данных пользователя: {} ({})'.format(response_json['error']['error_code'], response_json['error']['error_msg']))
        return ''

    print('Выбранный пользователь ВК: {} {}'.format(response_json['response'][0]['first_name'], response_json['response'][0]['last_name']))
    return response_json['response'][0]['id']


def get_groups(user_id):
    response_json = vk_request('groups.get', {'user_id': user_id})

    if 'error' in response_json:
        print('Ошибка при получении данных о группах пользователя (id {}): {} ({})'.format(user_id, response_json['error']['error_code'], response_json['error']['error_msg']))
        return list()

    return response_json['response']['items']


def get_friends(user_id):
    response_json = vk_request('friends.get', {'user_id': user_id})

    if 'error' in response_json:
        print('Ошибка при получении данных о друзьях пользователя (id {}): {} ({})'.format(user_id, response_json['error']['error_code'], response_json['error']['error_msg']))
        return list()

    return response_json['response']['items']


def get_group_members(group_id):
    response_json = vk_request('groups.getMembers', {'group_id': group_id, 'filter': 'friends'})

    if 'error' in response_json:
        print('Ошибка при получении данных об участниках группы (id {}): {} ({})'.format(group_id, response_json['error']['error_code'], response_json['error']['error_msg']))
        return 0

    return response_json['response']['count']


def get_group_info(group_id):
    response_json = vk_request('groups.getById', {'group_id': group_id, 'fields': 'members_count'})

    if 'error' in response_json:
        print('Ошибка при получении данных о группе (id {}): {} ({})'.format(group_id, response_json['error']['error_code'], response_json['error']['error_msg']))
        return {'name': '', 'members_count': 0}

    if not 'members_count' in response_json['response'][0]:
        response_json['response'][0]['members_count'] = 0

    if not 'members_count' in response_json['response'][0]:
        response_json['response'][0]['members_count'] = 0

    if 'deactivated' in response_json['response'][0]:
        response_json['response'][0]['name'] += ' #{}'.format(response_json['response'][0]['deactivated'])

    return response_json['response'][0]


def write_json_file(secret_gropus):
    current_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        with open(os.path.join(current_dir, 'groups.json'), 'w', encoding='utf8') as json_file:
            json.dump(secret_gropus, json_file, ensure_ascii=False)
    except OSError:
        return False

    return True


def main_v1(user_id, common_group_friend_count):
    user_friends = get_friends(user_id)

    print()
    print('Формируем список групп друзей...')

    friends_groups = dict()
    friends_count = len(user_friends)

    index = 0
    for friend_id in user_friends:
        index += 1

        print('..{} из {}..'.format(index, friends_count))

        friend_groups = get_groups(friend_id)
        for group_id in friend_groups:
            if group_id in friends_groups:
                friends_groups[group_id] += 1
            else:
                friends_groups[group_id] = 1

    user_groups = set(get_groups(user_id))

    difference = user_groups.difference(friends_groups)
    intersection = user_groups.intersection(friends_groups)

    secret_groups = list()

    print()
    print('Получаем данные о группах...')

    difference_count = len(difference)
    index = 0
    for group_id in difference:
        index += 1

        print('..{} из {}..'.format(index, difference_count))

        info = get_group_info(group_id)

        secret_groups.append(
            {
                'gid': group_id,
                'name': info['name'],
                'members_count': info['members_count']
            }
        )

    common_groups = list()

    for group_id in intersection:
        if friends_groups[group_id] > 0 and friends_groups[group_id] <= common_group_friend_count:
            info = get_group_info(group_id)

            common_groups.append(
                {
                    'name': info['name'],
                    'friends_count': friends_groups[group_id]
                }
            )

    return secret_groups, common_groups


def main_v2(user_id, common_group_friend_count):
    user_groups = get_groups(user_id)

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

        count_friends = get_group_members(group_id)

        if count_friends == 0:
            info = get_group_info(group_id)

            secret_groups.append(
                {
                    'gid': group_id,
                    'name': info['name'],
                    'members_count': info['members_count']
                }
            )
        elif count_friends > 0 and count_friends <= common_group_friend_count:
            info = get_group_info(group_id)

            common_groups.append(
                {
                    'name': info['name'],
                    'friends_count': count_friends
                }
            )

    return secret_groups, common_groups


def main():
    input_data = input('Введите имя или ID пользователя ВК: ')

    if not input_data:
        return

    user_id = get_user_id(input_data)

    if not user_id:
        return

    print()
    common_group_friend_count = input('Введите максимальное количество друзей для выбора общих групп: ')

    if not common_group_friend_count or not common_group_friend_count.isdigit():
        common_group_friend_count = 0
    else:
        common_group_friend_count = int(common_group_friend_count)

    print()
    print('Варианты исполнения программы:')
    print('     1. API friends.get и groups.get с разницей множеств')
    print('     2. API groups.get и groups.getMembers с фильтром friends')
    variant = input('Введите текущий вариант исполнения: ')

    if not variant or not variant.isdigit():
        variant = 1
    else:
        variant = int(variant)

    if variant == 1:
        secret_groups, common_groups = main_v1(user_id, common_group_friend_count)
    else:
        secret_groups, common_groups = main_v2(user_id, common_group_friend_count)

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
