<template>

  <div class="top">
    <div class="top-op">
      <el-button type="primary" @click="uploadRTSPStream">RTSP流</el-button>
      <el-button type="success" @click="startAnalysis">开始分析</el-button>
    </div>

  </div>
  <div class="double-video-player">
    <div class="video-container">
      <video-player ref="videoRef1" :options="videoOptions1"></video-player>
    </div>
    <div class="separator" @mousedown="startDrag"></div>
    <div class="video-container">
      <video-player ref="videoRef2" :options="videoOptions2"></video-player>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted, onUnmounted, getCurrentInstance} from 'vue'
import Navigation from "@/components/Navigation.vue";
import VideoPlayer from 'video-player';
import 'video.js/dist/video-js.css';
import message from "@/utils/Message.js";

const uploadRTSPStream = () => {
  message.error('todo')
}
const startAnalysis = () => {
  message.error('todo')
}


// 引用视频播放器
const videoRef1 = ref();
const videoRef2 = ref();

// 视频配置选项
const videoOptions1 = {
  autoplay: false, // 自动播放
  controls: true, // 显示控制条
  preload: 'auto', // 预加载
  width: '100%',
  height: '100%',
  fluid: true, // 自适应大小
  loop: false,
  sources: [
    {
      type: 'video/mp4',
      src: 'file:///D:/Videos/small.mp4'
    }
  ]
};

const videoOptions2 = {
  autoplay: false,
  controls: true,
  preload: 'auto',
  width: '100%',
  height: '100%',
  fluid: true,
  loop: false,
  sources: [
    {
      type: 'video/mp4',
      src: 'file:///D:/Videos/small.mp4'
    }
  ]
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
    const deltaX = e.clientX - startX.value;
    const newLeft = separatorLeft.value + (deltaX / document.querySelector('.double-video-player').offsetWidth) * 100;
    if (newLeft > 10 && newLeft < 90) {
      separatorLeft.value = newLeft;
      startX.value = e.clientX;
    }
  }
};

const endDrag = () => {
  isDragging.value = false;
  document.removeEventListener('mousemove', handleDrag);
  document.removeEventListener('mouseup', endDrag);
};

onMounted(() => {
  // 初始化视频播放器
  const player1 = videoRef1.value.player;
  const player2 = videoRef2.value.player;
});
</script>

<style lang="scss" scoped>
@use "@/assets/file.list.scss";

.double-video-player {
  display: flex;
  height: 400px; /* 可根据需要调整高度 */
  width: 100%;
}

.video-container {
  flex: 1;
  overflow: hidden;
}

.separator {
  width: 5px;
  background-color: #ccc;
  cursor: col-resize;
  position: relative;
  left: calc(50% - 2.5px);
  transition: left 0.2s ease;
  z-index: 1;
}

.separator::before {
  content: '';
  position: absolute;
  top: 0;
  left: -2px;
  width: 9px;
  height: 100%;
}

.double-video-player .video-container:nth-child(1) {
  width: calc(100% - 5px);
  width: calc(var(--separator-left, 50%) - 2.5px);
}

.double-video-player .video-container:nth-child(3) {
  width: calc(100% - 5px);
  width: calc(100% - var(--separator-left, 50%) - 2.5px);
}

.double-video-player::before {
  --separator-left: 50%;
  content: '';
  display: block;
  width: 0;
  height: 0;
}
</style>
