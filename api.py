# coding=utf-8
import json

import streamlit as st

from lawyer_helper.fee_calc.fee_calculator import LeveLHolder

fee_rate = {1: (0.3, 0.10), 2: ('ignore', 0.06),
            3: ('ignore', 0.04), 4: ('ignore', 0.02),
            # 5: ('ignore', 0.03), 6: ('ignore', 0.02)
            }
st.markdown('# Lawer Helper')
# num_dict = st.sidebar.text_input('please type in settings', value=json.dumps(fee_rate))
num_dict = fee_rate
LH = LeveLHolder(conf='settings.csv', fee_rate=fee_rate)


def set_rate(upper, lower, label, value=None):
    key = label
    return st.sidebar.slider(label, max_value=upper, min_value=lower, value=value, key=key)


def set_base_lower(label='base_lower', value=0.3):
    key = label
    return st.sidebar.number_input(label, value=value, key=key)


def base_ratio_table(thershold=None):
    # st.write(thershold)
    if thershold is None:
        pass
    else:
        raw = LH.raw_conf
        old = raw[raw['level'] == 1]['base'].values[0]
        if old == thershold:
            st.write('old')
            pass
        else:
            st.write('thershold')
            raw.loc[0, 'base'] = thershold
            LH.raw_conf = raw

    show_df = LH.raw_conf.set_index('level').drop('bound', axis=1)

    st.sidebar.dataframe(show_df)
    return show_df

def tes(show_df, thershold=0.3):
    new = {}
    for level, d in show_df.groupby('level'):
        u = d['rate_upper'].values[0]
        l = d['rate_lower'].values[0]
        v = set_rate(u, l, 'Set up Level ' + str(level) + ' fee rate')
        if level == 1:
            t = (thershold, v)
        else:
            t = ('ignore', v)
        new[level] = t
    return new


thershold = set_base_lower(label='最低费用')
show_df = base_ratio_table(thershold=thershold)
new = tes(show_df, thershold=thershold)
# st.write(new)
num = st.number_input('请输入总金额：')
_holder, c = LH.calc(num, fee_rate=new).sum()
st.write(_holder)
st.write(c)

if __name__ == '__main__':
    pass
