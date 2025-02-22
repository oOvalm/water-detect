<template>
  <div class="home-menu">
    <el-menu class="el-menu-class"
             :default-active="activeID"
             unique-opened @select="handleSelect">
      <el-menu-item
          v-for="(item, index) in menus"
          :key="index"
          :index="item.index.toString()"
      >
        <!-- 菜单项的图标 -->
        <template #title>
          <el-icon>
            <House/>
          </el-icon>
          <!-- 菜单项的文本 -->
          <span>{{ item.title }}</span>
        </template>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup>
import {onBeforeMount, onMounted, ref} from 'vue';
import router from "@/router/index.js";
import {House} from "@element-plus/icons-vue";
import {useRoute} from "vue-router";

// 定义菜单数据
const activeID = ref()
const menus = ref([
  {
    index: 0,
    title: '首页',
    icon: '',
    path: '/',
  },
  {
    index: 1,
    title: '水域分析',
    icon: 'el-icon-user',
    path: 'analyse',
  },
  {
    index: 2,
    title: '分析记录',
    icon: 'el-icon-goods',
    path: 'disk'
  }
]);

// 处理菜单项选择事件的函数
const handleSelect = (key, keyPath) => {
  // console.log(`选中的菜单项索引: ${typeof(key)}`);
  // console.log(`选中菜单项的路径: ${typeof(keyPath[key])}`);
  // 这里可以添加路由跳转等逻辑
  // 例如：router.push({ name: 'SomeRouteName' })
  router.push(menus.value[key].path)
};
onBeforeMount(() => {
  const pat = useRoute().path.replaceAll('/', '');
  for (let i = 0; i < menus.value.length; i++) {
    if (pat === menus.value[i].path) {
      activeID.value = i;
    }
  }
  console.log(activeID.value)
})
</script>

<style lang="scss" scoped>
.home-menu {
  top: 64px;
  bottom: 0;
  left: 0;
  overflow: auto;
  @apply shadow-md fixed bg-light-50;
  //.el-menu-class{
  //}
}
</style>
