#!/usr/bin/env python3

import os, collections, asyncio, logging

import aiosqlite

log = logging.getLogger(__file__)

# TODO : move Offer namedtuple
Offer = collections.namedtuple('JobOffer', 'title company salary location \
                                         type_ date txt url link skills',
                                         defaults=(0,))

# TODO : move aioObject somewhere else
class aioObject(object):
    """ Inheriting this class allows you to define an async __init__.
    So you can create objects by doing something like 'await MyClass(params)'
    https://stackoverflow.com/questions/33128325/how-to-set-class-attribute-with-await-in-init
    """
    async def __new__(cls, *a, **kw):
        instance = super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self):
        pass

class AsyncDB(aioObject):
    """ Async aiosqlite database """
    
    async def __init__(self, name):
        # get current dir
        dir = dir = os.path.dirname(os.path.realpath(__file__))
        # build database dir 
        self.name = f'{dir}/data/{name}' 
    
        self.con = None
        self.cursor = None

        # create table on init
        await self.create_table()

    def work(func):
        """ Async decorator: opening the database in a context manager before use """
        async def _wraper(*args):
            # decorator in class : extract self from function args
            self = args[0]
            # open connection in a context manager
            async with aiosqlite.connect(self.name) as self.con:
                self.cursor = await self.con.cursor()
                return await func(*args)
        return _wraper

    @work
    async def create_table(self):
        """ Create the database's tables if they do not exist"""
        await self.cursor.execute('''CREATE TABLE if not exists Jobs (
                                        title, company, salary, location, type, 
                                        date, description, url, apply_link, skills)''')
        return await self.con.commit()

    @work
    async def insert(self, offer):
        """ Insert row into the database """
        insert = "INSERT INTO Jobs VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )"
        try:
            await self.cursor.execute(insert, (offer.title, offer.company, f'{offer.salary}',
                                            offer.location, offer.type_, offer.date,
                                            offer.txt, offer.url, offer.link, f'{offer.skills}'))
        except aiosqlite.OperationalError:
            print(f"Insert error with : {offer}")
        
        except AttributeError:
            print(f"Insert error with : {offer}")
        return await self.con.commit()

    @work
    async def get_all(self):
        select = "SELECT * FROM Jobs"
        await self.cursor.execute(select)
        return await self.cursor.fetchall()
    

if __name__=="__main__":
    import sys

    extension = '.db'

    name = ''
    try:
        name = sys.argv[1] + extension
    except IndexError:
        print("Name of the database as first argument")
        exit(1)

    # define async test function 
    async def test(name):
        db = await AsyncDB(name)
        log.info("Database created in /data")
    
    # run test function
    asyncio.run(test(name))
