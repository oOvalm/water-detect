<template>
  <div class="video-container" ref="doubleVideoRef">
    <div class="video-wrapper" ref="leftRef">
      <PreviewVideo ref="player1Ref" v-if="showOrigin" :url="originUrl" :live="props.live"
                    @play="()=>{syncVideo('play', 1)}"
                    @pause="()=>{syncVideo('pause', 1)}"
                    @seeked="(newTime) => {syncVideo('seeked', 1, {newTime: newTime})}"
      ></PreviewVideo>
      <div class="loading" v-else>
        <el-icon class="is-loading">
          <Loading/>
        </el-icon>
        <input type="text" value="视频转码中"/>
      </div>
    </div>
    <div class="resize" ref="splitterRef" title="分界线">
      <div class="dots">⋮</div>
    </div>
    <div class="video-wrapper" ref="rightRef">
      <PreviewVideo ref="player2Ref" v-if="showAnalysed" :url="analysedUrl" :live="props.live"
                    @play="()=>{syncVideo('play', 2)}"
                    @pause="()=>{syncVideo('pause', 2)}"
                    @seeked="(newTime) => {syncVideo('seeked', 2, {newTime: newTime})}"
      ></PreviewVideo>
      <div class="loading" v-else>
        <el-icon class="is-loading">
          <Loading/>
        </el-icon>
      </div>
    </div>
  </div>
</template>
<script setup>
import {onMounted, onUnmounted, ref, watch} from "vue";
import PreviewVideo from "@/components/preview/PreviewVideo.vue";
import {Loading} from "@element-plus/icons-vue";


const props = defineProps({
  originUrl: {
    type: String,
    default: ""
  },
  analysedUrl: {
    type: String,
    default: ""
  },
  showOrigin: {
    type: Boolean,
    default: false
  },
  showAnalysed: {
    type: Boolean,
    default: false
  },
  isSync: {
    type: Boolean,
    default: false,
  },
  live: {
    type: Boolean,
    default: false,
  }
})
const doubleVideoRef = ref();
const splitterRef = ref();
const leftRef = ref();
const rightRef = ref();
const player1Ref = ref();
const player2Ref = ref();

watch(() => props.isSync, (oldValue, newValue) => {
  if (newValue) {
    console.log("xxxx");
    player2Ref.value.setVideoStatus(player1Ref.value.getVideoStatus());
  }
})

const syncVideo = (op, srcPlayerID, extra) => {
  console.log(props.isSync)
  if (!props.isSync) return;
  let destPlayer = null;
  if (srcPlayerID === 1) destPlayer = player2Ref.value
  else destPlayer = player1Ref.value
  if (op === 'play') {
    destPlayer.playVideo();
  } else if (op === 'pause') {
    destPlayer.pauseVideo();
  } else if (op === 'seeked') {
    const newTime = extra.newTime
    destPlayer.seekVideo(newTime);
  }
}


const addListener = () => {
  let resize = splitterRef.value;
  let left = leftRef.value;
  let right = rightRef.value;
  let doubleVideo = doubleVideoRef.value;
  console.log(resize)
  // 鼠标按下事件
  resize.onmousedown = function (e) {
    // 颜色改变提醒
    resize.style.background = '#818181';
    var startX = e.clientX;
    var leftWidth = left.offsetWidth;

    // 鼠标拖动事件
    document.onmousemove = function (e) {
      var endX = e.clientX;
      var moveLen = leftWidth + (endX - startX); // 计算移动的距离
      var maxT = doubleVideo.clientWidth - resize.offsetWidth; // 容器宽度 - 分隔条的宽度

      if (moveLen < 30) moveLen = 30; // 最小宽度
      if (moveLen > maxT - 30) moveLen = maxT - 30; // 最大宽度

      left.style.width = moveLen + 'px';
      right.style.width = (doubleVideo.clientWidth - moveLen - 10) + 'px';
    };

    // 鼠标松开事件
    document.onmouseup = function () {
      // 颜色恢复
      resize.style.background = '#d6d6d6';
      document.onmousemove = null;
      document.onmouseup = null;
      resize.releaseCapture && resize.releaseCapture(); // 释放鼠标捕获
    };

    resize.setCapture && resize.setCapture(); // 设置鼠标捕获
    return false;
  };
}

const removeListener = () => {
  // 移除鼠标事件
  if (splitterRef.value) {
    splitterRef.value.onmousedown = null;
    document.onmousemove = null;
    document.onmouseup = null;
  }
}

onMounted(() => {
  addListener();
})
onUnmounted(() => {
  removeListener();
})
</script>

<style lang="scss" scoped>
@use "@/assets/file.list.scss";

.double-video-player {
  display: flex;
  height: 100%; /* 可根据需要调整高度 */
  width: 100%;
  --separator-left: 50%; /* 初始分隔条位置 */
}

.video-container {
  display: flex;
  height: 300px;
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

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 100px;
}

/*拖拽区div样式*/
.resize {
  cursor: col-resize;
  float: left;
  position: relative;
  top: 0;
  background-color: #d6d6d6;
  border-radius: 5px;
  margin-top: -10px;
  width: 10px;
  height: 100%;
  background-size: cover;
  background-position: center;
  font-size: 32px;
  color: white;

  .dots {
    -webkit-box-orient: vertical;
    -webkit-box-direction: normal;
    display: -webkit-box;
    display: -webkit-flex;
    display: flex;
    -webkit-flex-direction: column;
    flex-direction: column;
  }
}

/*右侧div'样式*/
.right {
  float: left;
  width: 68%; /*右侧初始化宽度*/
  height: 100%;
  background: #fff;
  box-shadow: -1px 4px 5px 3px rgba(0, 0, 0, 0.11);
}

/*拖拽区鼠标悬停样式*/
.resize:hover {
  color: #444444;
}
</style>
