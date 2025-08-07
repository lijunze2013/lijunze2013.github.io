// API基础URL，根据环境自动切换
const API_BASE_URL = window.location.hostname.includes('github.io') 
    ? 'https://your-vercel-api-url.vercel.app/api'  // 替换为你的Vercel API地址
    : '/api';

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

    // 加载项目数据
    loadProjects();
    
    // 初始化联系表单
    initContactForm();
});

// 加载项目数据
function loadProjects() {
    const projectsGrid = document.querySelector('.projects-grid');
    if (!projectsGrid) return;

    projectsGrid.innerHTML = '<div class="loading">加载项目中...</div>';

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
                    card.setAttribute('data-category', project.category);
                    card.innerHTML = `
                        <img src="${project.image}" alt="${project.title}" class="project-image">
                        <span class="category">${project.category}</span>
                        <h3>${project.title}</h3>
                        <p>${project.description}</p>
                        <a href="${project.link}" class="btn btn-secondary">查看详情</a>
                    `;
                    projectsGrid.appendChild(card);
                });
                
                // 初始化项目筛选功能
                initProjectFilters();
            }
        })
        .catch(error => {
            console.error('加载项目失败:', error);
            projectsGrid.innerHTML = '<div style="text-align: center; padding: 50px; color: var(--danger-color);">加载失败，请稍后重试</div>';
        });
}

// 初始化项目筛选
function initProjectFilters() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // 更新按钮状态
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const filter = btn.getAttribute('data-filter');
            const projectCards = document.querySelectorAll('.project-card');
            
            projectCards.forEach(card => {
                if (filter === 'all' || card.getAttribute('data-category') === filter) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
}

// 初始化联系表单
function initContactForm() {
    const form = document.getElementById('contactForm');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 在实际应用中，这里应该添加表单提交逻辑
        const formData = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            message: document.getElementById('message').value
        };
        
        // 模拟表单提交
        console.log('表单提交数据:', formData);
        
        // 显示成功消息
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        
        submitBtn.disabled = true;
        submitBtn.textContent = '发送中...';
        
        setTimeout(() => {
            alert('消息发送成功！感谢您的留言。');
            form.reset();
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }, 1000);
    });
}
    