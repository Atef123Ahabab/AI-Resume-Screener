#!/bin/bash
cd "$(dirname "$0")/groq_screener"
python -m streamlit run simple_rank.py
