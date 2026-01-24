import pymysql
from urllib.parse import urlparse  # 用官方库解析URL，避免手动拆分出错
from app.api.core.config import settings

def execute_sql_file():
    # 用 urllib.parse 解析 URL（更健壮，避免手动拆分的bug）
    parsed_url = urlparse(settings.DATABASE_URL)
    
    # 正确提取连接参数
    host = parsed_url.hostname
    user = parsed_url.username
    password = parsed_url.password or ''  # 空密码时设为''
    db = parsed_url.path.lstrip('/')  # 去掉路径开头的/，只保留数据库名
    charset = 'utf8mb4'

    # 建立数据库连接
    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        db=db,
        charset=charset
    )

    try:
        with conn.cursor() as cursor:
            with open('table/table.sql', 'r', encoding='utf-8') as f:
                sql = f.read()
                # 按;拆分SQL，过滤空行
                for statement in sql.split(';'):
                    stmt = statement.strip()
                    if stmt and not stmt.startswith('--'):  # 跳过注释和空语句
                        cursor.execute(stmt)
        conn.commit()
        print("SQL脚本执行成功")
    except Exception as e:
        print(f"执行失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    execute_sql_file()