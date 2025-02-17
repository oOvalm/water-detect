<template>
  <el-header class="home-header">
    <!-- 左边图标 -->aaaa
    <div class="left-icon">
      <i class="el-icon-house"></i>
    </div>
    <!-- 右边头像及下拉框 -->
    <div class="right-avatar">
      <el-dropdown>
        <span class="el-dropdown-link">
          <img src="@/assets/qq.png" alt="Avatar" class="avatar"/>
          <el-icon class="el-icon--right"><arrow-down /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item :icon="Avatar">个人中心</el-dropdown-item>
            <el-dropdown-item :icon="InfoFilled">关于</el-dropdown-item>
            <el-dropdown-item :icon="SwitchButton">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </el-header>
</template>


<script setup>
import { ref } from 'vue';
import {ArrowDown, Avatar, CirclePlus, InfoFilled, SwitchButton} from "@element-plus/icons-vue";

// 处理下拉框选项点击事件
const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      console.log('跳转到个人中心');
      // 这里可以添加跳转到个人中心的路由逻辑
      break;
    case 'about':
      console.log('显示关于页面');
      // 这里可以添加显示关于页面的逻辑
      break;
    case 'logout':
      console.log('退出登录');
      // 这里可以添加退出登录的逻辑
      break;
    default:
      break;
  }
};
</script>

<style scoped lang="scss">
.home-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background-color: #f5f5f5;
  height: 60px;
}

.left-icon {
  font-size: 24px;
  color: #333;
}

.right-avatar {
  position: relative;
  color: #222222;
}

.avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  cursor: pointer;
}
</style>
