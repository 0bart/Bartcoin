import requests
chain = [
    {
        "index": 1,
        "previous_hash": 1,
        "proof": 100,
        "timestamp": 1521570522,
        "transactions": []
    },
    {
        "index": 2,
        "previous_hash": "84b558790f42980000b23555e0d32a47d1e2e0807a09d3f7c516a27f7a14490d",
        "proof": 106201,
        "timestamp": 1521570535,
        "transactions": [
            {
                "vin": [
                    {
                        "recipient": "BNaG6u4G1t5MzFTtTTDi6p5px2dnLDBFjY",
                        "sender": "coinbase"
                    }
                ],
                "vout": [
                    {
                        "value": 1
                    },
                    {
                        "value": -1
                    }
                ]
            }
        ]
    },
    {
        "index": 3,
        "previous_hash": "beea8d7cc9f9bff979c2543ccfcb150cd0157b31f042426e7f83f2796d6be3f7",
        "proof": 204892,
        "timestamp": 1521570560,
        "transactions": [
            {
                "vin": [
                    {
                        "recipient": "B9UF6n3FPSA9F9TqnizP87o1k7ARqWXiFG",
                        "sender": "BNaG6u4G1t5MzFTtTTDi6p5px2dnLDBFjY"
                    }
                ],
                "vout": [
                    {
                        "value": 0.1
                    },
                    {
                        "value": 0.9
                    }
                ]
            },
            {
                "vin": [
                    {
                        "recipient": "BNaG6u4G1t5MzFTtTTDi6p5px2dnLDBFjY",
                        "sender": "coinbase"
                    }
                ],
                "vout": [
                    {
                        "value": 1
                    },
                    {
                        "value": -2
                    }
                ]
            }
        ]
    }
]

def new_transaction():
    transaction_dict = {
        'sender': 'BHq53892yc22W43BKDtRFXWnV6dXiXkGpR',
        'recipient': 'BCt4usUmYo9c3SV8BcGUsGGWFUkWxpKGHy',
        'amount': 0.1,
        'sign': '0x3fa0acbf6bc27d7b7bb9d775c1528913e5be4ec4c51460aab93b9e21bef3be22',
    }
    try:
        response = requests.post(f'http://127.0.0.1:5000/transaction/new', json=transaction_dict, timeout=3)
        print("ODP")
        print(response.text)
    except requests.exceptions.Timeout:
        print("Sth went wrong")

    print("DONE")

new_transaction()