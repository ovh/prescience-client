import base64
import json
import re

from prescience_client.bean.entity.w10_ts_input import TimeSerieFeature


class Warp10Util:
    @staticmethod
    def generate_warp10_query(token: str, input_ts: TimeSerieFeature, interval: str, horizon: int):
        labels_string = '{ '
        for key, val in input_ts.labels.items():
            labels_string += f'\'{key}\' \'{val}\''
        labels_string += ' }'

        interval_string = Warp10Util.split_interval(interval)

        return f'[ \n' \
               f' \'{token}\' \n' \
               f' \'~{input_ts.selector}.*\' \n' \
               f' {labels_string} \n' \
               f' NOW {interval_string} {horizon} * + {interval_string} 10 {horizon} + * \n' \
               f' ] FETCH'

    @staticmethod
    def generate_warp10_quantum_query(query, backend):
        backend_json = json.dumps({
            "url": f"{backend}/api/v0",
            "fetchEndpoint": "/fetch",
            "headerName": "X-Warp10"
        })
        backend_b64 = base64.b64encode(backend_json.encode('utf-8')).decode('ascii')
        query_b64 = base64.b64encode(query.encode('utf-8')).decode('ascii')
        return f'https://quantum-ovh.metrics.ovh.net/#/warpscript/{query_b64}/{backend_b64}'

    @staticmethod
    def split_interval(s):
        match = re.compile("[^\W\d]").search(s)
        number = s[:match.start()]
        letter = s[match.start():]
        return f'{number} {letter}'
