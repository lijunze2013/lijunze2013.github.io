import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, session, render_template_string, redirect, url_for
from flask_cors import CORS
from functools import wraps
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.test import create_environ
from werkzeug.wrappers import Request

# 初始化Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'

# 配置CORS
CORS(app, supports_credentials=True, origins=[
    "https://your-project.vercel.app",
    "http://localhost:5500"
])

# 数据库模型
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    last_login = Column(DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    link = Column(String(200))
    image = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.title,
            'description': self.description,
            'image': self.image,
            'link': self.link,
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }


# 初始化数据库
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)


# 初始化默认数据
def init_default_data():
    db = SessionLocal()
    if not db.query(User).filter_by(username='admin').first():
        admin = User(username='admin')
        admin.set_password('li201338')  # 默认密码
        db.add(admin)
    if not db.query(Project).first():
        default_projects = [
            Project(title='个人博客系统', description='基于Flask构建的个人展示平台',
                    image='https://picsum.photos/seed/project1/300/200', link='#'),
            Project(title='任务管理应用', description='简洁高效的任务管理工具',
                    image='https://picsum.photos/seed/project2/300/200', link='#')
        ]
        db.add_all(default_projects)
    db.commit()
    db.close()


init_default_data()


# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect('/admin/login')
        return f(*args, **kwargs)

    return decorated_function


# 全局CSS样式
CSS_STYLES = """
<style>
:root {
    --primary-color: #3498db;
    --secondary-color: #2ecc71;
    --dark-color: #2c3e50;
    --light-color: #ecf0f1;
    --danger-color: #e74c3c;
    --text-color: #333;
    --shadow: 0 2px 10px rgba(0,0,0,0.1);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

body {
    color: var(--text-color);
    line-height: 1.6;
    background-color: #f9f9f9;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* 导航栏样式 */
.navbar {
    background-color: white;
    box-shadow: var(--shadow);
    padding: 15px 0;
    position: fixed;
    width: 100%;
    top: 0;
    z-index: 100;
    transition: background-color 0.3s;
}

.navbar.scrolled {
    background-color: rgba(255, 255, 255, 0.95);
    padding: 10px 0;
}

.navbar .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--primary-color);
    text-decoration: none;
}

.nav-links {
    display: flex;
    list-style: none;
}

.nav-links li {
    margin-left: 25px;
}

.nav-links a {
    color: var(--text-color);
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s;
}

.nav-links a:hover {
    color: var(--primary-color);
}

.mobile-menu-btn {
    display: none;
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
}

/* 按钮样式 */
.btn {
    display: inline-block;
    padding: 10px 20px;
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    text-decoration: none;
    font-weight: 500;
    transition: background-color 0.3s;
}

.btn:hover {
    background-color: #2980b9;
}

.btn-secondary {
    background-color: var(--secondary-color);
}

.btn-secondary:hover {
    background-color: #27ae60;
}

.btn-danger {
    background-color: var(--danger-color);
}

.btn-danger:hover {
    background-color: #c0392b;
}

/* 英雄区域样式 */
.hero {
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 0 20px;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    margin-top: 70px;
}

.hero h1 {
    font-size: 3rem;
    margin-bottom: 20px;
}

.hero p {
    font-size: 1.2rem;
    max-width: 700px;
    margin-bottom: 30px;
}

/* 部分通用样式 */
.section {
    padding: 100px 0;
}

.section-title {
    text-align: center;
    margin-bottom: 60px;
    font-size: 2.2rem;
    color: var(--dark-color);
}

/* 项目样式 */
.projects-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 30px;
}

.project-card {
    background-color: white;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: var(--shadow);
    transition: transform 0.3s;
}

.project-card:hover {
    transform: translateY(-5px);
}

.project-image {
    width: 100%;
    height: 200px;
    object-fit: cover;
}

.project-card h3 {
    padding: 20px;
    padding-bottom: 10px;
}

.project-card p {
    padding: 0 20px;
    padding-bottom: 20px;
}

.project-card .btn {
    margin: 0 20px 20px;
    width: calc(100% - 40px);
    text-align: center;
}

/* 关于部分样式 */
.about-section {
    background-color: white;
    padding: 40px;
    border-radius: 10px;
    box-shadow: var(--shadow);
}

.about-section p {
    margin-bottom: 20px;
}

/* 联系表单样式 */
.contact-form {
    max-width: 600px;
    margin: 0 auto;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
}

.form-group input,
.form-group textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 1rem;
}

.form-group textarea {
    height: 150px;
    resize: vertical;
}

/* 页脚样式 */
.footer {
    background-color: var(--dark-color);
    color: white;
    padding: 50px 0 20px;
    margin-top: 50px;
}

.footer-content {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 30px;
    margin-bottom: 40px;
}

.footer-section h3 {
    margin-bottom: 20px;
    position: relative;
}

.footer-section p,
.footer-section ul {
    margin-bottom: 10px;
}

.footer-section ul {
    list-style: none;
}

.footer-section a {
    color: var(--light-color);
    text-decoration: none;
    transition: color 0.3s;
}

.footer-section a:hover {
    color: var(--primary-color);
}

.footer-bottom {
    text-align: center;
    padding-top: 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* 管理后台样式 */
.admin-container {
    display: flex;
    min-height: 100vh;
    margin-top: 70px;
}

.sidebar {
    width: 250px;
    background-color: var(--dark-color);
    color: white;
    padding: 30px 0;
    height: calc(100vh - 70px);
    position: fixed;
    overflow-y: auto;
}

.sidebar-menu {
    list-style: none;
}

.sidebar-menu li {
    margin-bottom: 10px;
}

.sidebar-menu a {
    color: var(--light-color);
    text-decoration: none;
    display: block;
    padding: 10px 20px;
    transition: background-color 0.3s;
}

.sidebar-menu a:hover,
.sidebar-menu a.active {
    background-color: rgba(255, 255, 255, 0.1);
}

.admin-content {
    flex: 1;
    margin-left: 250px;
    padding: 30px;
}

.admin-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

/* 表单样式 */
.form-container {
    max-width: 600px;
    margin: 0 auto;
    background-color: white;
    padding: 30px;
    border-radius: 10px;
    box-shadow: var(--shadow);
}

.form-title {
    margin-bottom: 20px;
    text-align: center;
}

.form-message {
    padding: 10px;
    margin-bottom: 20px;
    border-radius: 5px;
    text-align: center;
}

.form-message.success {
    background-color: rgba(46, 204, 113, 0.2);
    color: var(--secondary-color);
}

.form-message.error {
    background-color: rgba(231, 76, 60, 0.2);
    color: var(--danger-color);
}

/* 表格样式 */
.table-container {
    overflow-x: auto;
    background-color: white;
    border-radius: 10px;
    box-shadow: var(--shadow);
}

.data-table {
    width: 100%;
    border-collapse: collapse;
}

.data-table th,
.data-table td {
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

.data-table th {
    background-color: var(--light-color);
    font-weight: bold;
}

/* 登录页面样式 */
.login-container {
    max-width: 400px;
    margin: 150px auto;
    background-color: white;
    padding: 30px;
    border-radius: 10px;
    box-shadow: var(--shadow);
}

/* 404页面样式 */
.not-found {
    text-align: center;
    padding: 100px 20px;
}

.not-found h1 {
    font-size: 5rem;
    margin-bottom: 20px;
    color: var(--primary-color);
}

.not-found p {
    font-size: 1.2rem;
    margin-bottom: 30px;
}

/* 响应式样式 */
@media (max-width: 768px) {
    .nav-links {
        display: none;
    }

    .mobile-menu-btn {
        display: block;
    }

    .mobile-nav {
        position: fixed;
        top: 70px;
        left: 0;
        width: 100%;
        background-color: white;
        box-shadow: var(--shadow);
        padding: 20px;
        display: none;
    }

    .mobile-nav.active {
        display: block;
    }

    .mobile-nav ul {
        list-style: none;
    }

    .mobile-nav li {
        margin-bottom: 15px;
    }

    .mobile-nav a {
        color: var(--text-color);
        text-decoration: none;
        font-size: 1.1rem;
    }

    .hero h1 {
        font-size: 2.2rem;
    }

    .section-title {
        font-size: 1.8rem;
    }

    .admin-container {
        flex-direction: column;
    }

    .sidebar {
        width: 100%;
        height: auto;
        position: relative;
    }

    .admin-content {
        margin-left: 0;
        margin-top: 20px;
    }
}
</style>
"""

# 全局JavaScript
GLOBAL_JS = """
<script>
// API基础URL
const API_BASE_URL = '/api';

// 导航栏滚动效果
document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.getElementById('navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            navbar.classList.toggle('scrolled', window.scrollY > 50);
        });
    }

    // 移动端菜单切换
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileNav = document.getElementById('mobileNav');
    if (mobileMenuBtn && mobileNav) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileNav.classList.toggle('active');
            const icon = mobileMenuBtn.querySelector('i');
            icon.classList.toggle('fa-bars');
            icon.classList.toggle('fa-times');
        });
    }

    // 平滑滚动
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = anchor.getAttribute('href');
            if (targetId === '#') return;

            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
                if (mobileNav && mobileNav.classList.contains('active')) {
                    mobileNav.classList.remove('active');
                    mobileMenuBtn.querySelector('i').classList.replace('fa-times', 'fa-bars');
                }
            }
        });
    });

    // 滚动动画
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.project-card, .about-section');
        elements.forEach(element => {
            const position = element.getBoundingClientRect().top;
            if (position < window.innerHeight * 0.85) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    };

    document.querySelectorAll('.project-card, .about-section').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    });

    window.addEventListener('load', animateOnScroll);
    window.addEventListener('scroll', animateOnScroll);

    // 检查页面类型并初始化相应功能
    if (window.location.pathname.includes('/admin')) {
        if (window.location.pathname.includes('/login')) {
            initLogin();
        } else {
            checkLogin();
        }
    } else {
        // 首页加载项目
        loadProjects();
    }
});

// 加载项目数据
function loadProjects() {
    const projectsGrid = document.querySelector('.projects-grid');
    if (!projectsGrid) return;

    projectsGrid.innerHTML = '<div style="text-align: center; padding: 50px;">加载项目中...</div>';

    fetch(`${API_BASE_URL}/projects`)
        .then(response => {
            if (!response.ok) throw new Error('加载失败');
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                projectsGrid.innerHTML = '';
                data.projects.forEach(project => {
                    const card = document.createElement('div');
                    card.className = 'project-card';
                    card.innerHTML = `
                        <img src="${project.image}" alt="${project.name}" class="project-image">
                        <h3>${project.name}</h3>
                        <p>${project.description}</p>
                        <a href="${project.link}" class="btn btn-secondary">查看详情</a>
                    `;
                    projectsGrid.appendChild(card);
                });
            }
        })
        .catch(error => {
            console.error('加载项目失败:', error);
            projectsGrid.innerHTML = '<div style="text-align: center; padding: 50px; color: var(--danger-color);">加载失败，请稍后重试</div>';
        });
}

// 管理后台功能
function checkLogin() {
    fetch(`${API_BASE_URL}/check-login`, { credentials: 'include' })
        .then(response => response.json())
        .then(data => {
            if (!data.logged_in) {
                window.location.href = '/admin/login';
            } else {
                initAdminPage();
            }
        })
        .catch(error => {
            console.error('检查登录失败:', error);
            alert('服务器连接失败');
        });
}

function initAdminPage() {
    // 登出功能
    document.getElementById('logoutBtn')?.addEventListener('click', function() {
        fetch(`${API_BASE_URL}/logout`, { 
            method: 'POST', 
            credentials: 'include' 
        })
        .then(() => {
            window.location.href = '/admin/login';
        })
        .catch(error => {
            console.error('登出失败:', error);
            alert('登出失败');
        });
    });

    // 初始化不同页面
    if (window.location.pathname.includes('dashboard')) {
        initDashboard();
    } else if (window.location.pathname.includes('projects')) {
        initProjects();
    } else if (window.location.pathname.includes('profile')) {
        initProfile();
    } else if (window.location.pathname.includes('settings')) {
        initSettings();
    }
}

// 登录功能
function initLogin() {
    const form = document.getElementById('loginForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const message = document.getElementById('message');

            fetch(`${API_BASE_URL}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
                credentials: 'include'
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    message.textContent = '登录成功，正在跳转...';
                    message.className = 'form-message success';
                    setTimeout(() => {
                        window.location.href = '/admin/dashboard';
                    }, 1000);
                } else {
                    message.textContent = data.message;
                    message.className = 'form-message error';
                }
            })
            .catch(error => {
                console.error('登录失败:', error);
                message.textContent = '服务器连接失败';
                message.className = 'form-message error';
            });
        });
    }
}

// 项目管理
function initProjects() {
    loadProjectsList();

    const form = document.getElementById('projectForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const projectData = {
                name: document.getElementById('projectName').value,
                description: document.getElementById('projectDescription').value,
                image: document.getElementById('projectImage').value,
                link: document.getElementById('projectLink').value
            };

            fetch(`${API_BASE_URL}/projects`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(projectData),
                credentials: 'include'
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    document.getElementById('message').textContent = '项目添加成功';
                    document.getElementById('message').className = 'form-message success';
                    form.reset();
                    loadProjectsList();
                    setTimeout(() => {
                        document.getElementById('message').textContent = '';
                    }, 3000);
                } else {
                    document.getElementById('message').textContent = data.message;
                    document.getElementById('message').className = 'form-message error';
                }
            })
            .catch(error => {
                console.error('添加项目失败:', error);
                document.getElementById('message').textContent = '添加失败';
                document.getElementById('message').className = 'form-message error';
            });
        });
    }
}

function loadProjectsList() {
    const listContainer = document.getElementById('projectsList');
    if (!listContainer) return;

    listContainer.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 20px;">加载项目中...</td></tr>';

    fetch(`${API_BASE_URL}/projects`, { credentials: 'include' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                if (data.projects.length === 0) {
                    listContainer.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 20px;">暂无项目</td></tr>';
                    return;
                }

                listContainer.innerHTML = data.projects.map(project => `
                    <tr>
                        <td>${project.id}</td>
                        <td>${project.name}</td>
                        <td>${project.description.substring(0, 50)}${project.description.length > 50 ? '...' : ''}</td>
                        <td>
                            <button onclick="editProject(${project.id})" class="btn">编辑</button>
                            <button onclick="deleteProject(${project.id})" class="btn btn-danger">删除</button>
                        </td>
                    </tr>
                `).join('');
            }
        })
        .catch(error => {
            console.error('加载项目列表失败:', error);
            listContainer.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 20px; color: var(--danger-color);">加载失败</td></tr>';
        });
}

function deleteProject(id) {
    if (confirm('确定要删除这个项目吗？')) {
        fetch(`${API_BASE_URL}/projects/${id}`, {
            method: 'DELETE',
            credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                loadProjectsList();
            } else {
                alert('删除失败: ' + data.message);
            }
        })
        .catch(error => {
            console.error('删除项目失败:', error);
            alert('删除失败');
        });
    }
}

// 编辑项目功能简化版
function editProject(id) {
    alert('编辑功能 - 项目ID: ' + id);
    // 完整实现需要添加编辑表单和PUT请求
}

// 初始化仪表盘
function initDashboard() {
    fetch(`${API_BASE_URL}/dashboard`, { credentials: 'include' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                document.getElementById('totalVisits').textContent = data.dashboard.stats.total_visits;
                document.getElementById('lastLogin').textContent = data.dashboard.stats.last_login;
            }
        })
        .catch(error => {
            console.error('加载仪表盘数据失败:', error);
        });
}

// 初始化个人资料页面
function initProfile() {
    // 个人资料功能实现
    const form = document.getElementById('profileForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            document.getElementById('message').textContent = '个人资料更新功能已触发（实际实现需要添加API调用）';
            document.getElementById('message').className = 'form-message success';

            setTimeout(() => {
                document.getElementById('message').textContent = '';
            }, 3000);
        });
    }
}

// 初始化设置页面
function initSettings() {
    // 设置功能实现
    const form = document.getElementById('settingsForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            document.getElementById('message').textContent = '设置保存功能已触发（实际实现需要添加API调用）';
            document.getElementById('message').className = 'form-message success';

            setTimeout(() => {
                document.getElementById('message').textContent = '';
            }, 3000);
        });
    }
}
</script>
"""


# 通用头部
def get_header():
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>个人博客与项目展示</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        {CSS_STYLES}
    </head>
    <body>
        <nav id="navbar" class="navbar">
            <div class="container">
                <a href="/" class="logo">我的博客</a>
                <button id="mobileMenuBtn" class="mobile-menu-btn">
                    <i class="fas fa-bars"></i>
                </button>
                <ul class="nav-links">
                    <li><a href="/#home">首页</a></li>
                    <li><a href="/#projects">项目</a></li>
                    <li><a href="/#about">关于</a></li>
                    <li><a href="/#contact">联系</a></li>
                    <li><a href="/admin/login">管理</a></li>
                </ul>
            </div>
        </nav>
        <div id="mobileNav" class="mobile-nav">
            <ul>
                <li><a href="/#home">首页</a></li>
                <li><a href="/#projects">项目</a></li>
                <li><a href="/#about">关于</a></li>
                <li><a href="/#contact">联系</a></li>
                <li><a href="/admin/login">管理</a></li>
            </ul>
        </div>
    """


# 通用底部
def get_footer():
    return f"""
        <footer class="footer">
            <div class="container">
                <div class="footer-content">
                    <div class="footer-section about">
                        <h3>关于我</h3>
                        <p>热爱技术的开发者，专注于Web开发和项目管理。</p>
                    </div>
                    <div class="footer-section links">
                        <h3>快速链接</h3>
                        <ul>
                            <li><a href="/#home">首页</a></li>
                            <li><a href="/#projects">项目</a></li>
                            <li><a href="/#about">关于</a></li>
                        </ul>
                    </div>
                    <div class="footer-section contact">
                        <h3>联系我</h3>
                        <p><i class="fas fa-envelope"></i> contact@example.com</p>
                    </div>
                </div>
                <div class="footer-bottom">
                    <p>&copy; {datetime.now().year} 我的博客 | 设计与开发</p>
                </div>
            </div>
        </footer>
        {GLOBAL_JS}
    </body>
    </html>
    """


# 路由 - 首页
@app.route('/')
def index():
    page = get_header()
    page += f"""
        <section id="home" class="hero">
            <div class="container">
                <h1>欢迎来到我的个人博客</h1>
                <p>展示我的项目和技能，分享我的学习和开发经验。</p>
                <a href="#projects" class="btn">查看我的项目</a>
            </div>
        </section>

        <section id="projects" class="section">
            <div class="container">
                <h2 class="section-title">我的项目</h2>
                <div class="projects-grid">
                    <!-- 项目将通过JavaScript动态加载 -->
                </div>
            </div>
        </section>

        <section id="about" class="section">
            <div class="container">
                <h2 class="section-title">关于我</h2>
                <div class="about-section">
                    <p>大家好，我是一名热爱编程的开发者，专注于Web开发领域。</p>
                    <p>我熟悉多种编程语言和框架，包括Python、JavaScript、Flask等。</p>
                    <p>这个博客是我展示个人项目和分享技术心得的平台，希望能和大家一起交流学习。</p>
                </div>
            </div>
        </section>

        <section id="contact" class="section">
            <div class="container">
                <h2 class="section-title">联系我</h2>
                <form class="contact-form">
                    <div class="form-group">
                        <label for="name">姓名</label>
                        <input type="text" id="name" name="name" required>
                    </div>
                    <div class="form-group">
                        <label for="email">邮箱</label>
                        <input type="email" id="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label for="message">留言</label>
                        <textarea id="message" name="message" required></textarea>
                    </div>
                    <button type="submit" class="btn">发送消息</button>
                </form>
            </div>
        </section>
    """
    page += get_footer()
    return page


# 路由 - 404页面
@app.route('/404')
def not_found():
    page = get_header()
    page += f"""
        <section class="not-found">
            <div class="container">
                <h1>404</h1>
                <p>抱歉，您访问的页面不存在。</p>
                <a href="/" class="btn">返回首页</a>
            </div>
        </section>
    """
    page += get_footer()
    return page


# 路由 - 管理后台登录页
@app.route('/admin/login')
def admin_login():
    if 'username' in session:
        return redirect('/admin/dashboard')

    page = get_header()
    page += f"""
        <div class="login-container">
            <h2 class="form-title">管理员登录</h2>
            <div id="message" class="form-message"></div>
            <form id="loginForm">
                <div class="form-group">
                    <label for="username">用户名</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">密码</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn">登录</button>
            </form>
        </div>
    """
    page += get_footer()
    return page


# 路由 - 管理后台仪表盘
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    page = get_header()
    page += f"""
        <div class="admin-container">
            <div class="sidebar">
                <ul class="sidebar-menu">
                    <li><a href="/admin/dashboard" class="active">仪表盘</a></li>
                    <li><a href="/admin/projects">项目管理</a></li>
                    <li><a href="/admin/profile">个人资料</a></li>
                    <li><a href="/admin/settings">系统设置</a></li>
                    <li><a href="#" id="logoutBtn">退出登录</a></li>
                </ul>
            </div>
            <div class="admin-content">
                <div class="admin-header">
                    <h1>仪表盘</h1>
                </div>
                <div class="form-container">
                    <h2>网站统计</h2>
                    <p><strong>总访问量：</strong> <span id="totalVisits">加载中...</span></p>
                    <p><strong>最后登录时间：</strong> <span id="lastLogin">加载中...</span></p>
                </div>
            </div>
        </div>
    """
    page += get_footer()
    return page


# 路由 - 项目管理
@app.route('/admin/projects')
@login_required
def admin_projects():
    page = get_header()
    page += f"""
        <div class="admin-container">
            <div class="sidebar">
                <ul class="sidebar-menu">
                    <li><a href="/admin/dashboard">仪表盘</a></li>
                    <li><a href="/admin/projects" class="active">项目管理</a></li>
                    <li><a href="/admin/profile">个人资料</a></li>
                    <li><a href="/admin/settings">系统设置</a></li>
                    <li><a href="#" id="logoutBtn">退出登录</a></li>
                </ul>
            </div>
            <div class="admin-content">
                <div class="admin-header">
                    <h1>项目管理</h1>
                </div>

                <div class="form-container">
                    <h2>添加新项目</h2>
                    <div id="message" class="form-message"></div>
                    <form id="projectForm">
                        <div class="form-group">
                            <label for="projectName">项目名称</label>
                            <input type="text" id="projectName" name="projectName" required>
                        </div>
                        <div class="form-group">
                            <label for="projectDescription">项目描述</label>
                            <textarea id="projectDescription" name="projectDescription" required></textarea>
                        </div>
                        <div class="form-group">
                            <label for="projectImage">图片URL</label>
                            <input type="text" id="projectImage" name="projectImage" placeholder="https://example.com/image.jpg">
                        </div>
                        <div class="form-group">
                            <label for="projectLink">项目链接</label>
                            <input type="url" id="projectLink" name="projectLink" placeholder="https://example.com">
                        </div>
                        <button type="submit" class="btn">添加项目</button>
                    </form>
                </div>

                <div style="margin-top: 30px;">
                    <h2>项目列表</h2>
                    <div class="table-container">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>名称</th>
                                    <th>描述</th>
                                    <th>操作</th>
                                </tr>
                            </thead>
                            <tbody id="projectsList">
                                <!-- 项目列表将通过JavaScript动态加载 -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    """
    page += get_footer()
    return page


# 路由 - 个人资料
@app.route('/admin/profile')
@login_required
def admin_profile():
    page = get_header()
    page += f"""
        <div class="admin-container">
            <div class="sidebar">
                <ul class="sidebar-menu">
                    <li><a href="/admin/dashboard">仪表盘</a></li>
                    <li><a href="/admin/projects">项目管理</a></li>
                    <li><a href="/admin/profile" class="active">个人资料</a></li>
                    <li><a href="/admin/settings">系统设置</a></li>
                    <li><a href="#" id="logoutBtn">退出登录</a></li>
                </ul>
            </div>
            <div class="admin-content">
                <div class="admin-header">
                    <h1>个人资料</h1>
                </div>
                <div class="form-container">
                    <div id="message" class="form-message"></div>
                    <form id="profileForm">
                        <div class="form-group">
                            <label for="profileUsername">用户名</label>
                            <input type="text" id="profileUsername" value="admin" disabled>
                        </div>
                        <div class="form-group">
                            <label for="profileEmail">邮箱</label>
                            <input type="email" id="profileEmail" placeholder="your@email.com">
                        </div>
                        <div class="form-group">
                            <label for="profileBio">个人简介</label>
                            <textarea id="profileBio" placeholder="介绍一下自己..."></textarea>
                        </div>
                        <button type="submit" class="btn">保存资料</button>
                    </form>
                </div>
            </div>
        </div>
    """
    page += get_footer()
    return page


# 路由 - 系统设置
@app.route('/admin/settings')
@login_required
def admin_settings():
    page = get_header()
    page += f"""
        <div class="admin-container">
            <div class="sidebar">
                <ul class="sidebar-menu">
                    <li><a href="/admin/dashboard">仪表盘</a></li>
                    <li><a href="/admin/projects">项目管理</a></li>
                    <li><a href="/admin/profile">个人资料</a></li>
                    <li><a href="/admin/settings" class="active">系统设置</a></li>
                    <li><a href="#" id="logoutBtn">退出登录</a></li>
                </ul>
            </div>
            <div class="admin-content">
                <div class="admin-header">
                    <h1>系统设置</h1>
                </div>
                <div class="form-container">
                    <h2>网站设置</h2>
                    <div id="message" class="form-message"></div>
                    <form id="settingsForm">
                        <div class="form-group">
                            <label for="siteName">网站名称</label>
                            <input type="text" id="siteName" value="我的博客">
                        </div>
                        <div class="form-group">
                            <label for="siteDescription">网站描述</label>
                            <textarea id="siteDescription">个人博客与项目展示平台</textarea>
                        </div>
                        <div class="form-group">
                            <label for="siteFooter">页脚信息</label>
                            <input type="text" id="siteFooter" value="© 2023 我的博客 | 设计与开发">
                        </div>
                        <button type="submit" class="btn">保存设置</button>
                    </form>
                </div>
            </div>
        </div>
    """
    page += get_footer()
    return page


# API - 登录
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    db = SessionLocal()
    user = db.query(User).filter_by(username=data.get('username')).first()

    if user and user.check_password(data.get('password')):
        session['username'] = user.username
        user.last_login = datetime.now()
        db.commit()
        db.close()
        return jsonify({'status': 'success', 'message': '登录成功'})

    db.close()
    return jsonify({'status': 'error', 'message': '用户名或密码错误'}), 401


# API - 登出
@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'status': 'success', 'message': '已退出登录'})


# API - 检查登录状态
@app.route('/api/check-login', methods=['GET'])
def check_login():
    return jsonify({
        'status': 'success',
        'logged_in': 'username' in session
    })


# API - 获取仪表盘数据
@app.route('/api/dashboard', methods=['GET'])
@login_required
def dashboard():
    db = SessionLocal()
    user = db.query(User).filter_by(username=session['username']).first()
    total_visits = 128  # 模拟数据

    return jsonify({
        'status': 'success',
        'dashboard': {
            'stats': {
                'total_visits': total_visits,
                'last_login': user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else '从未登录'
            }
        }
    })


# API - 获取项目列表
@app.route('/api/projects', methods=['GET'])
def get_projects():
    db = SessionLocal()
    projects = db.query(Project).all()
    db.close()
    return jsonify({
        'status': 'success',
        'projects': [p.to_dict() for p in projects]
    })


# API - 创建项目
@app.route('/api/projects', methods=['POST'])
@login_required
def create_project():
    data = request.get_json()
    new_project = Project(
        title=data.get('name'),
        description=data.get('description'),
        image=data.get('image'),
        link=data.get('link')
    )

    db = SessionLocal()
    db.add(new_project)
    db.commit()
    db.close()

    return jsonify({
        'status': 'success',
        'message': '项目创建成功',
        'project': new_project.to_dict()
    })


# API - 删除项目
@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    db = SessionLocal()
    project = db.query(Project).get(project_id)

    if not project:
        db.close()
        return jsonify({'status': 'error', 'message': '项目不存在'}), 404

    db.delete(project)
    db.commit()
    db.close()

    return jsonify({'status': 'success', 'message': '项目已删除'})


# Vercel原生Handler（关键修改）
def handler(event, context):
    # 转换Vercel事件为Flask环境
    environ = create_environ(
        path=event.get('path', '/'),
        method=event.get('httpMethod', 'GET'),
        query_string=event.get('queryStringParameters', {}),
        headers=event.get('headers', {}),
        data=event.get('body', '')
    )

    # 处理请求
    with app.request_context(environ):
        response = app.full_dispatch_request()

        # 构建返回结果
        return {
            'statusCode': response.status_code,
            'headers': dict(response.headers),
            'body': response.get_data(as_text=True)
        }
