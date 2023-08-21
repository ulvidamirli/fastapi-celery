import io

import pandas as pd
import requests
from sqlalchemy import create_engine

from .celeryconfig import app

"""
This is the Celery task file. We have defined a sample_task() function that will be called by the Celery worker.
This function will download the spreadsheet from Google Sheets and save it as a CSV file.
Then it will call the synchronize_data() function to compare the data with database and update the database if needed.

Since spreadsheet and database can be quite large, we are using chunking to process the data in batches.

Errors:
- Spreadsheet and database comparison not always work as expected. This will result in data being added with the same id, hence fail the query. (I need to check data cleaning in the spreadsheet)
- If the spreadsheet is empty or file is not found, the task will fail.
- If the spreadsheet is not in the correct format, the task will fail.
- If the database is not available, the task will fail.
- If the database is not in the correct format, the task will fail.

TODO list:
- Add error handling
- Add logging
- Add unit tests
- Save constants in env variable
- Handle the case when the spreadsheet is empty or file is not found
- Handle when spreadsheet is not in the correct format
- Handle when database is not available
- Use ORM instead of raw SQL
"""

# Define constants
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/17rhadYqfh8RhCZN0j32R9S4pVk6NdWorhelQwneehZ8/export?format=csv"
DB_ENGINE = create_engine("postgresql://postgres:postgres@postgres/main_db")
CHUNK_SIZE = 20


@app.task
def sample_task():
    response = requests.get(SPREADSHEET_URL, stream=True)

    if response.status_code == 200:
        df = pd.read_csv(io.StringIO(response.text))
        # Add the 'id' column
        df.insert(0, 'id', range(1, len(df) + 1))

        synchronize_data()
        return {"status": "success", "message": "Spreadsheet downloaded and parsed successfully"}
    else:
        return {"status": "error", "message": "Something went wrong while downloading the spreadsheet"}


def get_spreadsheet_chunks():
    for chunk in pd.read_csv('./app/assets/spreadsheet.csv', chunksize=CHUNK_SIZE):
        yield chunk


def get_db_data_chunks():
    query = "SELECT id, title, description, image FROM entity OFFSET %(offset)s LIMIT %(limit)s"
    offset = 0
    while True:
        db_data = pd.read_sql(query, DB_ENGINE, index_col='id', params={
                              'offset': offset, 'limit': CHUNK_SIZE})
        if db_data.empty:
            break
        offset += CHUNK_SIZE
        yield db_data


def compare_data(db_chunk, spreadsheet_chunk):
    spreadsheet_df = spreadsheet_chunk.set_index('id')
    db_df = db_chunk

    print('spreadsheet_df', spreadsheet_df)
    print('db_df', db_df)

    common_ids = db_df.index.intersection(spreadsheet_df.index)

    spreadsheet_changes = spreadsheet_df.loc[common_ids][~(
        db_df.loc[common_ids] == spreadsheet_df.loc[common_ids]).all(axis=1)]
    updated_data = spreadsheet_changes.reset_index().to_dict(orient='records')

    new_data = spreadsheet_df[~spreadsheet_df.index.isin(
        db_df.index)].reset_index().to_dict(orient='records')

    deleted_data = db_df[~db_df.index.isin(
        spreadsheet_df.index)].reset_index().to_dict(orient='records')
    
    print('updated_data', updated_data)
    print('new_data', new_data)
    print('deleted_data', deleted_data)

    return updated_data, new_data, deleted_data


def synchronize_data():
    spreadsheet_generator = get_spreadsheet_chunks()
    db_generator = get_db_data_chunks()

    for spreadsheet_chunk in spreadsheet_generator:
        try:
            db_chunk = next(db_generator)
        except StopIteration:
            updated_data, new_data, deleted_data = [
            ], spreadsheet_chunk.reset_index().to_dict(orient='records'), []
        else:
            updated_data, new_data, deleted_data = compare_data(
                db_chunk, spreadsheet_chunk)

        if updated_data:
            update_query = "UPDATE entity SET title = %(title)s, description = %(description)s, image = %(image)s WHERE id = %(id)s"
            DB_ENGINE.execute(update_query, updated_data)

        if new_data:
            insert_query = "INSERT INTO entity (id, title, description, image) VALUES (%(id)s, %(title)s, %(description)s, %(image)s)"
            DB_ENGINE.execute(insert_query, new_data)

        if deleted_data:
            delete_query = "DELETE FROM entity WHERE id = %(id)s"
            DB_ENGINE.execute(delete_query, deleted_data)

    DB_ENGINE.dispose()

    print("Data synchronization completed")