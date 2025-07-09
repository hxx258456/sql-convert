# SQL Converter

一个基于FastAPI和sqlglot的SQL转换服务，可以将MySQL SQL语句转换为Oracle SQL语句。

## 功能特性

- 🚀 基于FastAPI的高性能Web服务
- 🔄 使用sqlglot进行MySQL到Oracle的SQL转换
- 📝 支持格式化输出
- 🔄 支持批量转换
- 📊 自动API文档（Swagger UI）
- 🧪 包含完整的测试用例

## 安装和运行

### 1. 安装依赖

```bash
# 使用uv安装依赖
uv sync
```

### 2. 启动服务

```bash
# 方式1：直接运行
python main.py

# 方式2：使用uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

服务将在 `http://localhost:8000` 启动

### 3. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API使用

### 单个SQL转换

**POST** `/convert`

请求体：
```json
{
  "mysql_sql": "SELECT * FROM users WHERE age > 18",
  "pretty": true
}
```

响应：
```json
{
  "mysql_sql": "SELECT * FROM users WHERE age > 18",
  "oracle_sql": "SELECT * FROM users WHERE age > 18",
  "success": true,
  "error_message": null
}
```

### 批量SQL转换

**POST** `/convert/batch`

请求体：
```json
[
  {
    "mysql_sql": "SELECT * FROM products WHERE price > 100",
    "pretty": true
  },
  {
    "mysql_sql": "INSERT INTO users (name, email) VALUES ('John', 'john@example.com')",
    "pretty": true
  }
]
```

### 健康检查

**GET** `/health`

响应：
```json
{
  "status": "healthy",
  "service": "sql-converter"
}
```

## 测试

运行测试脚本：

```bash
python test_converter.py
```

## 示例

### 简单查询转换

```python
import requests

data = {
    "mysql_sql": "SELECT * FROM users WHERE age > 18",
    "pretty": True
}

response = requests.post("http://localhost:8000/convert", json=data)
result = response.json()
print(result["oracle_sql"])
```

### 复杂查询转换

```python
mysql_sql = """
SELECT 
    u.id,
    u.name,
    u.email,
    COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at >= '2023-01-01'
GROUP BY u.id, u.name, u.email
HAVING order_count > 0
ORDER BY order_count DESC
LIMIT 10
"""

data = {"mysql_sql": mysql_sql, "pretty": True}
response = requests.post("http://localhost:8000/convert", json=data)
result = response.json()
print(result["oracle_sql"])
```

## 支持的SQL特性

- SELECT 查询（包括JOIN、WHERE、GROUP BY、HAVING、ORDER BY、LIMIT）
- INSERT 语句
- UPDATE 语句
- DELETE 语句
- 子查询
- 聚合函数
- 字符串函数
- 日期函数
- 数学函数

## 注意事项

1. 某些MySQL特有的函数可能在Oracle中没有直接对应，转换结果可能需要手动调整
2. 数据类型转换可能需要根据具体业务场景进行调整
3. 建议在生产环境中添加适当的错误处理和日志记录

## 技术栈

- **FastAPI**: Web框架
- **sqlglot**: SQL解析和转换库
- **Pydantic**: 数据验证
- **Uvicorn**: ASGI服务器
