# coding=utf-8
import os
from collections import defaultdict

import numpy as np
import pandas as pd

from lawyer_helper import conf
from lawyer_helper.tools.file_loader import file_loader

AVAILABLE_CONF_TYPE = ('csv',)


class LeveLHolder(object):

    def __init__(self, conf='settings.csv', path=conf.__path__[0], base_or_rate={1: 'base'},
                 fee_rate=None):

        self._conf = conf
        self._conf_type = os.path.splitext(conf)[1].lstrip('.')
        self._check_conf_type()
        self._path = path
        self._fee_rate = self._ensure_fee_rate(fee_rate=fee_rate)
        self.base_or_rate = self._check_base_or_rate(base_or_rate)
        self._raw_conf_data = getattr(self, f'_parse_conf_{self._conf_type}')()
        self._holder = None
        self._create = False

    def _ensure_fee_rate(self, fee_rate=None):
        if fee_rate is None:
            fee_rate = fee_rate = {1: (0.3, 0.08), 2: ('ignore', 0.05),
                                   3: ('ignore', 0.03), 4: ('ignore', 0.01),
                                   # 5: ('ignore', 0.03), 6: ('ignore', 0.02)
                                   }
        else:
            pass

        df = pd.DataFrame.from_dict(fee_rate).T.reset_index().replace('ignore', 0)
        df.columns = ['level', 'base', 'rate']
        return df

    @property
    def _conf_path(self, ):
        file_path = file_loader(conf_file=self._conf, path=self._path)
        # with sqlite3.connect(path)  as f:
        return file_path

    def _check_conf_type(self):
        if self._conf_type in AVAILABLE_CONF_TYPE:
            pass
        else:
            raise ValueError(f'unknown conf_type:{self._conf_type}, only accept:{",".join(AVAILABLE_CONF_TYPE)}')

    @property
    def conf(self):
        raw_conf = self._raw_conf_data[['level', 'lower', 'upper', 'bound']]
        fr = self._fee_rate
        conf = raw_conf.merge(fr, on=['level'])
        return conf

    @property
    def raw_conf(self):
        return self._raw_conf_data

    @raw_conf.setter
    def raw_conf(self, value):
        self._raw_conf_data = value

        pass

    def _parse_conf_csv(self):
        return pd.read_csv(self._conf_path).fillna(0).replace('inf', np.inf)

    @staticmethod
    def _check_base_or_rate(base_or_rate={1: 'base'}):
        base = defaultdict(lambda: 'rate')
        base.update(base_or_rate)
        return base

    def _get_level_df(self, num: (int, float)):
        # get level
        if num < 0:
            raise ValueError('num is negative value which is not supported number')

        level = self.conf[self.conf['lower'] <= num].sort_values('level', ascending=False)
        return level

    def _get_raw_level_df(self, num: (int, float)):
        # get level
        if num < 0:
            raise ValueError('num is negative value which is not supported number')

        level = self.raw_conf[self.raw_conf['lower'] <= num].sort_values('level', ascending=False)
        return level

    def _calc_raw_rest_level(self, rest_level):
        rest_level['upper_lower'] = (rest_level['upper'] - rest_level['lower'])
        rest_level['upper_lower_rate_lower'] = rest_level['upper_lower'] * rest_level['rate_lower']
        rest_level['upper_lower_rate_upper'] = rest_level['upper_lower'] * rest_level['rate_upper']
        cc1 = rest_level[['upper_lower_rate_lower', 'base']].values
        h1 = []
        for c1, c2 in cc1:
            h1.append(max(c1, c2))

        rest_level['sub_fee_lower'] = h1
        cc2 = rest_level[['upper_lower_rate_upper', 'base']].values
        h2 = []
        for c1, c2 in cc2:
            h2.append(max(c1, c2))

        rest_level['sub_fee_upper'] = h2
        return rest_level

    def _calc_rest_level(self, rest_level):
        rest_level['upper_lower'] = (rest_level['upper'] - rest_level['lower'])
        rest_level['upper_lower_rate'] = rest_level['upper_lower'] * rest_level['rate']
        c = rest_level[['upper_lower_rate', 'base']].values
        h = []
        for c1, c2 in c:
            h.append(max(c1, c2))

        rest_level['sub_fee'] = h
        return rest_level

    def _raw_calc(self, num: (int, float)):
        level_df = self._get_raw_level_df(num)
        top_level = level_df.head(1)
        level = top_level['level'].values[0]
        lower = top_level['lower'].values[0]
        rest_level = level_df[level_df['level'] != level]
        top_level['upper'] = num
        level_replaced = pd.concat([rest_level, top_level]).sort_values('level', ascending=True)

        calced_level = self._calc_raw_rest_level(level_replaced)
        result_upper = calced_level['sub_fee_upper'].sum()
        result_lower = calced_level['sub_fee_lower'].sum()

        return calced_level, result_lower, result_upper

    def calc(self, num: (int, float), add_raw=True, fee_rate=None, conf=None):
        if conf is not None:
            self._conf = conf
        if fee_rate is not None:
            self._fee_rate = self._ensure_fee_rate(fee_rate=fee_rate)
        real, r = self._calc(num=num, )
        if add_raw:
            raw, u, l = self._raw_calc(num=num, )
            self._holder = raw.merge(real[['level', 'sub_fee']], on=['level'])
            self._create = True
            return self
        else:
            self._holder = real
            self._create = True
            return self

    def sum(self):
        if self._create:
            print(self._holder)
            if 'sub_fee_upper' in self._holder.columns:
                return self._holder, {'upper': self._holder['sub_fee_upper'].sum(),
                                      'lower': self._holder['sub_fee_lower'].sum(),
                                      'real': self._holder['sub_fee'].sum(),

                                      }
            else:
                return self._holder, {'real': self._holder['sub_fee'].sum(),

                                      }

    def _calc(self, num: (int, float)):

        level_df = self._get_level_df(num)
        top_level = level_df.head(1)

        level = top_level['level'].values[0]
        lower = top_level['lower'].values[0]
        rest_level = level_df[level_df['level'] != level]
        top_level['upper'] = num
        level_replaced = pd.concat([rest_level, top_level]).sort_values('level', ascending=True)

        calced_level = self._calc_rest_level(level_replaced)
        result = calced_level['sub_fee'].sum()

        return calced_level, result


if __name__ == '__main__':
    LH = LeveLHolder(fee_rate={1: (0.3, 0.10), 2: ('ignore', 0.06),
                               3: ('ignore', 0.04), 4: ('ignore', 0.02),
                               # 5: ('ignore', 0.03), 6: ('ignore', 0.02)
                               })

    print(LH.calc(200).sum())

    pass
