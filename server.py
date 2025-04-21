from flask import Flask, request, jsonify
import logging


app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    return jsonify(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:

        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ],
            "animal": "слон"
        }

        res['response']['text'] = f'Привет! Купи {sessionStorage[user_id]["animal"]}а!'

        res['response']['buttons'] = get_suggests(user_id)
        return

    if req['request']['original_utterance']:
        for word in (req['request']['original_utterance'].lower()).split():
            if word == "не":
                return
            if word in ["ладно", "куплю", "хорошо", "покупаю"]:
                res['response']['text'] = f'{sessionStorage[user_id]["animal"].upper()}а можно найти на Яндекс.Маркете!'
                res['response']['end_session'] = True
                return

    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи {sessionStorage[user_id]['animal']}а!"
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        if sessionStorage[user_id]["animal"] == "слон":
            suggests.append({
                "title": "Ладно",
                "url": "https://market.yandex.ru/search?text=слон",
                "hide": True
            })

            sessionStorage[user_id]["animal"] = "кролик"
        else:
            suggests.append({
                "title": "Ладно",
                "url": "https://market.yandex.ru/search?text=кролик",
                "hide": True
            })
            sessionStorage[user_id]["animal"] = "слон"

    return suggests


if __name__ == '__main__':
    app.run()