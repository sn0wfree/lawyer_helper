# coding=utf-8
import json

import streamlit as st

from lawyer_helper.fee_calc.fee_calculator import LeveLHolder


st.markdown('test')
num_dict = st.text_input('please type in settings')
# num_dict = json.load(num_dict)
# LH = LeveLHolder(fee_rate=num_dict)


if __name__ == '__main__':
    pass
