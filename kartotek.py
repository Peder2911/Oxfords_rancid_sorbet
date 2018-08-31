#!/usr/bin/env python

import sqlite3 as sq
import json
import sys
import os
import fire
import logging
from datetime import datetime


class main():
    def setup(self):

        try:
            os.mkdir('data')
        except FileExistsError:
            pass

        con = sq.connect('data/kartotek.db')
        c = con.cursor()
        c.execute('''CREATE TABLE note (i int,
                                      note text,
                                      tags text,
                                      date text,
                                      ref text)''')
        c.execute('''CREATE TABLE source (i text,
                                          title text,
                                          author text,
                                          pubdate text)''')
        con.commit()

    def add(self,s = False):
        con = sq.connect('data/kartotek.db')

        entry = {}
        if not s:
            tab = 'note'

            c = con.cursor()
            c.execute('SELECT i FROM note')
            indices = [v[0] for v in c.fetchall()]
            entry['i'] = findIndex(indices)

            entry['note'] = input('enter note:\n')
            entry['tags'] = input('enter tags:\n')
            entry['date'] = datetime.now().isoformat()[:10]
            entry['ref'] = input('enter ref:\n')
        else:
            tab = 'source'
            entry['title'] = input('enter title:\n')
            entry['author'] = input('enter author:\n')
            entry['pubdate'] = input('enter pubdate:\n')
            entry['i'] = input('enter reference:\n')

        dbAdd(con,tab,entry)

        con.commit()

    def show(self):
        con = sq.connect('data/kartotek.db')

        showNotes(con)

'''
Functions for handling the SQLite database containing the data.
'''
#####################################
logging.basicConfig(level = 0)
cl = logging.getLogger('console')
cl.setLevel('DEBUG')
#####################################

def dbAdd(con,table,entry):
    c = con.cursor()

    columns = entry.keys()
    columns = ','.join(columns)
    values = ['\"%s\"'%(v) for v in entry.values()]
    values = ','.join(values)

    q = 'INSERT INTO {table} ({columns}) VALUES ({values})'
    q = q.format(
            table = table,
            columns = columns,
            values = values
            )

    cl.debug(q)

    c.execute(q)

    con.commit()

def dbGet(con,table,condition = None):
    c = con.cursor()
    q = 'SELECT * FROM {table}'
    q = q.format(
            table = table
            )
    if condition is not None:
        q += ' WHERE ({condition})'
        q = q.format(condition = condition)

    cl.debug(q)

    c.execute(q)
    dat = c.fetchall()

    return(dat)

#####################################

def dbColnames(con,table):
    c = con.cursor()
    c.execute('PRAGMA table_info(%s)'%(table))
    names = [v[1] for v in c.fetchall()]
    return(names)

def showTable(con,table,condition = None):
    data = dbGet(con,table,condition)

    c = con.cursor()
    c.execute('PRAGMA table_info(%s)'%(table))
    colnames = [v[1] for v in c.fetchall()]
    present(data,colnames)

def showNotes(con,condition = None):
    c = con.cursor()

    notes = dbGet(con,'note',condition)
    noteNames = dbColnames(con,'note')

    refNotes = []
    sourcesNames = dbColnames(con,'source')
    for note in notes:
        ref = note[noteNames.index('ref')]
        c.execute('SELECT * FROM source WHERE i = \"%s\"'%(ref))
        res = c.fetchone()

        if res is not None:
            source = res
        else:
            ncol = len(sourcesNames)
            source = tuple(['' for i in range(ncol)])

        refNotes.append(tuple(list(note)+list(source)))

    refNotesNames = noteNames + sourcesNames
    present(refNotes,refNotesNames)


def present(data,colnames):
    for entry in data:
        print('\n'+'#'*38+'\n')
        i = entry[colnames.index('i')]

        print('--- ' + str(i))

        for i,name in enumerate(colnames):
            if name != 'i':
                print(name + ':')
                print('\t'+str(entry[i]))

#####################################

def search(con,table,search):
    c = con.cursor()
    q = 'SELECT * FROM {table}'
    q.format(
        table = table
        )

    c.execute(q)
    dat = c.fetchall()
    dat = fSearch(dat,search)

    return(dat)

def findIndex(indices):
    index = 1
    while index in indices:
        index += 1
    return(index)

if __name__ == '__main__':
    fire.Fire(main)
