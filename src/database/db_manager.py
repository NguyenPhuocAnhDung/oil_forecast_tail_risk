"""
src/database/db_manager.py
==========================
Lớp quản lý cơ sở dữ liệu SQLite tự trị của hệ thống dự báo.
Lưu trữ thông tin lịch sử thực tế, tham số sốc địa chính trị và kết quả dự báo phân vị.
"""

import os
import sqlite3
import pandas as pd
from typing import List, Dict, Optional, Union

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "processed", "forecast_storage.db"
)

class DBManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self):
        """Trả về connection SQLite với cài đặt timeout để thread-safe."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Khởi tạo các bảng cơ sở dữ liệu nếu chưa tồn tại."""
        with self.get_connection() as conn:
            # 1. Bảng giá thực tế lịch sử (trong nước và thế giới)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS actual_prices (
                    date TEXT PRIMARY KEY,
                    brent REAL,
                    wti REAL,
                    usd_index REAL,
                    mg95 REAL,
                    mg92 REAL,
                    do_001 REAL,
                    do_05 REAL
                )
            """)
            
            # 2. Bảng lưu trữ cú sốc từ tin tức vĩ mô trích xuất bởi LLM
            conn.execute("""
                CREATE TABLE IF NOT EXISTS llm_shocks (
                    date TEXT PRIMARY KEY,
                    gpr_shock INTEGER,
                    brent_shock_pct REAL,
                    wti_shock_pct REAL,
                    usd_index_shock_pct REAL,
                    decay_days INTEGER,
                    rationale TEXT
                )
            """)
            
            # 3. Bảng lưu trữ dự báo phân vị của GUMNet và các mô hình
            conn.execute("""
                CREATE TABLE IF NOT EXISTS forecasts (
                    prediction_date TEXT,
                    forecast_date TEXT,
                    product TEXT,
                    model TEXT,
                    seed INTEGER,
                    horizon INTEGER,
                    q10 REAL,
                    q50 REAL,
                    q90 REAL,
                    PRIMARY KEY (prediction_date, forecast_date, product, model, seed, horizon)
                )
            """)
            conn.commit()

    def save_actual_prices(self, date_str: str, brent: Optional[float], wti: Optional[float], 
                           usd_index: Optional[float], mg95: Optional[float] = None, 
                           mg92: Optional[float] = None, do_001: Optional[float] = None, 
                           do_05: Optional[float] = None):
        """Lưu hoặc cập nhật giá đóng cửa thực tế hằng ngày."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO actual_prices (date, brent, wti, usd_index, mg95, mg92, do_001, do_05)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    brent=coalesce(excluded.brent, brent),
                    wti=coalesce(excluded.wti, wti),
                    usd_index=coalesce(excluded.usd_index, usd_index),
                    mg95=coalesce(excluded.mg95, mg95),
                    mg92=coalesce(excluded.mg92, mg92),
                    do_001=coalesce(excluded.do_001, do_001),
                    do_05=coalesce(excluded.do_05, do_05)
            """, (date_str, brent, wti, usd_index, mg95, mg92, do_001, do_05))
            conn.commit()

    def save_llm_shock(self, date_str: str, gpr_shock: int, brent_shock_pct: float, 
                       wti_shock_pct: float, usd_index_shock_pct: float, 
                       decay_days: int, rationale: str):
        """Lưu trữ kết quả lượng hóa cú sốc của LLM."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO llm_shocks (date, gpr_shock, brent_shock_pct, wti_shock_pct, usd_index_shock_pct, decay_days, rationale)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    gpr_shock=excluded.gpr_shock,
                    brent_shock_pct=excluded.brent_shock_pct,
                    wti_shock_pct=excluded.wti_shock_pct,
                    usd_index_shock_pct=excluded.usd_index_shock_pct,
                    decay_days=excluded.decay_days,
                    rationale=excluded.rationale
            """, (date_str, gpr_shock, brent_shock_pct, wti_shock_pct, usd_index_shock_pct, decay_days, rationale))
            conn.commit()

    def save_forecasts(self, prediction_date_str: str, forecast_dates: List[str], 
                       product: str, model: str, seed: int, horizon: int, 
                       q10_list: List[float], q50_list: List[float], q90_list: List[float]):
        """Lưu trữ chuỗi dự báo phân vị 60 ngày."""
        with self.get_connection() as conn:
            for idx, f_date in enumerate(forecast_dates):
                conn.execute("""
                    INSERT INTO forecasts (prediction_date, forecast_date, product, model, seed, horizon, q10, q50, q90)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(prediction_date, forecast_date, product, model, seed, horizon) DO UPDATE SET
                        q10=excluded.q10,
                        q50=excluded.q50,
                        q90=excluded.q90
                """, (prediction_date_str, f_date, product, model, seed, horizon, 
                      q10_list[idx], q50_list[idx], q90_list[idx]))
            conn.commit()

    def get_actual_prices_df(self) -> pd.DataFrame:
        """Trả về DataFrame giá thực tế lịch sử để vẽ biểu đồ."""
        with self.get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM actual_prices ORDER BY date ASC", conn)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df

    def get_llm_shocks_df(self) -> pd.DataFrame:
        """Trả về DataFrame các cú sốc địa chính trị."""
        with self.get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM llm_shocks ORDER BY date DESC", conn)
        return df

    def get_forecast_df(self, prediction_date: str, product: str, model: str, 
                        horizon: int, seed_filter: Union[int, str] = "Average") -> pd.DataFrame:
        """
        Truy vấn kết quả dự báo từ SQLite.
        Nếu seed_filter == 'Average', tính trung bình phân vị của tất cả các seeds có sẵn.
        """
        with self.get_connection() as conn:
            if seed_filter == "Average":
                query = """
                    SELECT forecast_date, AVG(q10) as q10, AVG(q50) as q50, AVG(q90) as q90 
                    FROM forecasts 
                    WHERE prediction_date = ? AND product = ? AND model = ? AND horizon = ?
                    GROUP BY forecast_date
                    ORDER BY forecast_date ASC
                """
                df = pd.read_sql_query(query, conn, params=(prediction_date, product, model, horizon))
            else:
                query = """
                    SELECT forecast_date, q10, q50, q90 
                    FROM forecasts 
                    WHERE prediction_date = ? AND product = ? AND model = ? AND horizon = ? AND seed = ?
                    ORDER BY forecast_date ASC
                """
                df = pd.read_sql_query(query, conn, params=(prediction_date, product, model, horizon, int(seed_filter)))
        
        if not df.empty:
            df['forecast_date'] = pd.to_datetime(df['forecast_date'])
        return df

    def get_available_prediction_dates(self, product: str, model: str, horizon: int) -> List[str]:
        """Lấy danh sách các ngày trong lịch sử đã được chạy dự báo."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT prediction_date 
                FROM forecasts 
                WHERE product = ? AND model = ? AND horizon = ?
                ORDER BY prediction_date DESC
            """, (product, model, horizon))
            rows = cursor.fetchall()
        return [r[0] for r in rows]
