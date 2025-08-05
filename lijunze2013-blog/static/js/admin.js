// API基础地址配置
const API_BASE_URL = 'http://localhost:5000/api';

// 检查用户是否已登录
async function checkLogin() {
    // 非登录页面才需要检查登录状态
    if (!window.location.pathname.includes('login.html')) {
        try {
            const response = await fetch(`${API_BASE_URL}/check-login`, {
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (!data.logged_in) {
                // 未登录，重定向到登录页
                window.location.href = 'login.html';
            } else {
                // 已登录，初始化页面
                initAdminPage();
            }
        } catch (error) {
            console.error('检查登录状态失败:', error);
            alert('无法连接到服务器，请稍后重试');
        }
    }
}

// 初始化管理员页面
function initAdminPage() {
    // 初始化登出按钮
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
    
    // 根据不同页面初始化不同功能
    if (window.location.pathname.includes('dashboard.html')) {
        initDashboard();
    } else if (window.location.pathname.includes('profile.html')) {
        initProfile();
    } else if (window.location.pathname.includes('projects.html')) {
        initProjects();
    } else if (window.location.pathname.includes('settings.html')) {
        initSettings();
    }
}

// 登录功能
function initLogin() {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const messageElement = document.getElementById('message');
            
            try {
                const response = await fetch(`${API_BASE_URL}/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password }),
                    credentials: 'include'
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    messageElement.textContent = '登录成功，正在跳转...';
                    messageElement.className = 'form-message success';
                    
                    // 登录成功，跳转到管理面板
                    setTimeout(() => {
                        window.location.href = 'dashboard.html';
                    }, 1000);
                } else {
                    messageElement.textContent = data.message || '登录失败';
                    messageElement.className = 'form-message error';
                }
            } catch (error) {
                console.error('登录请求失败:', error);
                messageElement.textContent = '服务器连接失败，请稍后重试';
                messageElement.className = 'form-message error';
            }
        });
    }
}

// 登出功能
async function logout() {
    try {
        const response = await fetch(`${API_BASE_URL}/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // 登出成功，重定向到登录页
            window.location.href = 'login.html';
        }
    } catch (error) {
        console.error('登出请求失败:', error);
        alert('登出失败，请稍后重试');
    }
}

// 初始化控制面板
function initDashboard() {
    // 显示服务器时间
    const serverTimeElement = document.getElementById('serverTime');
    if (serverTimeElement) {
        setInterval(() => {
            const now = new Date();
            serverTimeElement.textContent = now.toLocaleString();
        }, 1000);
    }
    
    // 加载统计数据
    fetchDashboardData();
}

// 获取控制面板数据
async function fetchDashboardData() {
    try {
        const response = await fetch(`${API_BASE_URL}/dashboard`, {
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            const stats = data.dashboard.stats;
            
            // 更新统计数据
            const totalVisitsElement = document.getElementById('totalVisits');
            const lastLoginElement = document.getElementById('lastLogin');
            
            if (totalVisitsElement) {
                totalVisitsElement.textContent = stats.total_visits || '0';
            }
            
            if (lastLoginElement) {
                lastLoginElement.textContent = stats.last_login || '从未登录';
            }
        }
    } catch (error) {
        console.error('获取控制面板数据失败:', error);
    }
}

// 初始化个人资料页面
function initProfile() {
    // 加载个人资料
    loadProfileData();
    
    // 头像上传功能
    const changeImageBtn = document.getElementById('changeImageBtn');
    const imageUpload = document.getElementById('imageUpload');
    const profileImage = document.getElementById('profileImage');
    
    if (changeImageBtn && imageUpload && profileImage) {
        changeImageBtn.addEventListener('click', () => {
            imageUpload.click();
        });
        
        imageUpload.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    profileImage.src = event.target.result;
                    showMessage('profileForm', '头像已更新，点击保存生效', 'success');
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // 个人资料表单提交
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                fullName: document.getElementById('fullName').value,
                bio: document.getElementById('bio').value,
                website: document.getElementById('website').value,
                email: document.getElementById('email').value,
                github: document.getElementById('github').value,
                twitter: document.getElementById('twitter').value,
                linkedin: document.getElementById('linkedin').value
            };
            
            try {
                // 模拟保存个人资料
                await new Promise(resolve => setTimeout(resolve, 800));
                
                showMessage('profileForm', '个人资料保存成功', 'success');
                
                // 2秒后隐藏消息
                setTimeout(() => {
                    hideMessage('profileForm');
                }, 2000);
                
            } catch (error) {
                console.error('保存个人资料失败:', error);
                showMessage('profileForm', '保存失败，请稍后重试', 'error');
            }
        });
    }
    
    // 密码修改表单提交
    const passwordForm = document.getElementById('passwordForm');
    if (passwordForm) {
        passwordForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const currentPassword = document.getElementById('currentPassword').value;
            const newPassword = document.getElementById('newPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            
            // 验证密码
            if (newPassword !== confirmPassword) {
                showMessage('passwordForm', '两次输入的新密码不一致', 'error');
                return;
            }
            
            if (newPassword.length < 6) {
                showMessage('passwordForm', '密码长度不能少于6位', 'error');
                return;
            }
            
            try {
                // 模拟更新密码
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                // 假设旧密码验证成功
                showMessage('passwordForm', '密码更新成功', 'success');
                
                // 重置表单
                passwordForm.reset();
                
                // 2秒后隐藏消息
                setTimeout(() => {
                    hideMessage('passwordForm');
                }, 2000);
                
            } catch (error) {
                console.error('更新密码失败:', error);
                showMessage('passwordForm', '更新失败，请稍后重试', 'error');
            }
        });
    }
    
    // 取消按钮
    const cancelBtn = document.getElementById('cancelBtn');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            loadProfileData(); // 重新加载数据
            hideMessage('profileForm');
        });
    }
}

// 加载个人资料数据
function loadProfileData() {
    // 模拟从服务器加载数据
    const mockProfile = {
        fullName: 'lijunze2013',
        bio: '热爱技术的开发者，专注于Web开发和数据科学领域。',
        website: 'https://lijunze2013.example.com',
        email: 'lijunze2013@example.com',
        github: 'https://github.com/lijunze2013',
        twitter: 'https://twitter.com/lijunze2013',
        linkedin: 'https://linkedin.com/in/lijunze2013'
    };
    
    // 填充表单
    document.getElementById('fullName').value = mockProfile.fullName || '';
    document.getElementById('bio').value = mockProfile.bio || '';
    document.getElementById('website').value = mockProfile.website || '';
    document.getElementById('email').value = mockProfile.email || '';
    document.getElementById('github').value = mockProfile.github || '';
    document.getElementById('twitter').value = mockProfile.twitter || '';
    document.getElementById('linkedin').value = mockProfile.linkedin || '';
}

// 初始化项目管理页面
function initProjects() {
    // 加载项目列表
    loadProjects();
    
    // 添加项目按钮
    const addProjectBtn = document.getElementById('addProjectBtn');
    if (addProjectBtn) {
        addProjectBtn.addEventListener('click', () => {
            openProjectModal();
        });
    }
    
    // 关闭模态框
    document.querySelectorAll('.close-modal').forEach(button => {
        button.addEventListener('click', () => {
            closeProjectModal();
        });
    });
    
    // 项目图片预览
    const projectImage = document.getElementById('projectImage');
    const imagePreview = document.getElementById('imagePreview');
    
    if (projectImage && imagePreview) {
        projectImage.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    imagePreview.src = event.target.result;
                    imagePreview.classList.add('active');
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // 项目表单提交
    const projectForm = document.getElementById('projectForm');
    if (projectForm) {
        projectForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const projectId = document.getElementById('projectId').value;
            const projectName = document.getElementById('projectName').value;
            const projectDescription = document.getElementById('projectDescription').value;
            const projectLink = document.getElementById('projectLink').value;
            
            // 简单验证
            if (!projectName || !projectDescription) {
                showMessage('projectForm', '项目名称和描述不能为空', 'error');
                return;
            }
            
            try {
                // 模拟保存项目
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                showMessage('projectForm', projectId ? '项目更新成功' : '项目添加成功', 'success');
                
                // 关闭模态框并重新加载项目列表
                setTimeout(() => {
                    closeProjectModal();
                    loadProjects();
                }, 1000);
                
            } catch (error) {
                console.error('保存项目失败:', error);
                showMessage('projectForm', '保存失败，请稍后重试', 'error');
            }
        });
    }
}

// 加载项目列表
function loadProjects() {
    const tableBody = document.getElementById('projectsTableBody');
    if (!tableBody) return;
    
    // 显示加载状态
    tableBody.innerHTML = '<tr><td colspan="4">加载项目中...</td></tr>';
    
    // 模拟从服务器加载项目数据
    const mockProjects = [
        {
            id: 1,
            name: '个人博客系统',
            image: 'static/images/placeholder.jpg'
        },
        {
            id: 2,
            name: '任务管理应用',
            image: 'static/images/placeholder.jpg'
        },
        {
            id: 3,
            name: '数据可视化平台',
            image: 'static/images/placeholder.jpg'
        }
    ];
    
    // 填充表格
    setTimeout(() => {
        if (mockProjects.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="4">暂无项目数据</td></tr>';
            return;
        }
        
        tableBody.innerHTML = '';
        
        mockProjects.forEach(project => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${project.id}</td>
                <td>${project.name}</td>
                <td><img src="${project.image}" alt="${project.name}" class="project-image-thumbnail"></td>
                <td class="table-actions">
                    <button class="action-btn edit-btn" onclick="editProject(${project.id})">
                        <i class="fas fa-edit"></i> 编辑
                    </button>
                    <button class="action-btn delete-btn" onclick="deleteProject(${project.id})">
                        <i class="fas fa-trash"></i> 删除
                    </button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    }, 800);
}

// 打开项目模态框
function openProjectModal(projectId = null) {
    const modal = document.getElementById('projectModal');
    const modalTitle = document.getElementById('modalTitle');
    const projectIdInput = document.getElementById('projectId');
    const projectForm = document.getElementById('projectForm');
    const imagePreview = document.getElementById('imagePreview');
    
    if (modal && modalTitle && projectIdInput && projectForm) {
        // 重置表单
        projectForm.reset();
        hideMessage('projectForm');
        imagePreview.src = '';
        imagePreview.classList.remove('active');
        
        if (projectId) {
            // 编辑现有项目
            modalTitle.textContent = '编辑项目';
            projectIdInput.value = projectId;
            
            // 模拟加载项目数据
            const mockProject = {
                id: projectId,
                name: `项目 ${projectId}`,
                description: `这是项目 ${projectId} 的描述信息。`,
                link: '#'
            };
            
            document.getElementById('projectName').value = mockProject.name;
            document.getElementById('projectDescription').value = mockProject.description;
            document.getElementById('projectLink').value = mockProject.link;
            
        } else {
            // 添加新项目
            modalTitle.textContent = '添加新项目';
            projectIdInput.value = '';
        }
        
        // 显示模态框
        modal.classList.add('active');
    }
}

// 关闭项目模态框
function closeProjectModal() {
    const modal = document.getElementById('projectModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// 编辑项目
function editProject(projectId) {
    openProjectModal(projectId);
}

// 删除项目
function deleteProject(projectId) {
    if (confirm('确定要删除这个项目吗？此操作不可撤销。')) {
        // 模拟删除项目
        setTimeout(() => {
            loadProjects();
        }, 800);
    }
}

// 初始化设置页面
function initSettings() {
    // 加载设置数据
    loadSettings();
    
    // 基本设置表单提交
    const basicSettingsForm = document.getElementById('basicSettingsForm');
    if (basicSettingsForm) {
        basicSettingsForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            try {
                // 模拟保存设置
                await new Promise(resolve => setTimeout(resolve, 800));
                
                showMessage('basicSettingsForm', '基本设置保存成功', 'success');
                
                // 2秒后隐藏消息
                setTimeout(() => {
                    hideMessage('basicSettingsForm');
                }, 2000);
                
            } catch (error) {
                console.error('保存基本设置失败:', error);
                showMessage('basicSettingsForm', '保存失败，请稍后重试', 'error');
            }
        });
    }
    
    // 外观设置表单提交
    const appearanceSettingsForm = document.getElementById('appearanceSettingsForm');
    if (appearanceSettingsForm) {
        appearanceSettingsForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            try {
                // 模拟保存设置
                await new Promise(resolve => setTimeout(resolve, 800));
                
                showMessage('appearanceSettingsForm', '外观设置保存成功', 'success');
                
                // 2秒后隐藏消息
                setTimeout(() => {
                    hideMessage('appearanceSettingsForm');
                }, 2000);
                
            } catch (error) {
                console.error('保存外观设置失败:', error);
                showMessage('appearanceSettingsForm', '保存失败，请稍后重试', 'error');
            }
        });
    }
    
    // 高级设置表单提交
    const advancedSettingsForm = document.getElementById('advancedSettingsForm');
    if (advancedSettingsForm) {
        advancedSettingsForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            try {
                // 模拟保存设置
                await new Promise(resolve => setTimeout(resolve, 800));
                
                alert('高级设置保存成功，部分设置可能需要刷新页面才能生效');
                
            } catch (error) {
                console.error('保存高级设置失败:', error);
                alert('保存失败，请稍后重试');
            }
        });
    }
    
    // 恢复默认设置
    const resetSettingsBtn = document.getElementById('resetSettingsBtn');
    if (resetSettingsBtn) {
        resetSettingsBtn.addEventListener('click', function() {
            if (confirm('确定要恢复默认设置吗？所有自定义设置将被清除。')) {
                // 模拟恢复默认设置
                setTimeout(() => {
                    loadSettings();
                    alert('已恢复默认设置');
                }, 800);
            }
        });
    }
}

// 加载设置数据
function loadSettings() {
    // 模拟从服务器加载设置
    const mockSettings = {
        siteTitle: 'lijunze2013的博客',
        siteDescription: '个人展示和分享的空间',
        copyrightText: '© 2023 个人博客空间. 保留所有权利.',
        themeColor: 'blue',
        darkMode: false,
        showSocialLinks: true,
        apiUrl: 'http://localhost:5000/api',
        enableAnalytics: false
    };
    
    // 填充基本设置
    document.getElementById('siteTitle').value = mockSettings.siteTitle || '';
    document.getElementById('siteDescription').value = mockSettings.siteDescription || '';
    document.getElementById('copyrightText').value = mockSettings.copyrightText || '';
    
    // 填充外观设置
    document.querySelectorAll('input[name="themeColor"]').forEach(radio => {
        if (radio.value === mockSettings.themeColor) {
            radio.checked = true;
        }
    });
    
    document.getElementById('darkMode').checked = mockSettings.darkMode;
    document.getElementById('showSocialLinks').checked = mockSettings.showSocialLinks;
    
    // 填充高级设置
    document.getElementById('apiUrl').value = mockSettings.apiUrl || '';
    document.getElementById('enableAnalytics').checked = mockSettings.enableAnalytics;
    
    // 隐藏所有消息
    hideMessage('basicSettingsForm');
    hideMessage('appearanceSettingsForm');
}

// 显示消息
function showMessage(formId, message, type) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const messageElement = form.querySelector('.form-message');
    if (messageElement) {
        messageElement.textContent = message;
        messageElement.className = `form-message ${type}`;
    }
}

// 隐藏消息
function hideMessage(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const messageElement = form.querySelector('.form-message');
    if (messageElement) {
        messageElement.textContent = '';
        messageElement.className = 'form-message';
    }
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    // 检查登录状态
    checkLogin();
    
    // 如果是登录页面，初始化登录功能
    if (window.location.pathname.includes('login.html')) {
        initLogin();
    }
});
    