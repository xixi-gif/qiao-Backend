import pandas as pd
import re
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.api.models.knowledge import Base, KGNode

# ====================== 只改这里 ======================
DATABASE_URL = "mysql+pymysql://root:linjiaxin040219@127.0.0.1:3306/qiaoxiang_platform?charset=utf8mb4"
CSV_FILE_PATH = "export.csv"
# ======================================================

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def parse_node(node_str):
    type_match = re.search(r':(\w+)', node_str)
    node_type = type_match.group(1) if type_match else "Unknown"

    name = f"{node_type}_{uuid.uuid4().hex[:6]}"
    intro_match = re.search(r'简介:\s*"([^"]+)"', node_str)
    if intro_match:
        raw = intro_match.group(1).strip()
        name = raw[:12] + "..." if len(raw) > 12 else raw

    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "type": node_type,
        "original_data": node_str
    }

def run_import():
    db = SessionLocal()
    df = pd.read_csv(CSV_FILE_PATH)
    nodes = []

    for _, row in df.iterrows():
        node = parse_node(str(row["n"]))
        nodes.append(node)
        db.add(KGNode(**node))

    db.commit()
    db.close()
    print(f"✅ 导入成功！共导入 {len(nodes)} 个节点")

if __name__ == "__main__":
    run_import()