from typing import Self
import pymysql
from jwt import encode, decode
from dataclasses import dataclass
from werkzeug.security import generate_password_hash, check_password_hash
from src.routes.User.validate_curp import Validate
from __init__ import APP
from typing import List, Union
import random
from .banks import BANKS
import uuid

CLABE_LENGTH = 18
CLABE_WEIGHTS = [3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7]


def compute_control_digit(clabe: Union[str, List[int]]) -> str:
    clabe = [int(i) for i in clabe]
    weighted = [
        c * w % 10 for c, w in zip(clabe[: CLABE_LENGTH - 1], CLABE_WEIGHTS)
    ] 
    summed = sum(weighted) % 10
    control_digit = (10 - summed) % 10
    return str(control_digit)

def validate_clabe(clabe: str) -> bool:
    return (
        clabe.isdigit()
        and len(clabe) == CLABE_LENGTH
        and clabe[:3] in BANKS.keys()
        and clabe[-1] == compute_control_digit(clabe)
    )

def generate_new_clabes(number_of_clabes: int, prefix: str) -> List[str]:
    clabes = []
    missing = CLABE_LENGTH - len(prefix) - 1
    assert (10**missing - 10 ** (missing - 1)) >= number_of_clabes
    clabe_sections = random.sample(
        range(10 ** (missing - 1), 10**missing), number_of_clabes
    )
    for clabe_section in clabe_sections:
        clabe = prefix + str(clabe_section)
        clabe += compute_control_digit(clabe)
        assert validate_clabe(clabe)
        clabes.append(clabe)
    return clabes

@dataclass
class Database:

    user = 'root'
    password = ''
    host = 'localhost'
    database = 'bmc'

    def __post_init__(self):
        self.connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            cursorclass=pymysql.cursors.DictCursor
        )

    def query(self, query, params=None):
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
        
    def execute(self, query, params=None):
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            self.connection.commit()
            return True
        
    def close(self):
        self.connection.close()


@dataclass
class User:

    db = Database()
    data: dict = None

    def login(self):
        if not all(key in self.data for key in ['email', 'password']):
            return {'error': 'Invalid data'}

        try:
            user = self.db.query('SELECT * FROM users WHERE email = %s', self.data['email'])
            password_correct = check_password_hash(user[0]['password'], self.data['password'])

            if not password_correct:
                return {'error': 'Invalid password'}
            
            return {'token':encode({'email':self.data['email']}, APP.config['SECRET_KEY'], algorithm='HS256')}
        except:
            return {'error': 'Invalid email'}



    def register(self):
        if not all(key in self.data for key in ['email', 'password', 'name', 'lastName', 'curp']):
            return {'error': 'Invalid data'}

        user = self.db.query('SELECT * FROM users WHERE email = %s or curp = %s', (self.data['email'], self.data['curp']))

        if user:
            return {'error': 'User already exists'}
        
        passwd = generate_password_hash(self.data['password'])
        self.db.execute('INSERT INTO users (name, lastName, email, password, curp) VALUES (%s, %s, %s, %s, %s)', (self.data['name'], self.data['lastName'], self.data['email'], passwd, self.data['curp']))
        # Create an account for the user
        clabes = generate_new_clabes(1, '0021')
        self.db.execute('INSERT INTO cuenta (accountNumber, balance, userid) VALUES (%s, %s, %s)', (clabes[0], 0, self.data['curp']))


        return self.login()
        
    def get_user(self, token):
        email = decode(token, APP.config['SECRET_KEY'], algorithms=["HS256"])
        print(email)
        result = self.db.query('SELECT * FROM users WHERE email = %s', email['email'])
        account = self.db.query('SELECT * FROM cuenta WHERE userid = %s', result[0]['curp'])
        if not result:
            return {'error': 'User not found'}
        print({
            'name': result[0]['name'],
            'lastName': result[0]['lastName'],
            'email': result[0]['email'],
            'curp': result[0]['curp'],
            'account': account[0]['accountNumber'],
            'balance': account[0]['balance']
        })
        return {
            'name': result[0]['name'],
            'lastName': result[0]['lastName'],
            'email': result[0]['email'],
            'curp': result[0]['curp'],
            'account': account[0]['accountNumber'],
            'balance': account[0]['balance']
        }
    
    def get_account_information(self):
        if not all(key in self.data for key in ['account']):
            return {'error': 'Invalid data'}
        
        account = self.db.query('SELECT * FROM cuenta WHERE accountNumber = %s', self.data['account'])
        if not account:
            return {'error': 'Account not found'}
        
        information = self.db.query('SELECT * FROM users WHERE curp = %s', account[0]['userid'])
        if not information:
            return {'error': 'User not found'}
        
        return {
            'name': information[0]['name'],
            'lastName': information[0]['lastName'],
            'email': information[0]['email'],
            'curp': information[0]['curp']
        }
    

@dataclass
class Operations:

    db = Database()
    transaction_id = str(uuid.uuid4())
    data: dict = None

    def deposit(self):
        if not all(key in self.data for key in ['account', 'amount']):
            return {'error': 'Invalid data'}
        
        account = self.db.query('SELECT * FROM cuenta WHERE accountNumber = %s', self.data['account'])
        if not account:
            return {'error': 'Account not found'}
        
        self.db.execute('UPDATE cuenta SET balance = %s WHERE accountNumber = %s', (account[0]['balance'] + self.data['amount'], self.data['account']))
        self.db.execute('INSERT INTO transactions (transactionId, type, amount, accountNumber) VALUES (%s, %s, %s, %s)', (self.transaction_id, 'deposit', self.data['amount'], self.data['account']))
        return {'message': 'Deposit successful'}
    
    def withdraw(self):
        if not all(key in self.data for key in ['account', 'amount']):
            return {'error': 'Invalid data'}
        
        account = self.db.query('SELECT * FROM cuenta WHERE accountNumber = %s', self.data['account'])
        if not account:
            return {'error': 'Account not found'}
        
        if account[0]['balance'] < self.data['amount']:
            return {'error': 'Insufficient funds'}
        
        self.db.execute('UPDATE cuenta SET balance = %s WHERE accountNumber = %s', (account[0]['balance'] - self.data['amount'], self.data['account']))
        self.db.execute('INSERT INTO transactions (transactionId, type, amount, accountNumber) VALUES (%s, %s, %s, %s)', (self.transaction_id, 'withdraw', self.data['amount'], self.data['account']))
        return {'message': 'Withdraw successful'}
    
    def transfer(self):
        if not all(key in self.data for key in ['account', 'amount', 'accountTo']):
            return {'error': 'Invalid data'}
        
        account = self.db.query('SELECT * FROM cuenta WHERE accountNumber = %s', self.data['account'])
        if not account:
            return {'error': 'Account not found'}
        
        account_to = self.db.query('SELECT * FROM cuenta WHERE accountNumber = %s', self.data['accountTo'])
        if not account_to:
            return {'error': 'Account not found'}
        
        if account[0]['balance'] < self.data['amount']:
            return {'error': 'Insufficient funds'}
        
        self.db.execute('UPDATE cuenta SET balance = %s WHERE accountNumber = %s', (account[0]['balance'] - self.data['amount'], self.data['account']))
        self.db.execute('UPDATE cuenta SET balance = %s WHERE accountNumber = %s', (account_to[0]['balance'] + self.data['amount'], self.data['accountTo']))
        self.db.execute('INSERT INTO transactions (transactionId, type, amount, accountNumber) VALUES (%s, %s, %s, %s)', (self.transaction_id, 'send transfer', self.data['amount'], self.data['account']))
        self.db.execute('INSERT INTO transactions (transactionId, type, amount, accountNumber) VALUES (%s, %s, %s, %s)', (self.transaction_id, 'transfer received', self.data['amount'], self.data['accountTo']))
        return {'message': 'Transfer successful'}
    
    def save_transactions(self):
        if not all(key in self.data for key in ['token', 'amount', 'type', 'date']):
            return {'error': 'Invalid data'}
    
        email = decode(self.data['token'], APP.config['SECRET_KEY'], algorithms=["HS256"])
        result = self.db.query('SELECT * FROM users WHERE email = %s', email['email'])
        account = self.db.query('SELECT * FROM cuenta WHERE userid = %s', result[0]['curp'])

        if not result:
            return {'error': 'User not found'}
        
        self.db.execute('UPDATE cuenta SET balance = %s WHERE accountNumber = %s', (str(int(account[0]['balance']) + self.data['amount']), account[0]['accountNumber']))
        self.db.execute('INSERT INTO transactions (transactionId, type, amount, account) VALUES (%s, %s, %s, %s)', (self.transaction_id, self.data['type'], self.data['amount'], account[0]['accountNumber']))
        return {'message': 'Transaction saved'}

