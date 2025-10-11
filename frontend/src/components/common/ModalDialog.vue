<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div class="modal-overlay">
        <Transition
          enter-active-class="transition-all duration-300 ease-out"
          enter-from-class="opacity-0 scale-95"
          enter-to-class="opacity-100 scale-100"
          leave-active-class="transition-all duration-200 ease-in"
          leave-from-class="opacity-100 scale-100"
          leave-to-class="opacity-0 scale-95"
        >
          <div class="modal-dialog" @click.stop>
            <!-- 模态框头部 -->
            <div class="flex items-center justify-between p-6 border-b border-gray-200">
              <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
              <button
                @click="handleCancel"
                class="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <XMarkIcon class="w-5 h-5" />
              </button>
            </div>

            <!-- 模态框内容 -->
            <div class="p-6">
              <div class="flex items-start space-x-3">
                <!-- 图标 -->
                <div class="flex-shrink-0">
                  <component
                    :is="iconComponent"
                    :class="iconClass"
                    class="w-6 h-6"
                  />
                </div>

                <!-- 内容 -->
                <div class="flex-1">
                  <p class="text-gray-700 whitespace-pre-line">{{ content }}</p>
                </div>
              </div>
            </div>

            <!-- 模态框底部 -->
            <div class="flex justify-end space-x-3 p-6 border-t border-gray-200">
              <button
                v-if="showCancel"
                @click="handleCancel"
                class="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors"
              >
                {{ cancelText }}
              </button>
              <button
                @click="handleConfirm"
                :class="confirmButtonClass"
                class="px-4 py-2 rounded-lg font-medium transition-colors"
              >
                {{ confirmText }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import {
  XMarkIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XCircleIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  title: {
    type: String,
    default: '提示'
  },
  content: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['info', 'success', 'warning', 'error'].includes(value)
  },
  showCancel: {
    type: Boolean,
    default: true
  },
  confirmText: {
    type: String,
    default: '确认'
  },
  cancelText: {
    type: String,
    default: '取消'
  }
})

const emit = defineEmits(['confirm', 'cancel'])

// 根据类型获取图标和样式
const iconComponent = computed(() => {
  const icons = {
    success: CheckCircleIcon,
    error: XCircleIcon,
    warning: ExclamationTriangleIcon,
    info: InformationCircleIcon
  }
  return icons[props.type] || InformationCircleIcon
})

const iconClass = computed(() => {
  const classes = {
    success: 'text-green-500',
    error: 'text-red-500',
    warning: 'text-yellow-500',
    info: 'text-blue-500'
  }
  return classes[props.type] || 'text-blue-500'
})

const confirmButtonClass = computed(() => {
  const classes = {
    success: 'bg-green-600 hover:bg-green-700 text-white',
    error: 'bg-red-600 hover:bg-red-700 text-white',
    warning: 'bg-yellow-600 hover:bg-yellow-700 text-white',
    info: 'bg-blue-600 hover:bg-blue-700 text-white'
  }
  return classes[props.type] || 'bg-blue-600 hover:bg-blue-700 text-white'
})

// 事件处理
const handleConfirm = () => {
  emit('confirm')
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 1rem;
}

.modal-dialog {
  background-color: white;
  border-radius: 0.75rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  max-width: 28rem;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

/* 确保内容不会过长 */
.modal-dialog p {
  word-wrap: break-word;
  overflow-wrap: break-word;
}
</style>