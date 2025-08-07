from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

# 初始化 Flask 应用
app = Flask(__name__)

# 配置数据库：优先使用外部数据库，否则用 Vercel 临时目录的 SQLite
if os.environ.get('DATABASE_URL'):
    # 外部数据库（如 PostgreSQL/MySQL），需要替换为实际环境变量名
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL'].replace('postgres://', 'postgresql://')
else:
    # Vercel 临时目录（可读写）
    tmp_dir = os.environ.get('TMPDIR', '/tmp')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(tmp_dir, 'site.db')}"

# 关闭 SQLAlchemy 追踪（优化性能）
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 随机生成 SECRET_KEY（生产环境建议用环境变量）
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-default-secret-key')

# 初始化 SQLAlchemy
db = SQLAlchemy(app)

# 定义模型（示例：文章模型）
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Post {self.title}>'

# 创建表（首次运行自动创建，生产环境建议用迁移工具）
with app.app_context():
    db.create_all()

# 路由示例：首页
@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

# 路由示例：添加文章
@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_post = Post(title=title, content=content)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_post.html')

# 主程序入口
if __name__ == '__main__':
    # 本地开发用 debug，生产环境由 Vercel 托管
    app.run(debug=os.environ.get('DEBUG', False))
