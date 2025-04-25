<template>
  <div class="image-splitter">
    <div class="left-image" :style="{ width: leftWidth + '%' }">
      <img class="image-contain" :src="originUrl" alt="Left Image">
    </div>
    <div class="splitter" @mousedown="startDrag"></div>
    <div class="right-image" :style="{ width: 100 - leftWidth + '%' }">
      <div v-if="isLoading" class="loading">
        <el-icon class="is-loading">
          <Loading/>
        </el-icon>
      </div>
      <img v-else class="image-contain" :src="analysedUrl" alt="Right Image">
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted, onUnmounted} from 'vue';
import {Loading} from "@element-plus/icons-vue";

const props = defineProps({
  originUrl: {
    type: String,
    default: ""
  },
  analysedUrl: {
    type: String,
    default: ""
  }
})
const leftWidth = ref(50);
let isDragging = false;
let startX = 0;
let startWidth = 0;
const isLoading = ref(true);
let intervalId;

const startDrag = (e) => {
  isDragging = true;
  startX = e.clientX;
  startWidth = leftWidth.value;
  document.addEventListener('mousemove', onDrag);
  document.addEventListener('mouseup', endDrag);
};

const onDrag = (e) => {
  if (isDragging) {
    const deltaX = e.clientX - startX;
    const newWidth = startWidth + (deltaX / window.innerWidth) * 100;
    leftWidth.value = Math.min(Math.max(newWidth, 10), 90);
  }
};

const endDrag = () => {
  isDragging = false;
  document.removeEventListener('mousemove', onDrag);
  document.removeEventListener('mouseup', endDrag);
};

const fetchImage = async () => {
  console.log("fetch image")
  try {
    const response = await fetch(props.analysedUrl);
    if (!response.ok) {
      console.log("not finished")
      return
    }
    isLoading.value = false;
    clearInterval(intervalId);
    intervalId = null
  } catch (error) {
    isLoading.value = true;
  }
};

onMounted(() => {
  fetchImage();
  intervalId = setInterval(fetchImage, 1000);
});

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId);
});
</script>

<style scoped>
.image-splitter {
  display: flex;
  height: 100%;
  width: 100%;
}

.left-image,
.right-image {
  overflow: visible;
  display: flex;
  justify-content: center;
  align-items: center;
}

.image-contain {
  width: 100%;
  height: auto;
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.splitter {
  width: 5px;
  background-color: #ccc;
  cursor: col-resize;
}

.loading {
  font-size: 24px;
  color: #999;
}
</style>
