"""
SQLAlchemy高级查询示例
展示SQLAlchemy的强大查询能力
"""

from app.core.repositories.advanced_repository import AdvancedRepository
from app.models.entities.user import User
from app.models.entities.post import Post
from app.models.entities.comment import Comment
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime, date, timedelta
from typing import List, Dict, Any


def demo_advanced_queries():
    """演示高级查询功能"""
    print("🚀 SQLAlchemy高级查询演示")
    print("=" * 50)
    
    # 创建数据库连接
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 创建Repository
    user_repo = AdvancedRepository(User, session)
    post_repo = AdvancedRepository(Post, session)
    comment_repo = AdvancedRepository(Comment, session)
    
    # 创建测试数据
    create_test_data(session)
    
    # 1. 复杂条件查询
    print("\n1. 复杂条件查询")
    conditions = {
        "status": {"operator": "eq", "value": "active"},
        "created_at": {"operator": "gte", "value": date.today() - timedelta(days=30)},
        "email": {"operator": "like", "value": "@example.com"}
    }
    users = user_repo.filter_by_conditions(conditions)
    print(f"活跃用户（最近30天，@example.com邮箱）: {len(users)}")
    
    # 2. 全文搜索
    print("\n2. 全文搜索")
    search_results = user_repo.search_by_text(["username", "first_name", "last_name"], "john")
    print(f"搜索'john'的结果: {len(search_results)}")
    
    # 3. 日期范围查询
    print("\n3. 日期范围查询")
    start_date = date.today() - timedelta(days=7)
    end_date = date.today()
    recent_users = user_repo.filter_by_date_range("created_at", start_date, end_date)
    print(f"最近7天创建的用户: {len(recent_users)}")
    
    # 4. 本周数据
    print("\n4. 本周数据")
    this_week_users = user_repo.filter_by_this_week("created_at")
    print(f"本周创建的用户: {len(this_week_users)}")
    
    # 5. 本月数据
    print("\n5. 本月数据")
    this_month_users = user_repo.filter_by_this_month("created_at")
    print(f"本月创建的用户: {len(this_month_users)}")
    
    # 6. 关联查询
    print("\n6. 关联查询")
    user_with_posts = user_repo.get_with_relations(1, ["posts"])
    if user_with_posts:
        print(f"用户及其文章: {user_with_posts.username}")
        print(f"文章数量: {len(user_with_posts.posts) if hasattr(user_with_posts, 'posts') else 0}")
    
    # 7. 聚合查询
    print("\n7. 聚合查询")
    status_count = user_repo.count_by_field("status", "active")
    print(f"活跃用户数量: {status_count}")
    
    # 8. 字段统计
    print("\n8. 字段统计")
    login_stats = user_repo.get_field_stats("login_count")
    print(f"登录次数统计: {login_stats}")
    
    # 9. 分组统计
    print("\n9. 分组统计")
    status_groups = user_repo.group_by_field("status")
    print(f"按状态分组: {status_groups}")
    
    # 10. 多字段排序
    print("\n10. 多字段排序")
    order_fields = [("status", "asc"), ("created_at", "desc")]
    sorted_users = user_repo.order_by_multiple(order_fields)
    print(f"排序后的用户: {len(sorted_users)}")
    
    # 11. 分页查询
    print("\n11. 分页查询")
    page_result = user_repo.paginate(page=1, per_page=5, order_by="created_at", order_direction="desc")
    print(f"分页结果: 第{page_result['page']}页，共{page_result['pages']}页")
    print(f"当前页用户数: {len(page_result['items'])}")
    
    # 12. 原生SQL查询
    print("\n12. 原生SQL查询")
    sql_result = user_repo.get_by_sql(
        "SELECT username, email FROM users WHERE status = :status",
        {"status": "active"}
    )
    print(f"原生SQL查询结果: {len(sql_result)}")
    
    # 13. CASE语句查询
    print("\n13. CASE语句查询")
    case_conditions = {"active": "active", "inactive": "inactive"}
    case_users = user_repo.get_by_case_statement("status", case_conditions)
    print(f"CASE语句查询结果: {len(case_users)}")
    
    # 14. 日期部分提取
    print("\n14. 日期部分提取")
    today_users = user_repo.get_by_date_extract("created_at", "day", date.today().day)
    print(f"今天创建的用户: {len(today_users)}")
    
    # 15. JSON字段查询
    print("\n15. JSON字段查询")
    json_users = user_repo.get_by_json_field("profile_data", "age", 25)
    print(f"年龄为25的用户: {len(json_users)}")
    
    # 16. 数组包含查询
    print("\n16. 数组包含查询")
    array_users = user_repo.get_by_array_contains("permissions", "admin")
    print(f"包含admin权限的用户: {len(array_users)}")
    
    # 17. 数组重叠查询
    print("\n17. 数组重叠查询")
    overlap_users = user_repo.get_by_array_overlaps("permissions", ["admin", "user"])
    print(f"权限与['admin', 'user']重叠的用户: {len(overlap_users)}")
    
    # 18. 批量更新
    print("\n18. 批量更新")
    updated_count = user_repo.bulk_update_by_conditions(
        {"status": "pending"}, 
        {"status": "active"}
    )
    print(f"批量更新数量: {updated_count}")
    
    # 19. 批量删除
    print("\n19. 批量删除")
    deleted_count = user_repo.bulk_delete_by_conditions({"status": "inactive"})
    print(f"批量删除数量: {deleted_count}")
    
    # 20. 事务操作
    print("\n20. 事务操作")
    def create_user_with_posts():
        user = user_repo.create(
            username="transaction_user",
            email="transaction@example.com",
            password="password",
            first_name="Transaction",
            last_name="User"
        )
        return user
    
    try:
        result = user_repo.execute_in_transaction(create_user_with_posts)
        print(f"事务操作成功: {result.username}")
    except Exception as e:
        print(f"事务操作失败: {e}")


def demo_relationship_queries():
    """演示关系查询"""
    print("\n🔗 关系查询演示")
    print("=" * 50)
    
    # 创建数据库连接
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 创建Repository
    user_repo = AdvancedRepository(User, session)
    post_repo = AdvancedRepository(Post, session)
    
    # 创建测试数据
    create_test_data(session)
    
    # 1. 获取用户及其所有文章
    print("\n1. 获取用户及其所有文章")
    users_with_posts = user_repo.get_all_with_relations(["posts"])
    for user in users_with_posts:
        print(f"用户: {user.username}, 文章数: {len(user.posts) if hasattr(user, 'posts') else 0}")
    
    # 2. 获取用户及其所有评论
    print("\n2. 获取用户及其所有评论")
    users_with_comments = user_repo.get_all_with_relations(["comments"])
    for user in users_with_comments:
        print(f"用户: {user.username}, 评论数: {len(user.comments) if hasattr(user, 'comments') else 0}")
    
    # 3. 使用子查询加载关联数据
    print("\n3. 使用子查询加载关联数据")
    users_with_subquery = user_repo.get_with_subquery_relations(["posts", "comments"])
    for user in users_with_subquery:
        print(f"用户: {user.username}")
        if hasattr(user, 'posts'):
            print(f"  文章: {[post.title for post in user.posts]}")
        if hasattr(user, 'comments'):
            print(f"  评论: {[comment.content for comment in user.comments]}")


def demo_performance_optimization():
    """演示性能优化查询"""
    print("\n⚡ 性能优化查询演示")
    print("=" * 50)
    
    # 创建数据库连接
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 创建Repository
    user_repo = AdvancedRepository(User, session)
    
    # 创建测试数据
    create_test_data(session)
    
    # 1. 使用索引优化查询
    print("\n1. 使用索引优化查询")
    indexed_users = user_repo.query().filter(User.email == "user1@example.com").all()
    print(f"索引查询结果: {len(indexed_users)}")
    
    # 2. 使用LIMIT优化查询
    print("\n2. 使用LIMIT优化查询")
    limited_users = user_repo.query().limit(10).all()
    print(f"限制查询结果: {len(limited_users)}")
    
    # 3. 使用SELECT优化查询
    print("\n3. 使用SELECT优化查询")
    selected_users = user_repo.query().with_entities(User.username, User.email).all()
    print(f"选择字段查询结果: {len(selected_users)}")
    
    # 4. 使用EXISTS优化查询
    print("\n4. 使用EXISTS优化查询")
    from sqlalchemy import exists
    users_with_posts = user_repo.query().filter(
        exists().where(Post.user_id == User.id)
    ).all()
    print(f"存在文章的用户: {len(users_with_posts)}")


def create_test_data(session):
    """创建测试数据"""
    # 创建用户
    users = [
        User(username="user1", email="user1@example.com", password="password", first_name="User", last_name="One", status="active"),
        User(username="user2", email="user2@example.com", password="password", first_name="User", last_name="Two", status="active"),
        User(username="user3", email="user3@example.com", password="password", first_name="User", last_name="Three", status="inactive"),
        User(username="john_doe", email="john@example.com", password="password", first_name="John", last_name="Doe", status="active"),
        User(username="jane_smith", email="jane@example.com", password="password", first_name="Jane", last_name="Smith", status="pending"),
    ]
    
    for user in users:
        session.add(user)
    
    session.commit()
    
    # 创建文章
    posts = [
        Post(title="Post 1", content="Content 1", user_id=1, status="published"),
        Post(title="Post 2", content="Content 2", user_id=1, status="draft"),
        Post(title="Post 3", content="Content 3", user_id=2, status="published"),
    ]
    
    for post in posts:
        session.add(post)
    
    session.commit()
    
    # 创建评论
    comments = [
        Comment(content="Comment 1", user_id=1, post_id=1),
        Comment(content="Comment 2", user_id=2, post_id=1),
        Comment(content="Comment 3", user_id=1, post_id=2),
    ]
    
    for comment in comments:
        session.add(comment)
    
    session.commit()


if __name__ == "__main__":
    print("🎯 SQLAlchemy高级查询完整演示")
    print("=" * 60)
    
    # 运行演示
    demo_advanced_queries()
    demo_relationship_queries()
    demo_performance_optimization()
    
    print("\n🎉 演示完成！")
    print("\n💡 SQLAlchemy强大功能:")
    print("1. 复杂条件查询 - 支持多种操作符")
    print("2. 全文搜索 - 多字段模糊搜索")
    print("3. 日期范围查询 - 灵活的时间过滤")
    print("4. 关联查询 - 预加载关联数据")
    print("5. 聚合查询 - 统计和分组")
    print("6. 分页查询 - 高效的分页处理")
    print("7. 原生SQL - 复杂查询支持")
    print("8. 批量操作 - 高效的批量处理")
    print("9. 事务管理 - 数据一致性保证")
    print("10. 性能优化 - 查询性能优化")