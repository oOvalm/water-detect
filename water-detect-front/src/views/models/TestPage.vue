<template>
  <div>
    <el-input v-model="streamKey" placeholder="请输入 streamkey"/>
    <el-checkbox v-model="isAnalyse" label="是否分析后" size="small"/>
    <el-button @click="playStream">确认</el-button>
    <div ref="playerContainer"></div>
  </div>
</template>

<script setup>
import {onUnmounted, ref} from 'vue';
import {ElInput, ElButton} from 'element-plus';
import DPlayer from 'dplayer';
import Hls from "hls.js";
import httpRequest from "@/api/httpRequest.ts";
import message from "@/utils/Message.js";

const isAnalyse = ref(false);
const streamKey = ref('');
const playerContainer = ref(null);
let dp = null;

const playStream = () => {
  if (dp) {
    dp.destroy();
    dp = null;
  }
  httpRequest.get(`/stream/proxy/live/${streamKey.value}?analyse=${isAnalyse.value}`).then(({data}) => {
    const hlsUrl = `/api/stream/${data}`;
    dp = new DPlayer({
      container: playerContainer.value,
      live: true,
      autoplay: true,
      video: {
        url: hlsUrl,
        type: "customHls",
        customType: {
          customHls: function (video, player) {
            const hlsConfig = {
              // 最大重试次数
              maxRetry: Infinity,
              // 初始重试延迟时间（毫秒）
              retryDelay: 3000,
              // 每次重试后延迟时间的增加量（倍数）
              backoffFactor: 1
            };
            const hls = new Hls(hlsConfig);
            hls.loadSource(video.src);
            hls.attachMedia(video);
          },
        },
      }
    });
  }).catch((e) => {
    message.error('获取流连接失败');
    console.log(e)
  })
};

onUnmounted(() => {
  if (dp) {
    dp.destroy();
  }
})
</script>

<style scoped>
/* 可以添加自定义样式 */
</style>
