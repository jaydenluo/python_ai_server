"""
查询构建器使用示例
展示链式查询的强大功能
"""

from app.core.query_builder import QueryBuilder
from app.models.entities.user import User
from app.models.entities.post import Post
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime, date, timedelta


def demo_query_builder():
    """演示查询构建器功能"""
    print("🚀 查询构建器演示")
    print("=" * 50)
    
    # 创建数据库连接
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 创建测试数据
    create_test_data(session)
    
    # 创建查询构建器
    user_builder = QueryBuilder(User, session)
    post_builder = QueryBuilder(Post, session)
    
    # 1. 基础查询
    print("\n1. 基础查询")
    users = user_builder.where("status", "eq", "active").all()
    print(f"活跃用户: {len(users)}")
    
    # 2. 链式查询
    print("\n2. 链式查询")
    recent_users = (user_builder
                   .where("status", "eq", "active")
                   .where("created_at", "gte", date.today() - timedelta(days=30))
                   .order_by("created_at", "desc")
                   .limit(5)
                   .all())
    print(f"最近30天活跃用户: {len(recent_users)}")
    
    # 3. 复杂条件查询
    print("\n3. 复杂条件查询")
    complex_users = (user_builder
                   .where("status", "eq", "active")
                   .where("email", "like", "@example.com")
                   .where("login_count", "gt", 0)
                   .order_by("login_count", "desc")
                   .all())
    print(f"复杂条件用户: {len(complex_users)}")
    
    # 4. 日期范围查询
    print("\n4. 日期范围查询")
    this_week_users = user_builder.where_this_week("created_at").all()
    print(f"本周创建用户: {len(this_week_users)}")
    
    this_month_users = user_builder.where_this_month("created_at").all()
    print(f"本月创建用户: {len(this_month_users)}")
    
    # 5. 模糊搜索
    print("\n5. 模糊搜索")
    search_users = (user_builder
                   .where_like("username", "user")
                   .or_where("first_name", "like", "John")
                   .all())
    print(f"搜索用户: {len(search_users)}")
    
    # 6. 数组查询
    print("\n6. 数组查询")
    admin_users = user_builder.where_array_contains("permissions", "admin").all()
    print(f"管理员用户: {len(admin_users)}")
    
    # 7. JSON字段查询
    print("\n7. JSON字段查询")
    json_users = user_builder.where_json("profile_data", "age", 25).all()
    print(f"年龄25的用户: {len(json_users)}")
    
    # 8. 日期部分查询
    print("\n8. 日期部分查询")
    today_users = user_builder.where_date_part("created_at", "day", date.today().day).all()
    print(f"今天创建用户: {len(today_users)}")
    
    # 9. 排序和分页
    print("\n9. 排序和分页")
    page_result = (user_builder
                  .where("status", "eq", "active")
                  .order_by("created_at", "desc")
                  .paginate_result(page=1, per_page=3))
    print(f"分页结果: 第{page_result['page']}页，共{page_result['pages']}页")
    print(f"当前页用户数: {len(page_result['items'])}")
    
    # 10. 聚合查询
    print("\n10. 聚合查询")
    total_users = user_builder.where("status", "eq", "active").count()
    print(f"活跃用户总数: {total_users}")
    
    # 11. 关联查询
    print("\n11. 关联查询")
    users_with_posts = (user_builder
                       .where("status", "eq", "active")
                       .with_relations(["posts"])
                       .all())
    for user in users_with_posts:
        print(f"用户: {user.username}, 文章数: {len(user.posts) if hasattr(user, 'posts') else 0}")
    
    # 12. 子查询关联
    print("\n12. 子查询关联")
    users_with_subquery = (user_builder
                          .where("status", "eq", "active")
                          .with_subquery_relations(["posts", "comments"])
                          .all())
    for user in users_with_subquery:
        print(f"用户: {user.username}")
        if hasattr(user, 'posts'):
            print(f"  文章: {[post.title for post in user.posts]}")
        if hasattr(user, 'comments'):
            print(f"  评论: {[comment.content for comment in user.comments]}")
    
    # 13. 选择特定字段
    print("\n13. 选择特定字段")
    user_fields = (user_builder
                  .select("username", "email", "status")
                  .where("status", "eq", "active")
                  .all())
    print(f"选择字段查询: {len(user_fields)}")
    
    # 14. 去重查询
    print("\n14. 去重查询")
    distinct_users = (user_builder
                     .distinct()
                     .select("status")
                     .all())
    print(f"去重状态: {len(distinct_users)}")
    
    # 15. 分组查询
    print("\n15. 分组查询")
    status_groups = (user_builder
                    .group_by("status")
                    .aggregate("id", "count")
                    .all())
    print(f"状态分组: {status_groups}")
    
    # 16. 原生SQL查询
    print("\n16. 原生SQL查询")
    sql_result = user_builder.raw_sql(
        "SELECT username, email FROM users WHERE status = :status",
        {"status": "active"}
    ).all()
    print(f"原生SQL查询: {len(sql_result)}")
    
    # 17. 查询克隆
    print("\n17. 查询克隆")
    base_query = user_builder.where("status", "eq", "active")
    active_users = base_query.clone().all()
    recent_active_users = base_query.clone().where("created_at", "gte", date.today() - timedelta(days=7)).all()
    print(f"活跃用户: {len(active_users)}")
    print(f"最近7天活跃用户: {len(recent_active_users)}")
    
    # 18. 查询信息
    print("\n18. 查询信息")
    query_info = user_builder.where("status", "eq", "active").order_by("created_at", "desc").to_dict()
    print(f"查询信息: {query_info}")


def demo_advanced_queries():
    """演示高级查询"""
    print("\n🔧 高级查询演示")
    print("=" * 50)
    
    # 创建数据库连接
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 创建测试数据
    create_test_data(session)
    
    # 创建查询构建器
    user_builder = QueryBuilder(User, session)
    post_builder = QueryBuilder(Post, session)
    
    # 1. 多表关联查询
    print("\n1. 多表关联查询")
    users_with_posts = (user_builder
                       .join("posts")
                       .where("posts.status", "eq", "published")
                       .with_relations(["posts"])
                       .all())
    print(f"有已发布文章的用户: {len(users_with_posts)}")
    
    # 2. 复杂排序
    print("\n2. 复杂排序")
    sorted_users = (user_builder
                   .where("status", "eq", "active")
                   .order_by_multiple([("login_count", "desc"), ("created_at", "asc")])
                   .all())
    print(f"复杂排序用户: {len(sorted_users)}")
    
    # 3. 条件组合
    print("\n3. 条件组合")
    complex_users = (user_builder
                   .where("status", "eq", "active")
                   .where("email", "like", "@example.com")
                   .where("login_count", "gt", 0)
                   .where("created_at", "gte", date.today() - timedelta(days=30))
                   .order_by("login_count", "desc")
                   .limit(10)
                   .all())
    print(f"复杂条件用户: {len(complex_users)}")
    
    # 4. 聚合统计
    print("\n4. 聚合统计")
    stats = user_builder.where("status", "eq", "active").aggregate("login_count", "sum").first()
    print(f"活跃用户总登录次数: {stats}")
    
    # 5. 分页查询
    print("\n5. 分页查询")
    page_result = (user_builder
                  .where("status", "eq", "active")
                  .order_by("created_at", "desc")
                  .paginate_result(page=1, per_page=5))
    print(f"分页查询: 第{page_result['page']}页，共{page_result['pages']}页")
    print(f"总用户数: {page_result['total']}")
    print(f"当前页用户数: {len(page_result['items'])}")
    
    # 6. 存在性检查
    print("\n6. 存在性检查")
    has_active_users = user_builder.where("status", "eq", "active").exists()
    print(f"是否存在活跃用户: {has_active_users}")
    
    # 7. 批量查询
    print("\n7. 批量查询")
    user_ids = [1, 2, 3]
    batch_users = user_builder.where_in("id", user_ids).all()
    print(f"批量查询用户: {len(batch_users)}")
    
    # 8. 范围查询
    print("\n8. 范围查询")
    range_users = (user_builder
                  .where_between("login_count", 1, 100)
                  .all())
    print(f"登录次数1-100的用户: {len(range_users)}")
    
    # 9. 空值查询
    print("\n9. 空值查询")
    null_users = user_builder.where_null("last_login_at").all()
    print(f"从未登录的用户: {len(null_users)}")
    
    not_null_users = user_builder.where_not_null("last_login_at").all()
    print(f"已登录的用户: {len(not_null_users)}")


def create_test_data(session):
    """创建测试数据"""
    # 创建用户
    users = [
        User(username="user1", email="user1@example.com", password="password", 
             first_name="User", last_name="One", status="active", login_count=10,
             permissions=["user", "admin"], profile_data={"age": 25}),
        User(username="user2", email="user2@example.com", password="password", 
             first_name="User", last_name="Two", status="active", login_count=5,
             permissions=["user"], profile_data={"age": 30}),
        User(username="user3", email="user3@example.com", password="password", 
             first_name="User", last_name="Three", status="inactive", login_count=0,
             permissions=["user"], profile_data={"age": 20}),
        User(username="john_doe", email="john@example.com", password="password", 
             first_name="John", last_name="Doe", status="active", login_count=15,
             permissions=["user", "admin"], profile_data={"age": 25}),
        User(username="jane_smith", email="jane@example.com", password="password", 
             first_name="Jane", last_name="Smith", status="pending", login_count=0,
             permissions=["user"], profile_data={"age": 28}),
    ]
    
    for user in users:
        session.add(user)
    
    session.commit()
    
    # 创建文章
    posts = [
        Post(title="Post 1", content="Content 1", user_id=1, status="published"),
        Post(title="Post 2", content="Content 2", user_id=1, status="draft"),
        Post(title="Post 3", content="Content 3", user_id=2, status="published"),
        Post(title="Post 4", content="Content 4", user_id=4, status="published"),
    ]
    
    for post in posts:
        session.add(post)
    
    session.commit()
    
    # 创建评论
    comments = [
        Comment(content="Comment 1", user_id=1, post_id=1),
        Comment(content="Comment 2", user_id=2, post_id=1),
        Comment(content="Comment 3", user_id=1, post_id=2),
        Comment(content="Comment 4", user_id=4, post_id=3),
    ]
    
    for comment in comments:
        session.add(comment)
    
    session.commit()


if __name__ == "__main__":
    print("🎯 查询构建器完整演示")
    print("=" * 60)
    
    # 运行演示
    demo_query_builder()
    demo_advanced_queries()
    
    print("\n🎉 演示完成！")
    print("\n💡 查询构建器优势:")
    print("1. 链式查询 - 代码简洁易读")
    print("2. 类型安全 - 编译时检查字段名")
    print("3. 功能强大 - 支持复杂查询")
    print("4. 易于扩展 - 可以轻松添加新功能")
    print("5. 性能优化 - 自动优化查询")
    print("6. 查询复用 - 支持查询克隆")
    print("7. 原生SQL - 支持复杂查询")
    print("8. 关联查询 - 预加载关联数据")
    print("9. 聚合查询 - 统计和分组")
    print("10. 分页查询 - 高效的分页处理")