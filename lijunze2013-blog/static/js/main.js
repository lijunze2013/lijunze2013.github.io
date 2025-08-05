// API基础地址配置
const API_BASE_URL = 'http://localhost:5000/api';

// DOM元素加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 导航栏滚动效果
    const navbar = document.getElementById('navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // 移动端菜单切换
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileNav = document.getElementById('mobileNav');
    
    if (mobileMenuBtn && mobileNav) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileNav.classList.toggle('active');
            const icon = mobileMenuBtn.querySelector('i');
            if (mobileNav.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
    }

    // 平滑滚动
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
                
                // 关闭移动菜单（如果打开）
                if (mobileNav && mobileNav.classList.contains('active')) {
                    mobileNav.classList.remove('active');
                    const icon = mobileMenuBtn.querySelector('i');
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            }
        });
    });

    // 滚动动画效果 - 元素进入视口时显示动画
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.intro-card, .project-card, .about-section');
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementPosition < windowHeight * 0.85) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    };

    // 初始设置元素样式
    document.querySelectorAll('.intro-card, .project-card, .about-section').forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    });

    // 初始加载和滚动时触发动画
    window.addEventListener('load', animateOnScroll);
    window.addEventListener('scroll', animateOnScroll);

    // 加载项目数据
    loadProjects();
});

// 加载项目数据
function loadProjects() {
    const projectsGrid = document.querySelector('.projects-grid');
    if (!projectsGrid) return;

    // 显示加载状态
    projectsGrid.innerHTML = '<div class="loading">加载项目中...</div>';

    // 模拟API请求获取项目数据
    fetch(`${API_BASE_URL}/projects`)
        .then(response => {
            if (!response.ok) {
                throw new Error('网络响应不正常');
            }
            
            // 模拟项目数据
            const mockProjects = [
                {
                    id: 1,
                    name: '个人博客系统',
                    description: '基于Flask和原生前端技术构建的个人博客系统，支持项目展示和个人信息管理。',
                    image: 'static/images/placeholder.jpg',
                    link: '#'
                },
                {
                    id: 2,
                    name: '任务管理应用',
                    description: '一款简洁高效的任务管理工具，支持任务创建、分类和进度跟踪。',
                    image: 'static/images/placeholder.jpg',
                    link: '#'
                },
                {
                    id: 3,
                    name: '数据可视化平台',
                    description: '基于Python的数据可视化工具，能够生成各种交互式图表和数据报表。',
                    image: 'static/images/placeholder.jpg',
                    link: '#'
                }
            ];
            
            return mockProjects;
        })
        .then(projects => {
            // 清空网格并添加项目卡片
            projectsGrid.innerHTML = '';
            
            projects.forEach(project => {
                const projectCard = document.createElement('div');
                projectCard.className = 'project-card';
                projectCard.innerHTML = `
                    <img src="${project.image}" alt="${project.name}" class="project-image">
                    <h3>${project.name}</h3>
                    <p>${project.description}</p>
                    <a href="${project.link}" class="btn secondary-btn">查看详情</a>
                `;
                projectsGrid.appendChild(projectCard);
            });
        })
        .catch(error => {
            console.error('加载项目失败:', error);
            projectsGrid.innerHTML = '<div class="error">加载项目失败，请稍后重试。</div>';
        });
}
    