/**
 * 心情可视化组件
 * 支持多次打卡的渐进式展示策略
 */

class MoodVisualization {
    constructor() {
        this.MOOD_CONFIG = {
            'happy': { color: '#FCD34D', icon: '😊', label: '开心' },
            'calm': { color: '#93C5FD', icon: '😌', label: '平静' },
            'anxious': { color: '#C4B5FD', icon: '😰', label: '焦虑' },
            'sad': { color: '#9CA3AF', icon: '😢', label: '伤心' },
            'angry': { color: '#F87171', icon: '😠', label: '愤怒' },
            'custom': { color: '#86EFAC', icon: '💭', label: '自定义' }
        };
    }

    /**
     * 根据记录数量选择展示策略
     * @param {Object} dayData - 天数据 {moods, primary_mood, count, avg_intensity}
     * @param {HTMLElement} container - 容器元素
     * @param {number} size - 圆环大小
     */
    renderMoodDay(dayData, container, size = 60) {
        if (!dayData || !dayData.moods || dayData.moods.length === 0) {
            this.renderEmptyDay(container);
            return;
        }

        const count = dayData.count;
        const moods = dayData.moods;
        const primaryMood = dayData.primary_mood;

        // 清空容器
        container.innerHTML = '';

        if (count === 1) {
            this.renderSingleMood(moods[0], container, size);
        } else if (count <= 2) {
            this.renderMultipleMoods(moods, container, size);
        } else if (count <= 4) {
            this.renderDonutChart(dayData, container, size);
        } else {
            this.renderAggregatedMood(dayData, container, size);
        }
    }

    /**
     * 渲染空白天
     */
    renderEmptyDay(container) {
        container.className = 'aspect-square border-2 border-gray-200 rounded-lg bg-gray-50 flex items-center justify-center';
        container.innerHTML = `<span class="text-gray-400 text-xs">--</span>`;
    }

    /**
     * 渲染单个心情
     */
    renderSingleMood(mood, container, size) {
        const config = this.MOOD_CONFIG[mood.mood_type] || this.MOOD_CONFIG['custom'];
        container.className = `aspect-square border-2 border-${mood.mood_type}-300 rounded-lg cursor-pointer transition-all duration-200 hover:scale-105`;
        container.style.backgroundColor = config.color + '30';
        const dateObj = new Date(mood.date);
        container.innerHTML = `
            <div class="h-full flex flex-col items-center justify-center p-1">
                <div class="text-2xl mb-1">${config.icon}</div>
                <div class="text-xs text-center">${dateObj.getDate()}</div>
            </div>
        `;
        this.addInteractivity(container, [mood]);
    }

    /**
     * 渲染多个心情（1-2个）
     */
    renderMultipleMoods(moods, container, size) {
        container.className = 'aspect-square border-2 border-gray-300 rounded-lg cursor-pointer transition-all duration-200 hover:scale-105';
        container.style.backgroundColor = '#F9FAFB';

        const iconsHtml = moods.map(mood => {
            const config = this.MOOD_CONFIG[mood.mood_type] || this.MOOD_CONFIG['custom'];
            return `<span class="text-lg">${config.icon}</span>`;
        }).join('');

        const dateObj = new Date(moods[0].date);
        container.innerHTML = `
            <div class="h-full flex flex-col items-center justify-center p-1">
                <div class="flex space-x-1 mb-1">${iconsHtml}</div>
                <div class="text-xs text-center font-medium">${dateObj.getDate()}</div>
                <div class="text-xs text-gray-500">${moods.length}次</div>
            </div>
        `;
        this.addInteractivity(container, moods);
    }

    /**
     * 渲染圆环图（3-4个心情）
     */
    renderDonutChart(dayData, container, size) {
        const { moods, primary_mood } = dayData;
        container.className = 'aspect-square border-2 border-purple-300 rounded-lg cursor-pointer transition-all duration-200 hover:scale-105';
        container.style.backgroundColor = '#F3E8FF';

        // 创建圆环图
        const donutSvg = this.createDonutChart(moods, size * 0.8);
        const primaryConfig = this.MOOD_CONFIG[primary_mood.mood_type] || this.MOOD_CONFIG['custom'];

        const dateObj = new Date(moods[0].date);
        container.innerHTML = `
            <div class="h-full flex flex-col items-center justify-center p-1 relative">
                <div class="absolute inset-0 flex items-center justify-center">${donutSvg}</div>
                <div class="relative z-10 text-center">
                    <div class="text-lg">${primaryConfig.icon}</div>
                    <div class="text-xs font-medium">${dateObj.getDate()}</div>
                </div>
                <div class="absolute top-0 right-0 bg-purple-600 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
                    ${moods.length}
                </div>
            </div>
        `;
        this.addInteractivity(container, moods);
    }

    /**
     * 渲染聚合心情（5次以上）
     */
    renderAggregatedMood(dayData, container, size) {
        const { primary_mood, count, avg_intensity } = dayData;
        const primaryConfig = this.MOOD_CONFIG[primary_mood.mood_type] || this.MOOD_CONFIG['custom'];

        container.className = 'aspect-square border-2 border-indigo-300 rounded-lg cursor-pointer transition-all duration-200 hover:scale-105';

        // 根据平均强度设置背景渐变
        const intensity = avg_intensity / 10; // 归一化到0-1
        const gradient = this.createIntensityGradient(primary_mood.mood_type, intensity);
        container.style.background = gradient;

        const dateObj = new Date(primary_mood.date);
        container.innerHTML = `
            <div class="h-full flex flex-col items-center justify-center p-1 relative">
                <div class="text-center">
                    <div class="text-2xl mb-1">${primaryConfig.icon}</div>
                    <div class="text-xs font-medium">${dateObj.getDate()}</div>
                    <div class="text-xs text-gray-600">${count}次记录</div>
                </div>
                <div class="absolute top-0 right-0 bg-indigo-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                    ${count}
                </div>
                <div class="absolute bottom-0 right-0 bg-black bg-opacity-20 text-white text-xs px-1 rounded">
                    强度${Math.round(avg_intensity)}
                </div>
            </div>
        `;
        this.addInteractivity(container, dayData.moods);
    }

    /**
     * 创建圆环图SVG
     */
    createDonutChart(moods, size) {
        const stats = this.calculateMoodStats(moods);
        const segments = Object.entries(stats);

        let currentAngle = -90; // 从顶部开始
        const paths = [];

        segments.forEach(([moodType, percentage]) => {
            const config = this.MOOD_CONFIG[moodType] || this.MOOD_CONFIG['custom'];
            const angle = (percentage / 100) * 360;

            const path = this.createDonutSegment(
                size / 2, size / 2, size * 0.3, size * 0.4,
                currentAngle, currentAngle + angle,
                config.color
            );

            paths.push(path);
            currentAngle += angle;
        });

        return `
            <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
                ${paths.join('')}
            </svg>
        `;
    }

    /**
     * 创建圆环段
     */
    createDonutSegment(cx, cy, innerRadius, outerRadius, startAngle, endAngle, color) {
        const startAngleRad = (startAngle * Math.PI) / 180;
        const endAngleRad = (endAngle * Math.PI) / 180;

        const x1 = cx + innerRadius * Math.cos(startAngleRad);
        const y1 = cy + innerRadius * Math.sin(startAngleRad);
        const x2 = cx + outerRadius * Math.cos(startAngleRad);
        const y2 = cy + outerRadius * Math.sin(startAngleRad);
        const x3 = cx + outerRadius * Math.cos(endAngleRad);
        const y3 = cy + outerRadius * Math.sin(endAngleRad);
        const x4 = cx + innerRadius * Math.cos(endAngleRad);
        const y4 = cy + innerRadius * Math.sin(endAngleRad);

        const largeArc = endAngle - startAngle > 180 ? 1 : 0;

        const pathData = [
            `M ${x1} ${y1}`,
            `L ${x2} ${y2}`,
            `A ${outerRadius} ${outerRadius} 0 ${largeArc} 1 ${x3} ${y3}`,
            `L ${x4} ${y4}`,
            `A ${innerRadius} ${innerRadius} 0 ${largeArc} 0 ${x1} ${y1}`,
            'Z'
        ].join(' ');

        return `<path d="${pathData}" fill="${color}" stroke="white" stroke-width="1" opacity="0.8"/>`;
    }

    /**
     * 计算心情统计
     */
    calculateMoodStats(moods) {
        const stats = {};
        const total = moods.length;

        moods.forEach(mood => {
            if (!stats[mood.mood_type]) {
                stats[mood.mood_type] = 0;
            }
            stats[mood.mood_type]++;
        });

        // 转换为百分比
        Object.keys(stats).forEach(moodType => {
            stats[moodType] = Math.round((stats[moodType] / total) * 100);
        });

        return stats;
    }

    /**
     * 创建强度渐变背景
     */
    createIntensityGradient(moodType, intensity) {
        const config = this.MOOD_CONFIG[moodType] || this.MOOD_CONFIG['custom'];
        const baseColor = config.color;

        // 将hex颜色转换为rgb
        const rgb = this.hexToRgb(baseColor);

        // 根据强度调整透明度
        const opacity = 0.2 + (intensity * 0.6); // 0.2 到 0.8

        return `linear-gradient(135deg, ${baseColor}${Math.round(opacity * 255).toString(16)}, ${baseColor}${Math.round(opacity * 0.5 * 255).toString(16)})`;
    }

    /**
     * HEX颜色转RGB
     */
    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : { r: 0, g: 0, b: 0 };
    }

    /**
     * 添加交互效果
     */
    addInteractivity(container, moods) {
        // 添加悬浮提示
        container.addEventListener('mouseenter', (e) => {
            this.showTooltip(e, moods);
        });

        container.addEventListener('mouseleave', () => {
            this.hideTooltip();
        });

        // 添加点击事件
        container.addEventListener('click', () => {
            if (moods.length > 0) {
                const date = moods[0].date;
                const dateStr = date.toISOString().split('T')[0];
                window.location.href = `/mood/date/${dateStr}`;
            }
        });
    }

    /**
     * 显示悬浮提示
     */
    showTooltip(event, moods) {
        const tooltip = document.createElement('div');
        tooltip.id = 'mood-tooltip';
        tooltip.className = 'absolute z-50 bg-white border border-gray-200 rounded-lg shadow-lg p-3 max-w-xs';
        tooltip.style.top = `${event.pageY + 10}px`;
        tooltip.style.left = `${event.pageX + 10}px`;

        const moodsHtml = moods.slice(0, 3).map(mood => {
            const config = this.MOOD_CONFIG[mood.mood_type] || this.MOOD_CONFIG['custom'];
            const time = new Date(mood.timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
            return `
                <div class="flex items-center justify-between py-1">
                    <span class="flex items-center">
                        <span class="mr-2">${config.icon}</span>
                        <span class="text-sm">${config.label}</span>
                    </span>
                    <span class="text-xs text-gray-500">${time}</span>
                </div>
            `;
        }).join('');

        const moreText = moods.length > 3 ? `<div class="text-xs text-gray-500 pt-1">还有${moods.length - 3}条记录...</div>` : '';

        const dateObj = new Date(moods[0].date);
        tooltip.innerHTML = `
            <div class="font-medium text-sm mb-2">${dateObj.toLocaleDateString('zh-CN')} 心情记录</div>
            ${moodsHtml}
            ${moreText}
            <div class="text-xs text-gray-400 pt-2">点击查看详情</div>
        `;

        document.body.appendChild(tooltip);
    }

    /**
     * 隐藏悬浮提示
     */
    hideTooltip() {
        const tooltip = document.getElementById('mood-tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }
}

// 全局实例
window.moodViz = new MoodVisualization();

// 初始化函数
window.initMoodVisualization = function() {
    // 查找所有心情日历格子
    const moodCells = document.querySelectorAll('[data-mood-day]');

    moodCells.forEach(cell => {
        const dayData = JSON.parse(cell.dataset.moodDay || '{}');
        if (dayData.moods && dayData.moods.length > 0) {
            window.moodViz.renderMoodDay(dayData, cell);
        }
    });
};

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.initMoodVisualization === 'function') {
        window.initMoodVisualization();
    }
});