/**
 * 公共JavaScript工具库
 * 提供通用的AJAX操作、模态框、删除确认等功能
 */

// 模态框管理
class ModalManager {
    constructor() {
        this.modalId = 'globalModal';
        this.init();
    }

    init() {
        // 如果不存在模态框，则创建
        if (!document.getElementById(this.modalId)) {
            const modalHtml = `
                <div id="${this.modalId}" class="modal-overlay" style="display: none;">
                    <div class="modal-dialog">
                        <div class="modal-header">
                            <h3 class="modal-title" id="modalTitle">确认操作</h3>
                        </div>
                        <div class="modal-body">
                            <p id="modalMessage">确定要执行这个操作吗？</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="modal-btn" id="modalCancel">取消</button>
                            <button type="button" class="modal-btn modal-btn-danger" id="modalConfirm">确认</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }

        this.setupEventListeners();
    }

    setupEventListeners() {
        const modal = document.getElementById(this.modalId);
        const cancelBtn = document.getElementById('modalCancel');
        const confirmBtn = document.getElementById('modalConfirm');

        // 取消按钮
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.hide());
        }

        // 点击外部关闭
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.hide();
            }
        });

        // ESC键关闭
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hide();
            }
        });
    }

    show(title, message, onConfirm) {
        const modal = document.getElementById(this.modalId);
        const titleEl = document.getElementById('modalTitle');
        const messageEl = document.getElementById('modalMessage');
        const confirmBtn = document.getElementById('modalConfirm');

        titleEl.textContent = title;
        messageEl.textContent = message;
        modal.style.display = 'flex';
        modal.classList.add('show');

        // 移除旧的事件监听器
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

        // 添加新的事件监听器
        newConfirmBtn.addEventListener('click', () => {
            if (onConfirm) onConfirm();
            this.hide();
        });
    }

    hide() {
        const modal = document.getElementById(this.modalId);
        modal.classList.remove('show');

        // 等待过渡动画完成后隐藏
        setTimeout(() => {
            if (!modal.classList.contains('show')) {
                modal.style.display = 'none';
            }
        }, 300);
    }
}

// AJAX操作管理
class AjaxManager {
    constructor() {
        this.getCSRFToken();
    }

    getCSRFToken() {
        const csrfInput = document.querySelector('input[name="csrf_token"]');
        this.csrfToken = csrfInput ? csrfInput.value : null;
    }

    // 通用AJAX请求
    request(method, url, data = null) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open(method, url, true);
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

            if (method === 'POST' && this.csrfToken) {
                xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            }

            xhr.onload = () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const response = xhr.responseText ? JSON.parse(xhr.responseText) : { success: true };
                        resolve(response);
                    } catch (e) {
                        // 检查是否是重定向到登录页面（未登录用户）
                        if (xhr.responseText.includes('login') || xhr.responseText.includes('Redirecting')) {
                            reject(new Error('需要登录才能执行此操作'));
                        } else {
                            resolve({ success: true, text: xhr.responseText });
                        }
                    }
                } else if (xhr.status === 302) {
                    // 处理重定向（通常是未登录导致的）
                    reject(new Error('需要登录才能执行此操作'));
                } else {
                    reject(new Error(`HTTP ${xhr.status}: ${xhr.statusText}`));
                }
            };

            xhr.onerror = () => reject(new Error('网络错误'));

            if (method === 'POST' && data) {
                const formData = new FormData();
                if (this.csrfToken) {
                    formData.append('csrf_token', this.csrfToken);
                }
                for (const [key, value] of Object.entries(data)) {
                    formData.append(key, value);
                }

                const params = new URLSearchParams();
                for (const [key, value] of formData) {
                    params.append(key, value);
                }
                xhr.send(params.toString());
            } else {
                xhr.send();
            }
        });
    }

    // GET请求
    get(url) {
        return this.request('GET', url);
    }

    // POST请求
    post(url, data = {}) {
        return this.request('POST', url, data);
    }
}

// 删除操作管理
class DeleteManager {
    constructor(modalManager, ajaxManager) {
        this.modal = modalManager;
        this.ajax = ajaxManager;
    }

    // 通用删除确认
    confirmDelete(itemType, itemId, itemName = '', options = {}) {
        console.log('confirmDelete called:', { itemType, itemId, itemName, options });

        const {
            title = '确认删除',
            message = itemName ? `确定要删除"${itemName}"吗？此操作无法撤销。` : `确定要删除这个${itemType}吗？此操作无法撤销。`,
            url = `/${itemType}/${itemId}/delete`,
            onSuccess = null,
            onError = null,
            containerSelector = null
        } = options;

        console.log('Delete URL:', url);
        console.log('Modal manager available:', typeof this.modal !== 'undefined');
        console.log('AJAX manager available:', typeof this.ajax !== 'undefined');
        console.log('CSRF token available:', this.ajax.csrfToken);

        this.modal.show(title, message, async () => {
            console.log('User confirmed deletion, sending request...');
            console.log('Request URL:', url);
            console.log('CSRF Token:', this.ajax.csrfToken);

            try {
                const response = await this.ajax.post(url);
                console.log('Delete response:', response);

                if (response.success) {
                    // 移除元素
                    if (containerSelector) {
                        this.removeElementWithAnimation(itemId, containerSelector);
                    }

                    // 执行成功回调
                    if (onSuccess) onSuccess(response);

                    // 显示成功消息
                    this.showFlashMessage(response.message || `${itemType}已删除`, 'success');
                } else {
                    throw new Error(response.message || '删除失败');
                }
            } catch (error) {
                console.error('删除失败:', error);
                console.error('Error details:', error.message, error.stack);
                if (onError) onError(error);
                this.showFlashMessage(`删除失败: ${error.message}`, 'error');
            }
        });
    }

    // 带动画的元素移除
    removeElementWithAnimation(itemId, containerSelector) {
        const element = document.querySelector(`[data-item-id="${itemId}"]`);
        if (element) {
            element.style.transition = 'opacity 0.3s, transform 0.3s';
            element.style.opacity = '0';
            element.style.transform = 'scale(0.95)';

            setTimeout(() => {
                element.remove();

                // 检查是否还有元素
                const container = document.querySelector(containerSelector);
                if (container && container.children.length === 0) {
                    this.showEmptyState(container);
                }
            }, 300);
        }
    }

    // 显示空状态
    showEmptyState(container) {
        const emptyMessage = container.dataset.emptyMessage || '暂无数据';
        container.innerHTML = `
            <div class="text-center py-8">
                <p class="text-gray-500">${emptyMessage}</p>
            </div>
        `;
    }

    // 显示Flash消息
    showFlashMessage(message, type = 'info') {
        // 创建Flash消息元素
        const flashDiv = document.createElement('div');
        flashDiv.className = `flash-message flash-${type}`;
        flashDiv.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} mr-2"></i>
                <span>${message}</span>
            </div>
        `;

        // 添加样式
        flashDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            padding: 12px 20px;
            border-radius: 4px;
            color: white;
            font-weight: 500;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;

        // 设置背景色
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };
        flashDiv.style.backgroundColor = colors[type] || colors.info;

        // 添加到页面
        document.body.appendChild(flashDiv);

        // 显示动画
        setTimeout(() => {
            flashDiv.style.transform = 'translateX(0)';
        }, 10);

        // 自动移除
        setTimeout(() => {
            flashDiv.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (flashDiv.parentNode) {
                    flashDiv.parentNode.removeChild(flashDiv);
                }
            }, 300);
        }, 3000);
    }
}

// 初始化全局对象
const modalManager = new ModalManager();
const ajaxManager = new AjaxManager();
const deleteManager = new DeleteManager(modalManager, ajaxManager);

// 导出到全局作用域（兼容旧代码）
window.modalManager = modalManager;
window.ajaxManager = ajaxManager;
window.deleteManager = deleteManager;

// 便捷函数（兼容旧代码）
window.showModal = (message, onConfirm) => {
    modalManager.show('确认操作', message, onConfirm);
};

// 工具函数
window.Utils = {
    // 获取CSRF token
    getCSRFToken: () => ajaxManager.csrfToken,

    // 格式化日期
    formatDate: (date, format = 'YYYY-MM-DD HH:mm:ss') => {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        const seconds = String(d.getSeconds()).padStart(2, '0');

        return format
            .replace('YYYY', year)
            .replace('MM', month)
            .replace('DD', day)
            .replace('HH', hours)
            .replace('mm', minutes)
            .replace('ss', seconds);
    },

    // 防抖函数
    debounce: (func, wait) => {
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
};

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('Common.js loaded and initialized');
    console.log('deleteManager available:', typeof deleteManager !== 'undefined');
    console.log('modalManager available:', typeof modalManager !== 'undefined');
    console.log('ajaxManager available:', typeof ajaxManager !== 'undefined');
});