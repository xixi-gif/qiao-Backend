import pymysql
from app.api.core.config import settings


def execute_sql_file():
    conn = pymysql.connect(
        host=settings.DATABASE_URL.split('@')[1].split(':')[0],
        user=settings.DATABASE_URL.split('://')[1].split(':')[0],
        password=settings.DATABASE_URL.split(':')[2].split('@')[0],
        db=settings.DATABASE_URL.split('/')[-1],
        charset='utf8mb4'
    )

    try:
        with conn.cursor() as cursor:
            with open('table/table.sql', 'r', encoding='utf-8') as f:
                sql = f.read()
                for statement in sql.split(';'):
                    if statement.strip():
                        cursor.execute(statement)
        conn.commit()
        print("SQL脚本执行成功")
    except Exception as e:
        print(f"执行失败: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    execute_sql_file()