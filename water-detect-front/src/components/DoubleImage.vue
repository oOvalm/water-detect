<template>
  <div class="image-splitter">
    <div class="left-image" :style="{ width: leftWidth + '%' }">
      <img class="image-contain" :src="originUrl" alt="Left Image">
    </div>
    <div class="splitter" @mousedown="startDrag"></div>
    <div class="right-image" :style="{ width: 100 - leftWidth + '%' }">
      <img class="image-contain" :src="analysedUrl" alt="Right Image">
    </div>
  </div>
</template>

<script setup>
import {ref} from 'vue';

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
</style>
