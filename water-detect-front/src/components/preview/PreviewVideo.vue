<template>
  <div ref="playerRef" id="player"></div>
</template>

<script setup>
import DPlayer from "dplayer";
import {nextTick, onMounted, ref} from "vue";
import Hls from "hls.js";


const props = defineProps({
  url: {
    type: String,
  },
});

const emit = defineEmits(["play", "pause", "seeked"]);

const videoInfo = ref({
  video: null,
});


let dp = null;

let isCallback = true

const seekCallback = () => {
  if (isCallback) emit('seeked', dp.video.currentTime);
}

const playerRef = ref(null);

const initPlayer = () => {
  dp = new DPlayer({
    element: playerRef.value,
    container: playerRef.value,
    mutex: false,
    theme: "#b7daff",
    screenshot: true,
    video: {
      url: `/api${props.url}`,
      type: "customHls",
      customType: {
        customHls: function (video, player) {
          const hls = new Hls();
          hls.loadSource(video.src);
          hls.attachMedia(video);
        },
      },
    },
  });
  dp.on('play', () => {
    emit('play')
  })
  dp.on('pause', () => {
    emit('pause')
  })
  dp.on('seeked', seekCallback);
};
const playVideo = () => {
  if (dp) {
    dp.play();
  }
}
const pauseVideo = () => {
  if (dp) {
    dp.pause();
  }
}
const seekVideo = (time) => {
  if (dp) {
    // 防止死循环
    isCallback = false
    dp.seek(time);
    setTimeout(() => {
      isCallback = true;
      console.log("wowooowo");
    }, 1000)
  }
}
defineExpose({playVideo, pauseVideo, seekVideo});
onMounted(() => {
  nextTick(() => {
    initPlayer();
  });
});
</script>

<style lang="scss" scoped>
#player {
  width: 100%;

  :deep.dplayer-video-wrap {
    text-align: center;

    .dplayer-video {
      margin: 0px auto;
      max-height: calc(100vh - 41px);
    }
  }
}
</style>
