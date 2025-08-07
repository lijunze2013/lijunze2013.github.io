// API基础URL，根据环境自动切换
const API_BASE_URL = window.location.hostname.includes('github.io') 
    ? 'https://your-vercel-api-url.vercel.app/api'  // 替换为你的Vercel API地址
    : '/api';

// 页面加载时检查登录状态
document.addEventListener('DOMContentLoaded', function() {
    // 导航栏滚动效果
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

    // 检查页面类型并初始化相应功能
    if (window.location.pathname.includes('/admin')) {
        if (window.location.pathname.includes('/login')) {
            initLogin();
        } else {
            checkLogin();
        }
    }
});

// 检查登录状态
function checkLogin() {
    fetch(`${API_BASE_URL}/check-login`, { credentials: 'include' })
        .then(response => {
            if (!response.ok) throw new Error('检查登录失败');
            return response.json();
        })
        .then(data => {
            if (!data.logged_in) {
                window.location.href = '/admin/login';
            } else {
                // 登录成功，初始化页面
                initAdminPage();
                
                // 如果是个人资料页面，填充用户数据
                if (window.location.pathname.includes('profile') && data.user) {
                    populateProfileData(data.user);
                }
            }
        })
        .catch(error => {
            console.error('检查登录失败:', error);
            alert('服务器连接失败，请刷新页面重试');
        });
}

// 初始化管理页面
function initAdminPage() {
    // 登出功能
    document.getElementById('logoutBtn')?.addEventListener('click', function() {
        if (confirm('确定要退出登录吗？')) {
            fetch(`${API_BASE_URL}/logout`, { 
                method: 'POST', 
                credentials: 'include' 
            })
            .then(response => response.json())
            .then(data => {
                window.location.href = '/admin/login';
            })
            .catch(error => {
                console.error('登出失败:', error);
                alert('登出失败，请刷新页面重试');
            });
        }
    });

    // 根据不同页面初始化功能
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
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const message = document.getElementById('message');
        const submitBtn = form.querySelector('button[type="submit"]');

        // 简单验证
        if (!username || !password) {
            message.textContent = '请输入用户名和密码';
            message.className = 'form-message error';
            return;
        }

        // 禁用按钮并显示加载状态
        submitBtn.disabled = true;
        submitBtn.textContent = '登录中...';
        message.textContent = '';

        fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
            credentials: 'include'
        })
        .then(response => {
            submitBtn.disabled = false;
            submitBtn.textContent = '登录';
            
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.message || '登录失败');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                message.textContent = '登录成功，正在跳转...';
                message.className = 'form-message success';
                setTimeout(() => {
                    window.location.href = '/admin/dashboard';
                }, 1000);
            }
        })
        .catch(error => {
            console.error('登录失败:', error);
            message.textContent = error.message || '服务器连接失败';
            message.className = 'form-message error';
        });
    });
}

// 初始化仪表盘
function initDashboard() {
    // 加载仪表盘数据
    fetch(`${API_BASE_URL}/dashboard`, { credentials: 'include' })
        .then(response => {
            if (!response.ok) throw new Error('加载仪表盘数据失败');
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                document.getElementById('totalVisits').textContent = data.dashboard.stats.total_visits;
                document.getElementById('projectCount').textContent = data.dashboard.stats.project_count;
                document.getElementById('lastLogin').textContent = data.dashboard.stats.last_login;
                
                // 加载最近项目
                loadRecentProjects();
            }
        })
        .catch(error => {
            console.error('加载仪表盘数据失败:', error);
            alert('加载数据失败，请刷新页面重试');
        });
}

// 加载最近项目
function loadRecentProjects() {
    const listContainer = document.getElementById('recentProjectsList');
    if (!listContainer) return;

    listContainer.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 20px;">加载中...</td></tr>';

    fetch(`${API_BASE_URL}/projects`, { credentials: 'include' })
        .then(response => {
            if (!response.ok) throw new Error('加载项目失败');
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                // 只显示最近3个项目
                const recentProjects = data.projects.slice(0, 3);
                
                if (recentProjects.length === 0) {
                    listContainer.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 20px;">暂无项目</td></tr>';
                    return;
                }
                
                listContainer.innerHTML = recentProjects.map(project => `
                    <tr>
                        <td>${project.id}</td>
                        <td>${project.title}</td>
                        <td>${project.category}</td>
                        <td>${project.created_at}</td>
                    </tr>
                `).join('');
            }
        })
        .catch(error => {
            console.error('加载最近项目失败:', error);
            listContainer.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 20px; color: var(--danger-color);">加载失败</td></tr>';
        });
}

// 初始化项目管理
function initProjects() {
    // 加载项目列表
    loadProjectsList();
    
    // 初始化添加项目表单
    initAddProjectForm();
    
    // 初始化编辑模态框
    initEditModal();
}

// 加载项目列表
function loadProjectsList() {
    const listContainer = document.getElementById('projectsList');
    if (!listContainer) return;

    listContainer.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px;">加载项目中...</td></tr>';

    fetch(`${API_BASE_URL}/projects`, { credentials: 'include' })
        .then(response => {
            if (!response.ok) throw new Error('加载项目失败');
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                if (data.projects.length === 0) {
                    listContainer.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px;">暂无项目</td></tr>';
                    return;
                }
                
                listContainer.innerHTML = data.projects.map(project => `
                    <tr>
                        <td>${project.id}</td>
                        <td>${project.title}</td>
                        <td>${project.category}</td>
                        <td>${project.description.substring(0, 50)}${project.description.length > 50 ? '...' : ''}</td>
                        <td>
                            <button onclick="prepareEditProject(${project.id})" class="btn">编辑</button>
                            <button onclick="deleteProject(${project.id})" class="btn btn-danger">删除</button>
                        </td>
                    </tr>
                `).join('');
            }
        })
        .catch(error => {
            console.error('加载项目列表失败:', error);
            listContainer.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px; color: var(--danger-color);">加载失败</td></tr>';
        });
}

// 初始化添加项目表单
function initAddProjectForm() {
    const form = document.getElementById('projectForm');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const message = document.getElementById('message');
        const submitBtn = form.querySelector('button[type="submit"]');
        
        // 获取表单数据
        const projectData = {
            title: document.getElementById('title').value,
            description: document.getElementById('description').value,
            category: document.getElementById('category').value,
            image: document.getElementById('image').value,
            link: document.getElementById('link').value
        };
        
        // 简单验证
        if (!projectData.title || !projectData.description) {
            message.textContent = '项目名称和描述不能为空';
            message.className = 'form-message error';
            return;
        }
        
        // 禁用按钮并显示加载状态
        submitBtn.disabled = true;
        submitBtn.textContent = '添加中...';
        message.textContent = '';
        
        fetch(`${API_BASE_URL}/projects`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(projectData),
            credentials: 'include'
        })
        .then(response => {
            submitBtn.disabled = false;
            submitBtn.textContent = '添加项目';
            
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.message || '添加项目失败');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                message.textContent = '项目添加成功';
                message.className = 'form-message success';
                form.reset();
                loadProjectsList(); // 刷新项目列表
                
                // 3秒后清除消息
                setTimeout(() => {
                    message.textContent = '';
                }, 3000);
            }
        })
        .catch(error => {
            console.error('添加项目失败:', error);
            message.textContent = error.message || '服务器连接失败';
            message.className = 'form-message error';
        });
    });
}

// 初始化编辑模态框
function initEditModal() {
    const modal = document.getElementById('editModal');
    const closeBtn = document.querySelector('.close-btn');
    const editForm = document.getElementById('editProjectForm');
    
    if (!modal || !closeBtn || !editForm) return;
    
    // 关闭模态框
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    // 点击模态框外部关闭
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // 编辑表单提交
    editForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const projectId = document.getElementById('editProjectId').value;
        const submitBtn = editForm.querySelector('button[type="submit"]');
        
        // 获取表单数据
        const projectData = {
            title: document.getElementById('editTitle').value,
            description: document.getElementById('editDescription').value,
            category: document.getElementById('editCategory').value,
            image: document.getElementById('editImage').value,
            link: document.getElementById('editLink').value
        };
        
        // 简单验证
        if (!projectData.title || !projectData.description) {
            alert('项目名称和描述不能为空');
            return;
        }
        
        // 禁用按钮并显示加载状态
        submitBtn.disabled = true;
        submitBtn.textContent = '保存中...';
        
        fetch(`${API_BASE_URL}/projects/${projectId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(projectData),
            credentials: 'include'
        })
        .then(response => {
            submitBtn.disabled = false;
            submitBtn.textContent = '保存修改';
            
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.message || '更新项目失败');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                modal.style.display = 'none';
                loadProjectsList(); // 刷新项目列表
                
                // 显示成功消息
                const message = document.getElementById('message');
                message.textContent = '项目更新成功';
                message.className = 'form-message success';
                
                // 3秒后清除消息
                setTimeout(() => {
                    message.textContent = '';
                }, 3000);
            }
        })
        .catch(error => {
            console.error('更新项目失败:', error);
            alert(error.message || '服务器连接失败');
        });
    });
}

// 准备编辑项目
function prepareEditProject(projectId) {
    // 加载项目详情
    fetch(`${API_BASE_URL}/projects/${projectId}`, { credentials: 'include' })
        .then(response => {
            if (!response.ok) throw new Error('加载项目详情失败');
            return response.json();
        })
        .then(data => {
            if (data.status === 'success' && data.project) {
                const project = data.project;
                
                // 填充表单数据
                document.getElementById('editProjectId').value = project.id;
                document.getElementById('editTitle').value = project.title;
                document.getElementById('editDescription').value = project.description;
                document.getElementById('editCategory').value = project.category;
                document.getElementById('editImage').value = project.image;
                document.getElementById('editLink').value = project.link;
                
                // 显示模态框
                document.getElementById('editModal').style.display = 'block';
            }
        })
        .catch(error => {
            console.error('加载项目详情失败:', error);
            alert('加载项目详情失败，请重试');
        });
}

// 删除项目
function deleteProject(projectId) {
    if (confirm('确定要删除这个项目吗？此操作不可撤销！')) {
        fetch(`${API_BASE_URL}/projects/${projectId}`, {
            method: 'DELETE',
            credentials: 'include'
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.message || '删除项目失败');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                loadProjectsList(); // 刷新项目列表
                
                // 显示成功消息
                const message = document.getElementById('message');
                message.textContent = '项目已成功删除';
                message.className = 'form-message success';
                
                // 3秒后清除消息
                setTimeout(() => {
                    message.textContent = '';
                }, 3000);
            }
        })
        .catch(error => {
            console.error('删除项目失败:', error);
            alert(error.message || '服务器连接失败');
        });
    }
}

// 填充个人资料数据
function populateProfileData(user) {
    document.getElementById('username').value = user.username || '';
    document.getElementById('email').value = user.email || '';
    document.getElementById('bio').value = user.bio || '';
}

// 初始化个人资料页面
function initProfile() {
    const form = document.getElementById('profileForm');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const message = document.getElementById('message');
        const submitBtn = form.querySelector('button[type="submit"]');
        
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        // 密码验证
        if (password && password !== confirmPassword) {
            message.textContent = '两次输入的密码不一致';
            message.className = 'form-message error';
            return;
        }
        
        // 获取表单数据
        const profileData = {
            email: document.getElementById('email').value,
            bio: document.getElementById('bio').value
        };
        
        // 只有输入了密码才添加到数据中
        if (password) {
            profileData.password = password;
        }
        
        // 禁用按钮并显示加载状态
        submitBtn.disabled = true;
        submitBtn.textContent = '保存中...';
        message.textContent = '';
        
        fetch(`${API_BASE_URL}/profile`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(profileData),
            credentials: 'include'
        })
        .then(response => {
            submitBtn.disabled = false;
            submitBtn.textContent = '保存资料';
            
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.message || '更新资料失败');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                message.textContent = '个人资料更新成功';
                message.className = 'form-message success';
                
                // 清除密码字段
                document.getElementById('password').value = '';
                document.getElementById('confirmPassword').value = '';
                
                // 3秒后清除消息
                setTimeout(() => {
                    message.textContent = '';
                }, 3000);
            }
        })
        .catch(error => {
            console.error('更新个人资料失败:', error);
            message.textContent = error.message || '服务器连接失败';
            message.className = 'form-message error';
        });
    });
}

// 初始化设置页面
function initSettings() {
    const form = document.getElementById('settingsForm');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const message = document.getElementById('message');
        const submitBtn = form.querySelector('button[type="submit"]');
        
        // 获取表单数据
        const settingsData = {
            siteName: document.getElementById('siteName').value,
            siteDescription: document.getElementById('siteDescription').value,
            siteFooter: document.getElementById('siteFooter').value
        };
        
        // 简单验证
        if (!settingsData.siteName) {
            message.textContent = '网站名称不能为空';
            message.className = 'form-message error';
            return;
        }
        
        // 禁用按钮并显示加载状态
        submitBtn.disabled = true;
        submitBtn.textContent = '保存中...';
        message.textContent = '';
        
        // 在实际应用中，这里应该发送请求到后端保存设置
        // 这里使用setTimeout模拟API请求
        setTimeout(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = '保存设置';
            
            message.textContent = '系统设置保存成功';
            message.className = 'form-message success';
            
            // 3秒后清除消息
            setTimeout(() => {
                message.textContent = '';
            }, 3000);
        }, 1000);
    });
}
    