/**
 * v-click-outside 指令
 * 当点击元素外部时触发回调
 */
const clickOutside = {
  // 在元素挂载前
  beforeMount(el, binding) {
    el._clickOutside = (event) => {
      // 检查点击是否在元素外部
      if (!(el === event.target || el.contains(event.target))) {
        // 调用绑定的方法
        binding.value(event)
      }
    }
    // 添加事件监听器
    document.addEventListener('click', el._clickOutside)
  },

  // 元素卸载时
  unmounted(el) {
    // 移除事件监听器
    if (el._clickOutside) {
      document.removeEventListener('click', el._clickOutside)
      delete el._clickOutside
    }
  }
}

export default clickOutside

// 注册为全局指令的函数
export const setupClickOutside = (app) => {
  app.directive('click-outside', clickOutside)
}