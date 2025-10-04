import os
import unittest
import click

from flask.cli import FlaskGroup
from flask_migrate import (
    Migrate,
    init as mg_init,
    migrate as mg_migrate,
    upgrade as mg_upgrade,
    downgrade as mg_downgrade,
    revision as mg_revision,
    stamp as mg_stamp,
    show as mg_show,
    heads as mg_heads,
    current as mg_current,
    history as mg_history,
)

# 你的应用工厂 & 数据库对象
# app/__init__.py 必须提供 create_app(config_name) 并在其中 init_app(db)
from app import create_app, db
from app.models import User, Role, Post, Thought


def create_app_wrapper():
    """为 FlaskGroup 提供无参工厂：从环境变量读取配置名，默认 'default'。"""
    return create_app(os.getenv("FLASK_CONFIG") or "default")


# 初始化应用、CLI、迁移
app = create_app_wrapper()
cli = FlaskGroup(create_app=create_app_wrapper)
migrate = Migrate(app, db)  # 标准做法：应自动把 `db` 命令挂到 CLI


@app.shell_context_processor
def make_shell_context():
    """python manage.py shell 自动注入这些名字"""
    return dict(app=app, db=db, User=User, Role=Role, Post=Post, Thought=Thought)


@cli.command("test")
def test():
    """运行单元测试"""
    tests = unittest.TestLoader().discover("tests")
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    raise SystemExit(0 if result.wasSuccessful() else 1)


@cli.command("runserver")
@click.option("--host", default="0.0.0.0", show_default=True)
@click.option("--port", default=5000, type=int, show_default=True)
@click.option("--debug/--no-debug", default=True, show_default=True)
def runserver(host, port, debug):
    """开发服务器（等价于 flask run，可自选 host/port）"""
    app.run(debug=debug, host=host, port=port, use_reloader=debug)

# -------------------- 兜底的 db 命令组（显式转发到 flask_migrate） --------------------
@cli.group("db")
def db_group():
    """数据库迁移命令（兜底版）"""
    pass

def _ctx():
    return app.app_context()

@db_group.command("init")
@click.option("--directory", default=None, help="迁移目录，默认 'migrations'")
def db_init(directory):
    with _ctx():
        mg_init(directory)

@db_group.command("migrate")
@click.option("-m", "--message", default=None, help="迁移说明")
@click.option("--directory", default=None)
@click.option("--rev-id", default=None, help="自定义 revision id")
def db_migrate(message, directory, rev_id):
    with _ctx():
        mg_migrate(directory=directory, message=message, rev_id=rev_id)

@db_group.command("upgrade")
@click.option("-r", "--revision", default="head", show_default=True,
              help="要升级到的版本（默认 head）")
@click.option("--directory", default=None)
def db_upgrade(revision, directory):
    with _ctx():
        mg_upgrade(directory=directory, revision=revision)

@db_group.command("downgrade")
@click.option("-r", "--revision", default="-1", show_default=True,
              help="回滚到指定版本（默认 -1 上一版本）")
@click.option("--directory", default=None)
def db_downgrade(revision, directory):
    with _ctx():
        mg_downgrade(directory=directory, revision=revision)

@db_group.command("revision")
@click.option("-m", "--message", default=None)
@click.option("--autogenerate", is_flag=True, default=False, show_default=True)
@click.option("--rev-id", default=None)
@click.option("--splice", is_flag=True, default=False, show_default=True)
@click.option("--head", default="head", show_default=True)
@click.option("--version-path", default=None)
@click.option("--branch-label", default=None)
@click.option("--depends-on", default=None)
def db_revision(message, autogenerate, rev_id, splice, head, version_path, branch_label, depends_on):
    with _ctx():
        mg_revision(
            message=message,
            autogenerate=autogenerate,
            rev_id=rev_id,
            splice=splice,
            head=head,
            version_path=version_path,
            branch_label=branch_label,
            depends_on=depends_on,
        )

@db_group.command("stamp")
@click.option("-r", "--revision", default="head", show_default=True)
@click.option("--directory", default=None)
def db_stamp(revision, directory):
    with _ctx():
        mg_stamp(directory=directory, revision=revision)

@db_group.command("show")
@click.option("-r", "--revision", default="head", show_default=True)
def db_show_cmd(revision):
    with _ctx():
        mg_show(revision)

@db_group.command("heads")
def db_heads_cmd():
    with _ctx():
        mg_heads()

@db_group.command("current")
def db_current_cmd():
    with _ctx():
        mg_current()

@db_group.command("history")
def db_history_cmd():
    with _ctx():
        mg_history()
