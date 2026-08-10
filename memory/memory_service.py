import sqlite3


class MemoryService:

    def __init__(self, db_path="memory/lacerta.db"):
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (session_id)
                    REFERENCES sessions(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        summary TEXT NOT NULL,
        prompt TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

        connection.commit()
        connection.close()

    def create_session(self) -> int:

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO sessions DEFAULT VALUES
        """)

        session_id = cursor.lastrowid

        connection.commit()
        connection.close()

        return session_id

    def save_message(
        self,
        session_id: int,
        role: str,
        content: str
    ):

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO messages (
                session_id,
                role,
                content
            )
            VALUES (?, ?, ?)
        """, (
            session_id,
            role,
            content
        ))
        cursor.execute("""
        UPDATE sessions
        SET updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (session_id,))

        connection.commit()
        connection.close()

    def get_messages(self, session_id: int) -> list[dict]:

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
        SELECT role, content, created_at
        FROM messages
        WHERE session_id = ?
        ORDER BY id ASC
    """, (session_id,))

        rows = cursor.fetchall()

        connection.close()

        return [
        {
            "role": role,
            "content": content,
            "created_at": created_at
        }
        for role, content, created_at in rows
    ]


    def get_last_session(self) -> int | None:

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
        SELECT id
        FROM sessions
        ORDER BY id DESC
        LIMIT 1
    """)

        row = cursor.fetchone()

        connection.close()

        return row[0] if row else None

    def save_memory(
    self,
    memory_type: str,
    key: str,
    value: str
        ):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
        SELECT id
        FROM memories
        WHERE type = ? AND key = ?
        LIMIT 1
    """, (
        memory_type,
        key
    ))

        row = cursor.fetchone()

        if row:

            cursor.execute("""
            UPDATE memories
            SET value = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            value,
            row[0]
        ))

        else:

            cursor.execute("""
            INSERT INTO memories (
                type,
                key,
                value
            )
            VALUES (?, ?, ?)
        """, (
            memory_type,
            key,
            value
        ))

        connection.commit()
        connection.close()


    def get_memory(
    self,
    memory_type: str,
    key: str
) -> dict | None:

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
        SELECT id, type, key, value, created_at, updated_at
        FROM memories
        WHERE type = ? AND key = ?
        LIMIT 1
    """, (
        memory_type,
        key
    ))

        row = cursor.fetchone()

        connection.close()

        if not row:
            return None

        return {
        "id": row[0],
        "type": row[1],
        "key": row[2],
        "value": row[3],
        "created_at": row[4],
        "updated_at": row[5]
    }

    def get_memories(
    self,
    memory_type: str | None = None
) -> list[dict]:

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        if memory_type:

            cursor.execute("""
            SELECT id, type, key, value, created_at, updated_at
            FROM memories
            WHERE type = ?
            ORDER BY id ASC
        """, (
            memory_type,
        ))

        else:

            cursor.execute("""
            SELECT id, type, key, value, created_at, updated_at
            FROM memories
            ORDER BY id ASC
        """)

        rows = cursor.fetchall()

        connection.close()

        return [
        {
            "id": row[0],
            "type": row[1],
            "key": row[2],
            "value": row[3],
            "created_at": row[4],
            "updated_at": row[5]
        }
        for row in rows
    ]

    def delete_memory(
    self,
    memory_type: str,
    key: str
) -> bool:

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
        DELETE FROM memories
        WHERE type = ? AND key = ?
    """, (
        memory_type,
        key
    ))

        deleted = cursor.rowcount > 0

        connection.commit()
        connection.close()

        return deleted

    # ----------------FAVORITOS----------------

    def save_favorite(
    self,
    category: str,
    summary: str,
    prompt: str
):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
        INSERT INTO favorites (
            category,
            summary,
            prompt
        )
        VALUES (?, ?, ?)
    """, (
        category,
        summary,
        prompt
    ))

        favorite_id = cursor.lastrowid

        connection.commit()
        connection.close()

        return favorite_id


    def get_favorite(
    self,
    favorite_id: int
) -> dict | None:

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
        SELECT
            id,
            category,
            summary,
            prompt,
            created_at,
            updated_at
        FROM favorites
        WHERE id = ?
        LIMIT 1
    """, (
        favorite_id,
    ))

        row = cursor.fetchone()

        connection.close()

        if not row:
            return None

        return {
        "id": row[0],
        "category": row[1],
        "summary": row[2],
        "prompt": row[3],
        "created_at": row[4],
        "updated_at": row[5]
    }


    def get_favorites(
    self,
    category: str | None = None
) -> list[dict]:

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        if category:

            cursor.execute("""
            SELECT
                id,
                category,
                summary,
                prompt,
                created_at,
                updated_at
            FROM favorites
            WHERE category = ?
            ORDER BY id ASC
        """, (
            category,
        ))

        else:

            cursor.execute("""
            SELECT
                id,
                category,
                summary,
                prompt,
                created_at,
                updated_at
            FROM favorites
            ORDER BY id ASC
        """)

        rows = cursor.fetchall()

        connection.close()

        return [
        {
            "id": row[0],
            "category": row[1],
            "summary": row[2],
            "prompt": row[3],
            "created_at": row[4],
            "updated_at": row[5]
        }
        for row in rows
    ]


    def delete_favorite(
    self,
    favorite_id: int
) -> bool:

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
        DELETE FROM favorites
        WHERE id = ?
    """, (
        favorite_id,
    ))

        deleted = cursor.rowcount > 0

        connection.commit()
        connection.close()

        return deleted


    def __repr__(self):
        return "<MemoryService>"