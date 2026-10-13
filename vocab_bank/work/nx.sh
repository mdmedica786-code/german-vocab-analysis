#!/bin/bash
# usage: nx.sh <bank> <n> [args]  -> compact next output
cd "$(dirname "$0")/.." && export PYTHONUTF8=1
python3 work/bank_tools.py next "$@" | sed -n '/pending in selection/,$p' | sed -e "s/ | register=neutral//; s/ | level_basis=netzwerk//; s/ | nw_chapter=/ | ch=/; s/ | freq_rank=[0-9]*//; s/ | kind=\(noun\|verb\|word\) / /; s/topic=T\([0-9]*\)[^|]*|/tp=T\1 |/; s/ | example_en=/ | en=/; s/ | example_de=/ | ex=/; s/ | meaning_en=/ | m=/" | cut -c1-360
