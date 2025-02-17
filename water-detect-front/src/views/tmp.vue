

<!--<template>-->
<!--  <div class="framework">-->
<!--    <div class="header">-->
<!--      <div class="logo">-->
<!--        <span class="iconfont icon-pan"></span>-->
<!--        <span class="name">Easy云盘</span>-->
<!--      </div>-->
<!--      <div class="right-panel">-->
<!--        <el-popover-->
<!--            :width="800"-->
<!--            trigger="click"-->
<!--            v-model:visible="showUploader"-->
<!--            :offset="20"-->
<!--            transition="none"-->
<!--            :hide-after="0"-->
<!--            :popper-style="{ padding: '0px' }"-->
<!--        >-->
<!--          <template #reference>-->
<!--            <span class="iconfont icon-transfer"></span>-->
<!--          </template>-->
<!--          <template #default>-->
<!--            <Uploader-->
<!--                ref="uploaderRef"-->
<!--                @uploadCallback="uploadCallbackHandler"-->
<!--            ></Uploader>-->
<!--          </template>-->
<!--        </el-popover>-->

<!--        <el-dropdown>-->
<!--          <div class="user-info">-->
<!--            <div class="avatar">-->
<!--              <Avatar-->
<!--                  :userId="userInfo.userId"-->
<!--                  :avatar="userInfo.avatar"-->
<!--                  :timestamp="timestamp"-->
<!--                  :width="46"-->
<!--              ></Avatar>-->
<!--            </div>-->
<!--            <span class="nick-name">{{ userInfo.nickName }}</span>-->
<!--          </div>-->
<!--          <template #dropdown>-->
<!--            <el-dropdown-menu>-->
<!--              <el-dropdown-item @click="updateAvatar">-->
<!--                修改头像-->
<!--              </el-dropdown-item>-->
<!--              <el-dropdown-item @click="updatePassword">-->
<!--                修改密码-->
<!--              </el-dropdown-item>-->
<!--              <el-dropdown-item @click="logout"> 退出 </el-dropdown-item>-->
<!--            </el-dropdown-menu>-->
<!--          </template>-->
<!--        </el-dropdown>-->
<!--      </div>-->
<!--    </div>-->
<!--  </div>-->
<!--</template>-->

<!--<script setup>-->

<!--</script>-->

<!--<style scoped>-->

<!--</style>-->
