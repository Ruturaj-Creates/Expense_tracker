#sqllite functions
import sqlite3
from datetime import datetime

class ExpenseDB:
    def __init__(self, db_file='expenses.db'):
        self.db_file=db_file
        self.init_db()

    def get_connection(self):
        '''Get database connection'''
        conn = sqlite3.connect(self.db_file)
        conn.row_factory=sqlite3.Row
        return conn
    
    def init_db(self):
        '''create tables if don't exist'''
        conn=self.get_connection()
        cursor=conn.cursor()

        #user table
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS users(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       telegram_id TEXT UNIQUE NOT NULL,
                       name TEXT,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
                        ''')
        
        #expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       user_id INTEGER NOT NULL,
                       amount REAL NOT NULL,
                       category TEXT,
                        description TEXT,
                       date DATE NOT NULL,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY (user_id) REFERENCES users(id)
                       )
        ''')
        conn.commit()
        conn.close()

    def get_or_create_user(self,telegram_id,name):
        ''''get user or create user'''
        conn=self.get_connection()
        cursor=conn.cursor()

        #check if user exists
        cursor.execute('SELECT id FROM users WHERE telegram_id =?',(telegram_id,))
        result=cursor.fetchone()

        if result:
            conn.close()
            return result[0]
        # create new user
        cursor.execute(
            'INSERT INTO users (telegram_id,name) VALUES (?,?)',
            (telegram_id,name)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    
    def add_expense(self,user_id, amount,category,description):
        """add new expense"""
        conn=self.get_connection()
        cursor=conn.cursor()

        today = datetime.now().date()
        cursor.execute('''
              INSERT INTO expenses (user_id,amount,category,description,date)
              VALUES(?,?,?,?,?)
            ''',(user_id,amount,category,description,today))
        conn.commit()
        conn.close()

    def get_daily_total(self,user_id):
        """get today's total spending"""
        conn=self.get_connection()
        cursor=conn.cursor()

        today=datetime.now().date()
        cursor.execute('''
                SELECT SUM(amount) FROM expenses
                WHERE user_id =? AND date =?
                       ''',(user_id,today))
        result=cursor.fetchone()[0] or 0 
        conn.close()
        return result

    def get_category_total(self,user_id,category):
        """get spending by category (today)""" 
        conn= self.get_connection()
        cursor=conn.cursor()

        today=datetime.now().date()
        cursor.execute('''
                SELECT SUM(amount) FROM expenses
                WHERE user_id=? AND category=? AND date=? 
                        ''',(user_id,category,today))
        result = cursor.fetchone()[0] or 0
        conn.close()
        return result
    
    def get_all_expenses(self, user_id, days=7):
        """get expenses from last N days"""
        from datetime import datetime, timedelta
        
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get ALL expenses for this user
        cursor.execute('''
                SELECT date, category, amount, description FROM expenses
                WHERE user_id = ?
                ORDER BY date DESC        
        ''', (user_id,))
        
        all_expenses = cursor.fetchall()
        conn.close()
        
        # Filter by days in Python
        cutoff_date = (datetime.now() - timedelta(days=days)).date()
        filtered = [e for e in all_expenses if str(e[0]) >= str(cutoff_date)]
        
        return filtered