
import asyncio
import re
from pathlib import Path
from sqlalchemy import text
from app.config import alchemy
from app.lib.settings import get_settings

# 配置
SQL_FILE = Path(r'C:\Users\ASUS\Desktop\project1\xtck_deploy\xtck_deploy\db_xtck_20260203.sql')
VIEWS_FILE = Path(r'C:\Users\ASUS\Desktop\project1\litestar-fullstack\tools\db\recreate_views.sql')

# 需要迁移的表前缀
TARGET_PREFIX = "public.dataapp_"

async def migrate():
    settings = get_settings()
    print(f"Connecting to database: {settings.db.URL}")
    
    async with alchemy.get_session() as session:
        # 1. 执行视图创建 (如果有依赖表未创建，可能会失败)
        # 注意：建议先做 litestar db upgrade
        
        # 2. 从 SQL 文件中提取并执行 INSERT 语句
        print("Parsing SQL for INSERT statements...")
        with open(SQL_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            count = 0
            batch = []
            for line in f:
                if line.startswith('INSERT INTO ' + TARGET_PREFIX):
                    # 修正表名，去掉 public. 前缀以匹配 SQLAlchemy 默认 schema
                    cleaned_line = line.replace('INSERT INTO public.', 'INSERT INTO ')
                    batch.append(cleaned_line)
                    
                    if len(batch) >= 100:
                        await session.execute(text("".join(batch)))
                        await session.commit()
                        count += len(batch)
                        print(f"Inserted {count} rows...")
                        batch = []
            
            if batch:
                await session.execute(text("".join(batch)))
                await session.commit()
                count += len(batch)
                print(f"Finished inserting {count} rows.")

        # 3. 创建视图
        print("Creating views...")
        if VIEWS_FILE.exists():
            with open(VIEWS_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                # 分割 SQL 语句
                statements = content.split(';')
                for stmt in statements:
                    stmt = stmt.strip()
                    if stmt:
                        # 修正视图中的 public. 前缀
                        stmt = stmt.replace('public.', '')
                        try:
                            await session.execute(text(stmt))
                            await session.commit()
                        except Exception as e:
                            print(f"Error creating view: {e[:100]}...")
                            await session.rollback()
            print("Views recreated successfully.")

if __name__ == "__main__":
    asyncio.run(migrate())
