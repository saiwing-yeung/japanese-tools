#!/usr/bin/env python3
from myougiden import database
from myougiden import orm
from myougiden import search

import MeCab
mecab = MeCab.Tagger()


input_file = 'memrise-input.txt'
output_file = 'memrise-output.txt'

con, cur = database.opendb(case_sensitive=False)


def make_conditions(the_query):
    base_search_args = { 'query': the_query, 'regexp': False, 'frequent': False,
                            'case_sensitive': False, 'extent': 'whole' }
    c1 = base_search_args
    c1['field'] = 'reading'
    c2 = base_search_args.copy()
    c2['field'] = 'kanji'
    
    conditions = [ c1, c2 ]
    return(conditions)


def get_results(chosen_search, ent_seqs):
    out = ''
    if chosen_search:
        entries = [ orm.fetch_entry(cur, ent_seqs[0]) ]
        out = [ entry.format_human(search_params=chosen_search, romajifn=False) for entry in entries]
        out = ("\n\n".join(out)) + "\n"
    return(out)


def do_format(entry, chosen_search):
    if (len(entry.kanjis) > 0):
        kanji_str = entry.kanjis[0].fmt()
    else:
        kanji_str = entry.readings[0].fmt()
    return("%s %s %s %s" % (kanji_str, entry.senses[0].tagstr(chosen_search), entry.readings[0].fmt(),
                              '; '.join(entry.senses[0].fmt_glosses(chosen_search))))


# Memrise order: Kana, English, Common Japanese, Kanji, Part of Speech, Gender
def do_memrise_format(entry, chosen_search):
    if (len(entry.kanjis) > 0):
        kanji_str = entry.kanjis[0].fmt()
    else:
        kanji_str = entry.readings[0].fmt()
    return('\t'.join((entry.readings[0].fmt(),
                     '; '.join(entry.senses[0].fmt_glosses(chosen_search)),
                     entry.readings[0].fmt(),
                     kanji_str,
                     entry.senses[0].tagstr(chosen_search))))


def search_inner(in_query):
    conditions = make_conditions(in_query)
    chosen_search, ent_seqs = search.guess(cur, conditions)
    return(chosen_search, ent_seqs)


def do_search_by_chunks(in_query):
    str_parsed = mecab.parse(in_query)
    chunk_parsed = str_parsed.split("\n")
    orig_chunks = []
    inflected_chunks = []

    for i in range(len(chunk_parsed)):
        cur_parse = chunk_parsed[i].split("\t")
        if cur_parse[0] == 'EOS':
            break
        cur_chunk = cur_parse[0]
        orig_chunks.append(cur_chunk)
        msg = cur_chunk
        if len(cur_parse) > 1:
            cur_details = cur_parse[1].split(",")
            if len(cur_details) >= 7:
                inflected_chunks.append(cur_details[6])
            else:
                inflected_chunks.append("")
        else:
            inflected_chunks.append("")

    #print("orig_chunks: ", orig_chunks)
    #print("inflected_chunks: ", inflected_chunks)
    for i in reversed(range(len(orig_chunks))):
        if i == len(orig_chunks):
            cur_base = orig_chunks[0]
        else:
            cur_base = "".join(orig_chunks[:i])
        orig_joined = cur_base + orig_chunks[i]
        inflected_joined = cur_base + inflected_chunks[i]
        #print("orig_joined: ", orig_joined)
        #print("inflected_joined: ", inflected_joined)
    
        # try the inflected form
        if inflected_joined != orig_joined:
            chosen_search, ent_seqs = search_inner(inflected_joined)
            if chosen_search:
                break
        # try the original form
        chosen_search, ent_seqs = search_inner(orig_joined)
        if chosen_search:
            break

    return chosen_search, ent_seqs


def do_search(in_query, memrise_order=True):
    chosen_search, ent_seqs = search_inner(in_query)
    if chosen_search == None:
        chosen_search, ent_seqs = do_search_by_chunks(in_query)
            
    if chosen_search:
        result = get_results(chosen_search, ent_seqs)
        entries = [ orm.fetch_entry(cur, ent_seqs[0]) ]
        if memrise_order:
            return(do_memrise_format(entries[0], chosen_search))
        else:
            return(do_format(entries[0], chosen_search))


with open(input_file) as f:
    lines = f.readlines()

proc_lines = [ x.strip() for x in lines ]
out_lines = []

for line in proc_lines:
    base_word = line
    cur_out = do_search(base_word, True)
    print(cur_out)
    out_lines.append(cur_out)

with open(output_file, 'w') as f:
    f.write('\n'.join(out_lines))


print("\nDefinitions of words in %s have been saved in %s a memrise-compatible format." % (input_file, output_file))

