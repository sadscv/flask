/**
 * 页面视觉增强效果
 */

document.addEventListener('DOMContentLoaded', function() {
    // 初始化基础增强功能
    initArticleEnhancements();
});

// 滚动动画
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');

                // 添加渐入延迟效果
                const delay = entry.target.dataset.delay || 0;
                entry.target.style.transitionDelay = `${delay}ms`;
            }
        });
    }, observerOptions);

    // 观察所有带有滚动动画的元素
    document.querySelectorAll('.scroll-animate').forEach(el => {
        observer.observe(el);
    });

    // 为文章卡片添加滚动动画
    document.querySelectorAll('.card-list .card').forEach((card, index) => {
        card.classList.add('scroll-animate');
        card.dataset.delay = index * 100;
        observer.observe(card);
    });
}

// 文章增强功能
function initArticleEnhancements() {
    // 为标题添加锚点链接
    document.querySelectorAll('.article-content h1, .article-content h2, .article-content h3, .article-content h4, .article-content h5, .article-content h6').forEach(header => {
        if (!header.querySelector('.anchor-link')) {
            const id = header.textContent.trim().toLowerCase().replace(/\s+/g, '-');
            header.id = id;

            const anchor = document.createElement('a');
            anchor.href = `#${id}`;
            anchor.className = 'anchor-link';
            anchor.innerHTML = '<i class="fas fa-link"></i>';
            anchor.title = '永久链接';

            header.appendChild(anchor);
        }
    });

    // 代码块复制功能
    document.querySelectorAll('pre code, .codehilite').forEach(block => {
        const wrapper = document.createElement('div');
        wrapper.style.position = 'relative';
        wrapper.className = 'code-wrapper';

        block.parentNode.insertBefore(wrapper, block);
        wrapper.appendChild(block);

        const copyBtn = document.createElement('button');
        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
        copyBtn.className = 'code-copy-btn';
        copyBtn.title = '复制代码';

        copyBtn.style.cssText = `
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            background: #374151;
            color: white;
            border: none;
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            cursor: pointer;
            font-size: 0.75rem;
            opacity: 0;
            transition: opacity 0.2s ease;
        `;

        wrapper.appendChild(copyBtn);

        wrapper.addEventListener('mouseenter', () => {
            copyBtn.style.opacity = '1';
        });

        wrapper.addEventListener('mouseleave', () => {
            copyBtn.style.opacity = '0';
        });

        copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(block.textContent).then(() => {
                copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => {
                    copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                }, 2000);
            });
        });
    });

    // 图片懒加载
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            }
        });
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
}

// 页面加载器
function initPageLoader() {
    const loader = document.createElement('div');
    loader.className = 'page-loader';
    loader.innerHTML = '<div class="loader-spinner"></div>';
    document.body.appendChild(loader);

    window.addEventListener('load', () => {
        setTimeout(() => {
            loader.classList.add('hidden');
            setTimeout(() => {
                loader.remove();
            }, 300);
        }, 500);
    });
}

// 回到顶部功能
function initBackToTop() {
    const backToTopBtn = document.createElement('button');
    backToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTopBtn.className = 'back-to-top';
    backToTopBtn.title = '回到顶部';

    backToTopBtn.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        width: 3rem;
        height: 3rem;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        color: white;
        border: none;
        border-radius: 50%;
        cursor: pointer;
        opacity: 0;
        transform: translateY(100px);
        transition: all 0.3s ease;
        z-index: 1000;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    `;

    document.body.appendChild(backToTopBtn);

    // 显示/隐藏按钮
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            backToTopBtn.style.opacity = '1';
            backToTopBtn.style.transform = 'translateY(0)';
        } else {
            backToTopBtn.style.opacity = '0';
            backToTopBtn.style.transform = 'translateY(100px)';
        }
    });

    // 点击回到顶部
    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// 阅读进度条
function initReadingProgress() {
    const progressBar = document.createElement('div');
    progressBar.className = 'reading-progress';
    document.body.appendChild(progressBar);

    window.addEventListener('scroll', () => {
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight - windowHeight;
        const scrolled = (window.scrollY / documentHeight) * 100;
        progressBar.style.width = `${scrolled}%`;
    });
}

// 卡片悬停效果增强 - 已禁用
// document.addEventListener('DOMContentLoaded', function() {
//     document.querySelectorAll('.card').forEach(card => {
//         card.addEventListener('mouseenter', function() {
//             this.style.transform = 'translateY(-8px) scale(1.02)';
//         });
//
//         card.addEventListener('mouseleave', function() {
//             this.style.transform = 'translateY(0) scale(1)';
//         });
//     });
// });

// 平滑的页面切换效果
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a[href^="/"]').forEach(link => {
        if (!link.href.includes('#') && !link.target) {
            link.addEventListener('click', function(e) {
                if (!e.ctrlKey && !e.metaKey) {
                    e.preventDefault();

                    document.body.style.opacity = '0.7';
                    document.body.style.transition = 'opacity 0.3s ease';

                    setTimeout(() => {
                        window.location.href = this.href;
                    }, 300);
                }
            });
        }
    });
});

// 添加键盘快捷键
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K 聚焦搜索框
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"], input[placeholder*="搜索"]');
        if (searchInput) {
            searchInput.focus();
        }
    }

    // ESC 关闭模态框
    if (e.key === 'Escape') {
        const modal = document.querySelector('.modal.show');
        if (modal) {
            modal.classList.remove('show');
        }
    }
});

// 性能优化：防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 性能优化：节流函数
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// 优化滚动事件
const optimizedScroll = throttle(() => {
    // 滚动相关的优化处理
}, 100);

window.addEventListener('scroll', optimizedScroll);