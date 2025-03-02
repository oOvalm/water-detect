<template>
  <div class="top">
    <div class="top-op">
      <el-button type="primary" @click="uploadRTSPStream">RTSP流</el-button>
      <el-button type="success" @click="startAnalysis">开始分析</el-button>
    </div>
  </div>
  <div class="box" ref="box" id="double-video" v-if="fileInfo.id">
    <div class="left" id="left">
      <PreviewVideo url="x"></PreviewVideo>
    </div>
    <div class="resize" title="分界线" id="splitter">
      <div class="dots">⋮</div>
    </div>
    <div class="right" id="right">
      <PreviewVideo url="x"></PreviewVideo>
    </div>
  </div>
  <div v-else>
    <el-upload
        class="upload-demo"
        drag
        action="https://run.mocky.io/v3/9d059bf9-4660-45f2-925d-ce80ad6c4d15"
        multiple
    >
      <el-icon class="el-icon--upload">
        <upload-filled/>
      </el-icon>
      <div class="el-upload__text">
        拖动文件到此处或 <em>点击上传文件</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          视频仅支持分析mp4, 图片仅支持jpg/png
        </div>
      </template>
    </el-upload>
  </div>
</template>

<script setup>
import {ref, onMounted, onUnmounted} from 'vue';
import message from "@/utils/Message.js";
import PreviewVideo from "@/components/preview/PreviewVideo.vue";
import {UploadFilled} from "@element-plus/icons-vue";

const fileInfo = ref({});

const uploadRTSPStream = () => {
  message.error('todo');
};
const startAnalysis = () => {
  message.error('todo');
};

onMounted(() => {
  var resize = document.getElementById('splitter');
  var left = document.getElementById('left');
  var right = document.getElementById('right');
  var doubleVideo = document.getElementById('double-video');

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
  height: 100%; /* 可根据需要调整高度 */
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

/* 拖拽相关样式 */
/*包围div样式*/
.box {
  width: 100%;
  height: 100%;
  margin: 1% 0px;
  overflow: hidden;
  box-shadow: -1px 9px 10px 3px rgba(0, 0, 0, 0.11);
}

/*左侧div样式*/
.left {
  width: calc(32% - 10px);
  height: 100%;
  background: #FFFFFF;
  float: left;
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

/*拖拽区鼠标悬停样式*/
.resize:hover {
  color: #444444;
}

/*右侧div'样式*/
.right {
  float: left;
  width: 68%; /*右侧初始化宽度*/
  height: 100%;
  background: #fff;
  box-shadow: -1px 4px 5px 3px rgba(0, 0, 0, 0.11);
}
</style>
