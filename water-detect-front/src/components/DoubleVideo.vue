<template>
  <div class="video-container">
    <!-- 第一个视频播放器 -->
    <div class="video-wrapper" :style="{ width: `${video1Width.value}%` }">
      <video
          ref="video1Ref"
          :src="videoSrc1"
          controls
          @play="onPlay(1)"
          @pause="onPause(1)"
          @timeupdate="onTimeUpdate(1)"
      ></video>
    </div>
    <!-- 分割条 -->
    <div
        class="divider"
        ref="dividerRef"
        @mousedown="startDrag"
        @touchstart="startDrag"
    ></div>
    <!-- 第二个视频播放器 -->
    <div class="video-wrapper" :style="{ width: `${video2Width.value}%` }">
      <video
          ref="video2Ref"
          :src="videoSrc2"
          controls
          @play="onPlay(2)"
          @pause="onPause(2)"
          @timeupdate="onTimeUpdate(2)"
      ></video>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted, onBeforeUnmount} from 'vue';

// 视频源地址
const videoSrc1 = 'your_video_url_1.mp4';
const videoSrc2 = 'your_video_url_2.mp4';

// 视频播放器引用
const video1Ref = ref(null);
const video2Ref = ref(null);
// 分割条引用
const dividerRef = ref(null);

// 控制视频播放器同步的标志
const isSyncing = ref(false);
// 两个视频播放器的宽度
const video1Width = ref(50);
const video2Width = ref(50);
// 拖动相关状态
const isDragging = ref(false);
const startX = ref(0);
const initialVideo1Width = ref(0);

// 播放事件处理
const onPlay = (playerIndex) => {
  if (isSyncing.value) return;
  isSyncing.value = true;
  const otherPlayer = playerIndex === 1 ? video2Ref.value : video1Ref.value;
  otherPlayer.play();
  isSyncing.value = false;
};

// 暂停事件处理
const onPause = (playerIndex) => {
  if (isSyncing.value) return;
  isSyncing.value = true;
  const otherPlayer = playerIndex === 1 ? video2Ref.value : video1Ref.value;
  otherPlayer.pause();
  isSyncing.value = false;
};

// 播放进度更新事件处理
const onTimeUpdate = (playerIndex) => {
  if (isSyncing.value) return;
  isSyncing.value = true;
  const currentPlayer = playerIndex === 1 ? video1Ref.value : video2Ref.value;
  const otherPlayer = playerIndex === 1 ? video2Ref.value : video1Ref.value;
  otherPlayer.currentTime = currentPlayer.currentTime;
  isSyncing.value = false;
};

// 开始拖动
const startDrag = (event) => {
  isDragging.value = true;
  startX.value = event.clientX || event.touches[0].clientX;
  initialVideo1Width.value = video1Width.value;
};

// 拖动过程
const drag = (event) => {
  if (!isDragging.value) return;
  const currentX = event.clientX || event.touches[0].clientX;
  const diffX = currentX - startX.value;
  const containerWidth = dividerRef.value.parentElement.offsetWidth;
  const newWidth = initialVideo1Width.value + (diffX / containerWidth) * 100;
  if (newWidth > 10 && newWidth < 90) {
    video1Width.value = newWidth;
    video2Width.value = 100 - newWidth;
  }
};

// 停止拖动
const stopDrag = () => {
  isDragging.value = false;
};

onMounted(() => {
  video1Ref.value.play();
  video2Ref.value.play();
  window.addEventListener('mousemove', drag);
  window.addEventListener('mouseup', stopDrag);
  window.addEventListener('touchmove', drag);
  window.addEventListener('touchend', stopDrag);
});

onBeforeUnmount(() => {
  window.removeEventListener('mousemove', drag);
  window.removeEventListener('mouseup', stopDrag);
  window.removeEventListener('touchmove', drag);
  window.removeEventListener('touchend', stopDrag);
});
</script>

<style scoped>
.video-container {
  display: flex;
  height: 300px;
}

.video-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

video {
  width: 100%;
  height: auto;
}

.divider {
  width: 5px;
  background-color: #ccc;
  cursor: col-resize;
}
</style>
