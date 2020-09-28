import sys
import time
import json
from os import path

def formatTime(t):
    seconds, remainder_of_seconds = t.split('.')
    result = time.strftime('%H:%M:%S', time.gmtime(int(seconds)))
    # fractions of seconds need to be to 3 digits, or Twitter will reject
    return result + "," + remainder_of_seconds.ljust(3, '0')

chunks = []
chunk = {
    'start_time': '',
    'end_time': '',
    'word_index': 1,
    'sentence': ''
}
word_break_limit = 10

if len(sys.argv) < 2:
    sys.exit('Please provide a file name.')

filename = sys.argv[1]

if not path.exists(filename):
    sys.exit('File ' + filename + ' does not exist.')

with open(filename) as f:
  data = json.load(f)

items = data['results']['items']

for i, item in enumerate(items):
    type = item['type']
    content = item['alternatives'][0]['content']

    # if a word, set the start time and end time (the latter is subject to change)
    # then add it to the current chunk         
    if type == "pronunciation":
        if chunk['start_time'] == "":
            chunk['start_time'] = item['start_time']
        chunk['end_time'] = item['end_time']
        # Don't want to start a fresh sentence with a space
        spacer = '' if chunk['word_index'] == 1 else ' '
        chunk['sentence'] = chunk['sentence'] + spacer + content
        chunk['word_index'] = chunk['word_index'] + 1
    
    elif type == "punctuation":
        # Add punctuation
        # But don't increment index
        chunk['sentence'] = chunk['sentence'] + content
    
    # End the caption chunk if
    # - this item is sending punctuation
    # - there are no more items after this one
    # - we hit the word break limit (provided the NEXT item is not punctuation)
    item_is_ending_punctuation = content == '.' or content == '?' or content == '!'
    is_last_item = len(items) - 1 == i
    next_item_is_punctuation = i < len(items) - 1 and items[i+1]['type'] == "punctuation"
    hit_word_break_limit = chunk['word_index'] >= word_break_limit and not next_item_is_punctuation

    if item_is_ending_punctuation or hit_word_break_limit or is_last_item:
        # End of the caption for this chunk
        # Add new empty chunk to end of array
        # and start over (or just exit loop).
        chunks.append(chunk)
        chunk = {
            'start_time': '',
            'end_time': '',
            'word_index': 1,
            'sentence': ''
        }

srt = ''
# Build out srt
for i, chunk in enumerate(chunks):
    chunk_index = str(i + 1)
    srt = srt + chunk_index + "\n"
    srt = srt + formatTime(chunk['start_time']) + " --> " + formatTime(chunk['end_time']) + "\n" + chunk['sentence'] + "\n\n"

print (srt)

