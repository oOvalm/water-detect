<template>
  <el-card class="profile-card">
    <el-form :model="profileForm" label-width="100px"
             :rules="rules">
      <!-- 头像上传 -->
      <el-form-item label="头像">
        <el-upload
            class="avatar-uploader"
            action="/api/account/avatar"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
            :before-upload="beforeAvatarUpload"
            accept="image/*"
        >
          <el-avatar v-if="profileForm.avatar && profileForm.avatar.length > 0" :size="80"
                     :src="`/api/${profileForm.avatar}`"/>
          <el-avatar v-else :size="80" :src="defaultAvatar"/>
        </el-upload>
      </el-form-item>

      <!-- 昵称 -->
      <el-form-item label="昵称" prop="username">
        <el-input v-model="profileForm.username"></el-input>
      </el-form-item>

      <!-- 性别 -->
      <el-form-item label="性别">
        <el-radio-group v-model="profileForm.sex">
          <el-radio :label="1">男</el-radio>
          <el-radio :label="2">女</el-radio>
        </el-radio-group>
      </el-form-item>

      <!-- 密码 -->
      <el-form-item label="密码" prop="password">
        <el-input type="password" v-model="profileForm.password"></el-input>
      </el-form-item>

      <el-form-item label="确认密码" prop="confirmPassword">
        <el-input type="password" v-model="profileForm.confirmPassword"></el-input>
      </el-form-item>

      <!-- 邮箱 -->
      <el-form-item label="邮箱">
        <el-input :disabled="true" v-model="profileForm.email"></el-input>
      </el-form-item>
      <!--      <el-form-item label="验证码">-->
      <!--        <el-row :gutter="16">-->
      <!--          <el-col :span="16">-->
      <!--            <el-input v-model="profileForm.checkCode"></el-input>-->
      <!--          </el-col>-->
      <!--          <el-col :span="8">-->
      <!--            <el-button type="primary" :disabled="emailCheckBtn.disable" @click="sendEmailVerification"-->
      <!--                       style="width: 100%">{{ emailCheckBtn.msg }}-->
      <!--            </el-button>-->
      <!--          </el-col>-->
      <!--        </el-row>-->
      <!--      </el-form-item>-->

      <!-- 保存按钮 -->
      <el-form-item>
        <el-button type="primary" @click="saveProfile">保存</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import {onMounted, ref} from 'vue';
import {ElMessage} from 'element-plus';
import httpRequest from "@/api/httpRequest.ts";
import Verify from "@/utils/Verify.js";

const emit = defineEmits(['updateProfile'])
const defaultAvatar = ref('https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png')
// 表单数据
const profileForm = ref({
  avatar: '',
  username: '用户昵称',
  sex: 0,
  password: '',
  confirmPassword: '',
  email: 'user@example.com',
});

const checkPassword = (rule, value, callback) => {
  if (value && Verify.password(rule, value, callback)) {
    callback(new Error(rule.message));
  } else {
    callback();
  }
};
const checkRePassword = (rule, value, callback) => {
  if (value && value !== profileForm.value.password) {
    callback(new Error(rule.message));
  } else {
    callback();
  }
};
const rules = {
  username: [{required: true, message: "请输入昵称"}],
  password: {
    validator: checkPassword,
    message: "密码只能是数字，字母，特殊字符 6-18位",
  },
  confirmPassword: {
    validator: checkRePassword,
    message: "两次输入的密码不一致",
  },
}

const emailCheckBtn = ref({
  disable: false,
  msg: "获取验证码"
})
// 头像上传成功回调
const handleAvatarSuccess = (response, file) => {
  console.log(response)
  profileForm.value.avatar = response.url;
};

// 头像上传前的校验
const beforeAvatarUpload = (file) => {
  // const isJPG = file.type === 'image/jpeg';
  const isLt2M = file.size / 1024 / 1024 < 2;

  // if (!isJPG) {
  //   ElMessage.error('上传头像图片只能是 JPG 格式!');
  // }
  if (!isLt2M) {
    ElMessage.error('上传头像图片大小不能超过 2MB!');
  }
  return isLt2M;
};

// 发送邮箱验证邮件
const sendEmailVerification = () => {
  // 调用后端接口发送验证邮件
  httpRequest.post('/account/captcha', {
    email: profileForm.value.email,
    type: 'modify',
  }).then(({data}) => {
    if (data.code !== 0) {
      ElMessage.error(data.msg);
    } else {
      ElMessage.success("验证码已发送")
      let remainingTime = 60;
      emailCheckBtn.value.disable = true
      emailCheckBtn.value.msg = `${remainingTime}`
      const intervalId = setInterval(() => {
        remainingTime--;
        if (remainingTime < 0) {
          clearInterval(intervalIfd);
          emailCheckBtn.value.disable = false;
          emailCheckBtn.value.msg = `获取验证码`
        } else {
          emailCheckBtn.value.msg = `${remainingTime}`
        }
      }, 1000);
    }
  })
};

// 保存个人信息
const saveProfile = () => {
  if (profileForm.value.password !== profileForm.value.confirmPassword) {
    ElMessage.error('密码和确认密码不一致');
    return;
  }

  httpRequest.post(`/account/${profileForm.value.id}`, profileForm.value)
      .then(({data}) => {
        if (data.code !== 0) {
          ElMessage.error(data.msg);
        } else {
          ElMessage.success('个人信息保存成功');
          emit('updateProfile')
        }
      })
      .catch((error) => {
        ElMessage.error('保存个人信息失败');
        console.error(error);
      });
};

onMounted(() => {
  httpRequest.get("account/selfInfo").then(({data}) => {
    if (data.code == null || data.code !== 0) {
      logout()
    } else {
      profileForm.value = data.data
    }
  }).catch((e) => {
    console.log(e);
    message.error("获取信息失败")
  })
})

</script>

<style scoped>
.profile-card {
  max-width: 600px;
  margin: 20px auto;
}

.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.avatar-uploader .el-upload:hover {
  border-color: #409EFF;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 150px;
  height: 150px;
  line-height: 150px;
  text-align: center;
}

.avatar {
  width: 150px;
  height: 150px;
  display: block;
}

.el-button {
  margin-left: 5px;
}
</style>
