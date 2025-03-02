<template>
  <div class="top">
    <div class="top-op">
      <el-button type="primary" @click="uploadRTSPStream">RTSP流</el-button>
      <el-button type="success" @click="startAnalysis">开始分析</el-button>
    </div>
  </div>
  <div class="double-video-player">
    <div class="video-container">
      <PreviewVideo url="/directory/ts/getVideoInfo/65"></PreviewVideo>
    </div>
    <div class="separator" @mousedown="startDrag"></div>
    <div class="video-container">
      <PreviewVideo url="/directory/ts/getVideoInfo/65"></PreviewVideo>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted, onUnmounted} from 'vue';
import message from "@/utils/Message.js";
import PreviewVideo from "@/components/preview/PreviewVideo.vue";

const uploadRTSPStream = () => {
  message.error('todo');
};
const startAnalysis = () => {
  message.error('todo');
};

// 拖动相关变量
const isDragging = ref(false);
const startX = ref(0);
const separatorLeft = ref(50); // 初始分隔条位置

const startDrag = (e) => {
  isDragging.value = true;
  startX.value = e.clientX;
  document.addEventListener('mousemove', handleDrag);
  document.addEventListener('mouseup', endDrag);
};

const handleDrag = (e) => {
  if (isDragging.value) {
    const doubleVideoPlayer = document.querySelector('.double-video-player');
    const deltaX = e.clientX - startX.value;
    const newLeft = separatorLeft.value + (deltaX / doubleVideoPlayer.offsetWidth) * 100;
    if (newLeft > 10 && newLeft < 90) {
      separatorLeft.value = newLeft;
      startX.value = e.clientX;
      // 更新 CSS 变量
      doubleVideoPlayer.style.setProperty('--separator-left', `${newLeft}%`);
    }
  }
};

const endDrag = () => {
  isDragging.value = false;
  document.removeEventListener('mousemove', handleDrag);
  document.removeEventListener('mouseup', endDrag);
};

onMounted(() => {
  const doubleVideoPlayer = document.querySelector('.double-video-player');
  // 初始化 CSS 变量
  doubleVideoPlayer.style.setProperty('--separator-left', `${separatorLeft.value}%`);
});

onUnmounted(() => {
  document.removeEventListener('mousemove', handleDrag);
  document.removeEventListener('mouseup', endDrag);
});
</script>

<style lang="scss" scoped>
@use "@/assets/file.list.scss";

.double-video-player {
  display: flex;
  height: 400px; /* 可根据需要调整高度 */
  width: 100%;
  --separator-left: 50%; /* 初始分隔条位置 */
}

.video-container {
  overflow: hidden;
}

.double-video-player .video-container:nth-child(1) {
  width: calc(var(--separator-left) - 2.5px);
}

.double-video-player .video-container:nth-child(3) {
  width: calc(100% - var(--separator-left) - 2.5px);
}

.separator {
  width: 5px;
  background-color: #ccc;
  cursor: col-resize;
  position: relative;
  left: calc(var(--separator-left) - 2.5px);
  transition: left 0.2s ease;
  z-index: 1;
}

//.separator::before {
//  content: '';
//  position: absolute;
//  top: 0;
//  left: -2px;
//  width: 9px;
//  height: 100%;
//}
</style>
