#!/usr/bin/env python

import csv
from googletrans import Translator
from Levenshtein import jaro
import getpass
import fbchat
from datetime import datetime,timedelta
import sys

translator = Translator()

templates = []
with open('templates.txt') as f:
    template = []
    for line in f:
        if not line.strip():
            if len(template):
                templates.append('\n'.join(template))
                template = []
        else:
            template.append(line.strip())
    if len(template):
        templates.append('\n'.join(template))
        template = []

def is_arabic(name):
    for c in name:
        if c == ' ' or 0x0600 < ord(c) < 0x06FF or 0xFE00 < ord(c) < 0xFEFF:
            # arabic charachter
            continue
        else:
            return False
    return True

def get_name(friend):
    name = friend.name.lower()
    first_name = friend.first_name.lower()
    gender = friend.gender
    return _get_name(name, first_name, gender)

def _get_name(name, first_name, gender):
    for prefix in ('eng', 'dr', 'hr', 'phd'):
        if first_name.startswith(prefix + ' '):
            first_name = first_name[len(prefix) + 1:]
    first_name = first_name.replace(' ', '')
    if first_name in ('abd', 'abdel', 'عبد') or first_name == '':
        ns = name.split(' ')
        segs = []
        for s in ns:
            segs.append(s)
            if s not in ('abd', 'el', 'عبد'):
                break
        first_name = ' '.join(segs).replace(' ', '')

    if is_arabic(first_name):
        return first_name

    if 'female' in gender:
        gender = 'female'
    elif 'male' in gender:
        gender = 'male'
    if gender == 'unknown':
        if first_name in males_en or first_name in males:
            gender = 'male'
        elif first_name in females_en or first_name in females:
            gender = 'female'

    if gender == 'unknown':
        nearest = -1
        nearest_gender = 'unknown'
        for en_name in males_en:
            similarity = jaro(first_name, en_name)
            if similarity > nearest:
                nearest_gender = 'male'
                nearest = similarity
            if similarity == nearest and nearest_gender == 'female':
                nearest_gender = 'unknown'
        for en_name in females_en:
            similarity = jaro(first_name, en_name)
            if similarity > nearest:
                nearest_gender = 'female'
                nearest = similarity
            if similarity == nearest and nearest_gender == 'male':
                nearest_gender = 'unknown'
        gender = nearest_gender

    d = males if gender == 'male' else females if gender == 'female' else unknowns
    if first_name in d:
        return d[first_name]

    res = translator.translate(first_name, dest='ar', src='en').text
    d[first_name] = res
    return res

def load_csv(file_name):
    with open(file_name, newline='') as f:
        return {i[0]:i[1] for i in csv.reader(f)}

def save_csv(file_name, iterable):
    with open(file_name, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(iterable)
    
males = load_csv('males.csv')
original_males = set(males.keys())
females = load_csv('females.csv')
original_females = set(females.keys())
unknowns = {}
original_unknowns = set()
    
females_en = load_csv('ArabicNameGenderFinder/females_en.csv')
males_en = load_csv('ArabicNameGenderFinder/males_en.csv')

year_ago = datetime.now() - timedelta(days=365)

def prepare(c):
    threads = []
    ts = c.fetchThreadList()
    threads.extend(ts)
    while len(ts) and int(ts[-1].last_message_timestamp) / 1000 > year_ago.timestamp():
        print('getting older messages')
        ts = c.fetchThreadList(before=int(ts[-1].last_message_timestamp))
        threads.extend(ts)
    friends = [user for user in threads if user.type == fbchat.ThreadType.USER and user.is_friend]

    res = []
    i = 0
    for friend in friends:
        name = get_name(friend)
        if not is_arabic(name):
            print('could not get name for friend %r, got name %r'%(friend.name, name))
            continue
        res.append((friend.uid, friend.name, name, templates[i].format(name=name)))
        i += 1
        i = i % len(templates)

    save_csv('to_be_sent.csv', res)    

    save()

def send(c):
    with open('to_be_sent.csv', newline='') as f:
        for person in csv.reader(f):
            [id, full_name, name, message] = person
            c.sendMessage(message, id)

def save():
    save_csv('new_males.csv', [(k, v) for k, v in males.items() if k not in original_males])
    save_csv('new_females.csv', [(k, v) for k, v in females.items() if k not in original_females])
    save_csv('new_unknowns.csv', [(k, v) for k, v in unknowns.items() if k not in original_unknowns])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise RuntimeError("usage: %s <username> [prepare|send]"%(sys.argv[0]))
    if sys.argv[2] not in ("prepare", "send"):
        raise RuntimeError("second argument must be 'prepare' or 'send'")
    c = fbchat.Client(sys.argv[1], getpass.getpass())
    if sys.argv[2] == "prepare":
        prepare(c)
    elif sys.argv[2] == "send":
        send(c)
