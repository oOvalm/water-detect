<template>
  <div class="home-menu" :style="{ width: isCollapsed ? '64px' : '200px' }">
    <el-menu class="el-menu-class"
             :default-active="activeID"
             unique-opened @select="handleSelect">
      <el-menu-item
          v-for="(item, index) in menus"
          :key="index"
          :index="item.index.toString()"
      >
        <template #title>
          <el-icon>
            <component :is="item.icon"/>
          </el-icon>
          <span v-if="!isCollapsed">{{ item.title }}</span>
        </template>
      </el-menu-item>
    </el-menu>
    <el-button class="collapse-button" @click="toggleCollapse">
      <el-icon>
        <ArrowRight v-if="isCollapsed"/>
        <ArrowLeft v-else></ArrowLeft>
      </el-icon>
      <span v-if="!isCollapsed">收起侧边栏</span>
    </el-button>
  </div>
</template>

<script setup>
import {onBeforeMount, onMounted, ref} from 'vue';
import router from "@/router/index.js";
import {Share, House, ArrowLeft, ArrowRight, Files, Key, VideoCamera, Avatar} from "@element-plus/icons-vue";
import {useRoute} from "vue-router";

// 定义菜单数据
const activeID = ref()
const menus = ref([
  {
    index: 0,
    title: '首页',
    icon: House,
    path: '/',
  },
  {
    index: 1,
    title: '在线分析',
    icon: VideoCamera,
    path: 'analyse',
  },
  {
    index: 2,
    title: "key管理",
    icon: Key,
    path: 'stream-key'
  },
  {
    index: 3,
    title: '分析记录',
    icon: Files,
    path: 'disk'
  },
  {
    index: 4,
    title: '测试页面',
    icon: Files,
    path: 'test'
  },
  {
    index: 5,
    title: '个人中心',
    icon: Avatar,
    path: 'profile'
  },
  {
    index: 6,
    title: '我的分享',
    icon: Share,
    path: 'share'
  }
]);

// 控制侧边栏展开和收起的状态变量
const isCollapsed = ref(false);

// 切换侧边栏展开和收起状态的方法
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
};

// 处理菜单项选择事件的函数
const handleSelect = (key, keyPath) => {
  router.push(menus.value[key].path)
};

onMounted(() => {
  const pat = useRoute().path.replaceAll('/', '');
  for (let i = 0; i < menus.value.length; i++) {
    if (pat === menus.value[i].path) {
      activeID.value = i;
    }
  }
})
</script>

<style lang="scss" scoped>
.home-menu {
  top: 64px;
  height: 100%;
  overflow: auto;
  @apply shadow-md fixed bg-light-50;
  display: flex;
  flex-direction: column;
}

.collapse-button {
  margin-top: auto; /* 将按钮推到底部 */
  width: 100%;
  border: none;
  background-color: transparent;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px 0;
}
</style>
