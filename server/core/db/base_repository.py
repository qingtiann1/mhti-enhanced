"""数据库操作 Mixin 基类。

提供简化的数据库操作方法，减少服务类中的重复代码。
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

import aiosqlite

from server.core.db.connection import db_context

if TYPE_CHECKING:
    pass


class DatabaseMixin:
    """数据库操作 Mixin，提供简化的 CRUD 方法。

    Usage:
        class MyService(DatabaseMixin):
            async def get_user(self, user_id: int):
                return await self._fetch_one(
                    "SELECT * FROM users WHERE id = ?",
                    (user_id,)
                )
    """

    async def _fetch_one(
        self,
        query: str,
        params: tuple[Any, ...] = (),
    ) -> aiosqlite.Row | None:
        """执行查询并返回单行结果。

        Args:
            query: SQL 查询语句。
            params: 查询参数。

        Returns:
            单行结果或 None。
        """
        async with db_context() as db:
            cursor = await db.execute(query, params)
            return await cursor.fetchone()

    async def _fetch_all(
        self,
        query: str,
        params: tuple[Any, ...] = (),
    ) -> list[aiosqlite.Row]:
        """执行查询并返回所有行。

        Args:
            query: SQL 查询语句。
            params: 查询参数。

        Returns:
            结果行列表。
        """
        async with db_context() as db:
            cursor = await db.execute(query, params)
            return await cursor.fetchall()

    async def _fetch_value(
        self,
        query: str,
        params: tuple[Any, ...] = (),
        default: Any = None,
    ) -> Any:
        """执行查询并返回第一列的值。

        Args:
            query: SQL 查询语句。
            params: 查询参数。
            default: 未找到时的默认值。

        Returns:
            第一列的值或默认值。
        """
        row = await self._fetch_one(query, params)
        return row[0] if row else default

    async def _execute(
        self,
        query: str,
        params: tuple[Any, ...] = (),
        commit: bool = True,
    ) -> int:
        """执行 SQL 语句并返回影响行数。

        Args:
            query: SQL 语句。
            params: 查询参数。
            commit: 是否自动提交。

        Returns:
            影响的行数。
        """
        async with db_context() as db:
            cursor = await db.execute(query, params)
            if commit:
                await db.commit()
            return cursor.rowcount

    async def _execute_many(
        self,
        query: str,
        params_list: list[tuple[Any, ...]],
        commit: bool = True,
    ) -> int:
        """批量执行 SQL 语句。

        Args:
            query: SQL 语句。
            params_list: 参数列表。
            commit: 是否自动提交。

        Returns:
            影响的总行数。
        """
        async with db_context() as db:
            await db.executemany(query, params_list)
            if commit:
                await db.commit()
            return len(params_list)

    async def _insert(
        self,
        query: str,
        params: tuple[Any, ...] = (),
    ) -> int:
        """执行插入并返回最后插入的 ID。

        Args:
            query: INSERT 语句。
            params: 查询参数。

        Returns:
            最后插入的行 ID。
        """
        async with db_context() as db:
            cursor = await db.execute(query, params)
            await db.commit()
            return cursor.lastrowid or 0

    async def _exists(
        self,
        query: str,
        params: tuple[Any, ...] = (),
    ) -> bool:
        """检查记录是否存在。

        Args:
            query: SQL 查询语句（应返回至少一行表示存在）。
            params: 查询参数。

        Returns:
            记录是否存在。
        """
        row = await self._fetch_one(query, params)
        return row is not None

    async def _count(
        self,
        table: str,
        where: str = "",
        params: tuple[Any, ...] = (),
    ) -> int:
        """获取表中记录数。

        Args:
            table: 表名。
            where: WHERE 子句（不包含 WHERE 关键字）。
            params: 查询参数。

        Returns:
            记录数。
        """
        query = f"SELECT COUNT(*) FROM {table}"
        if where:
            query += f" WHERE {where}"
        return await self._fetch_value(query, params, 0)
