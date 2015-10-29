#!/usr/bin/env python

import psycopg2
import sys

USER = 'kmama02'

ALTER TABLE reviews ALTER COLUMN user_followers TYPE varchar(100);
psql_connection = psycopg2.connect(database='Zodata',  user=USER)

# Open a cursor to perform database operations
cursor = psql_connection.cursor()

# Execute a command: this creates a new table
>>> cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")

query = "CREATE TABLE reviews (__review_id varchar(32) PRIMARY KEY UNIQUE, area_or_city varchar(100), management_response text, review_summary text, \
                        eatery_id varchar(25) NOT NULL, review_time timestamp, review_url text, scraped_epoch integer, user_followers varchar(5), \
                        user_id varchar(20),  user_url text,  review_text text NOT NULL, readable_review_day varchar(3),  review_id integer UNIQUE, \
                        readable_review_month varchar(2),  readable_review_year char(4));"


try:
        cursor.execute(query)
        psql_connection.commit()
except psycopg2.ProgrammingError as e:
        print "Table already exists "




try:
                    cursor.execute("INSERT INTO REVIEWS VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",  (post.get("__review_id"), post.get("area_or_city"), post.get("management_response"), post.get("review_summary"), post.get("eatery_id"), post.get("review_time"), post.get("review_url"), post.get("scraped_epoch"), post.get("user_followers"), post.get("user_id"), post.get("user_url"), post.get("review_text"), post.get("readable_review_day"), post.get("review_id"), post.get("readable_review_month"), post.get("readable_review_year") ))
                                    psql_connection.commit()
                                        except Exception as e:    
                                                                                             
                                                            psql_connection.rollback()








##Zodata=# ALTER TABLE reviews ALTER COLUMN review_id TYPE varchar(20);








