<template>
  <div class="login-body">
    <div class="login-panel">
      <el-form
          class="login-register"
          :model="formData"
          :rules="rules"
          ref="formDataRef"
      >
        <div class="login-title">水域分析系统</div> <!-- todo: 标题拿到外边 -->
        <!--input输入-->
        <el-form-item prop="email">
          <el-input
              size="large"
              clearable
              placeholder="请输入邮箱"
              v-model.trim="formData.email"
          >
            <template #prefix>
              <span class="iconfont icon-account"></span>
            </template>
          </el-input>
        </el-form-item>
        <!--登录密码-->
        <el-form-item prop="password" v-if="opType == 1">
          <el-input
              type="password"
              size="large"
              placeholder="请输入密码"
              v-model.trim="formData.password"
              show-password
          >
            <template #prefix>
              <span class="iconfont icon-password"></span>
            </template>
          </el-input>
        </el-form-item>
        <!--注册-->
        <div v-if="opType == 0 || opType == 2">
          <el-form-item prop="emailCode">
            <div class="send-emali-panel">
              <el-input
                  size="large"
                  placeholder="请输入邮箱验证码"
                  v-model.trim="formData.emailCaptcha"
              >
                <template #prefix>
                  <span class="iconfont icon-checkcode"></span>
                </template>
              </el-input>
              <el-button
                  :disabled="emailCheckBtn.disable"
                  class="send-mail-btn"
                  type="primary"
                  size="large"
                  @click="getEmailCode"
              >{{ emailCheckBtn.msg }}
              </el-button
              >
            </div>
            <el-popover placement="left" :width="500" trigger="click">
              <div>
                <p>1、在垃圾箱中查找邮箱验证码</p>
                <p>2、在邮箱中头像->设置->反垃圾->白名单->设置邮件地址白名单</p>
                <p>
                  3、将邮箱【laoluo@wuhancoder.com】添加到白名单不知道怎么设置？
                </p>
              </div>
              <template #reference>
                <span class="a-link" :style="{ 'font-size': '14px' }"
                >未收到邮箱验证码？</span
                >
              </template>
            </el-popover>
          </el-form-item>
          <el-form-item prop="nickName" v-if="opType == 0">
            <el-input
                size="large"
                clearable
                placeholder="请输入昵称"
                v-model.trim="formData.username"
                maxLength="20"
            >
              <template #prefix>
                <span class="iconfont icon-account"></span>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item prop="registerPassword">
            <el-input
                type="password"
                size="large"
                placeholder="请输入密码"
                v-model.trim="formData.registerPassword"
                show-password
            >
              <template #prefix>
                <span class="iconfont icon-password"></span>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item prop="reRegisterPassword">
            <el-input
                type="password"
                size="large"
                placeholder="请再次输入密码"
                v-model.trim="formData.reRegisterPassword"
                show-password
            >
              <template #prefix>
                <span class="iconfont icon-password"></span>
              </template>
            </el-input>
          </el-form-item>
        </div>
        <el-form-item prop="checkCode">
          <div class="check-code-panel">
            <el-input
                size="large"
                placeholder="请输入验证码"
                v-model.trim="formData.captcha"
                @keyup.enter="doSubmit"
            >
              <template #prefix>
                <span class="iconfont icon-checkcode"></span>
              </template>
            </el-input>
            <img
                :src="checkCodeUrl"
                class="check-code"
                @click="changeCheckCode(0)"
            />
          </div>
        </el-form-item>
        <el-form-item v-if="opType == 1">
          <div class="rememberme-panel">
            <el-checkbox v-model="formData.rememberMe">记住我</el-checkbox>
          </div>
          <div class="no-account">
            <a href="javascript:void(0)" class="a-link" @click="showPanel(2)"
            >忘记密码？</a
            >
            <a href="javascript:void(0)" class="a-link" @click="showPanel(0)"
            >没有账号？</a
            >
          </div>
        </el-form-item>
        <el-form-item v-if="opType == 0">
          <a href="javascript:void(0)" class="a-link" @click="showPanel(1)"
          >已有账号?</a
          >
        </el-form-item>
        <el-form-item v-if="opType == 2">
          <a href="javascript:void(0)" class="a-link" @click="showPanel(1)"
          >去登录?</a
          >
        </el-form-item>
        <el-form-item>
          <el-button
              type="primary"
              class="op-btn"
              @click="doSubmit"
              size="large"
          >
            <span v-if="opType == 0">注册</span>
            <span v-if="opType == 1">登录</span>
            <span v-if="opType == 2">重置密码</span>
          </el-button>
        </el-form-item>
        <!--        <div class="login-btn-qq" v-if="opType == 1">-->
        <!--          快捷登录 <img src="@/assets/qq.png" @click="qqLogin" />-->
        <!--        </div>-->
      </el-form>
    </div>
  </div>
</template>

<script setup>
import {ref, reactive, getCurrentInstance, nextTick, onMounted} from "vue";
import {useRouter, useRoute} from "vue-router";
import httpRequest from "@/api/httpRequest.ts";
import {ElMessage, ElMessageBox} from "element-plus";
import Verify from "@/utils/Verify.js";

const router = useRouter();
const route = useRoute();

// 0:注册 1:登录 2:重置密码
const opType = ref(1);
const showPanel = (type) => {
  opType.value = type;
  resetForm();
};

onMounted(() => {
  showPanel(1);
});

const checkRePassword = (rule, value, callback) => {
  if (value !== formData.value.registerPassword) {
    callback(new Error(rule.message));
  } else {
    callback();
  }
};
const formData = ref({});
const formDataRef = ref();
const rules = {
  email: [
    {required: true, message: "请输入邮箱"},
    {validator: Verify.email, message: "请输入正确的邮箱"},
  ],
  password: [{required: true, message: "请输入密码"}],
  emailCaptcha: [{required: true, message: "请输入邮箱验证码"}],
  username: [{required: true, message: "请输入昵称"}],
  registerPassword: [
    {required: true, message: "请输入密码"},
    {
      validator: Verify.password,
      message: "密码只能是数字，字母，特殊字符 6-18位",
    },
  ],
  reRegisterPassword: [
    {required: true, message: "请再次输入密码"},
    {
      validator: checkRePassword,
      message: "两次输入的密码不一致",
    },
  ],
  captcha: [{required: true, message: "请输入图片验证码"}],
};
//验证码
const checkCodeUrl = ref();
const checkCodeUrl4SendMailCode = ref();
const changeCheckCode = (type) => {
  if (type == 0) {
    httpRequest.get('/account/captcha').then(({data}) => {
      formData.value.captchaHashCode = data.data.hashkey
      console.log(data);
      checkCodeUrl.value = `/api${data.data.image_url}`
    })
    // checkCodeUrl.value =
    //     api.checkCode + "?type=" + type + "&time=" + new Date().getTime();
  } else {
    // checkCodeUrl4SendMailCode.value =
    //     api.checkCode + "?type=" + type + "&time=" + new Date().getTime();
  }
};

//获取邮箱验证码
const emailCheckBtn = ref({
  disable: false,
  msg: "获取验证码"
})
const getEmailCode = () => {
  formDataRef.value.validateField("email", (valid) => {
    if (!valid) {
      return;
    }
    httpRequest.post('/account/captcha', {
      email: formData.value.email,
      type: opType.value === 0 ? 'register' : 'reset_password',
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
            clearInterval(intervalId);
            emailCheckBtn.value.disable = false;
            emailCheckBtn.value.msg = `获取验证码`
          } else {
            emailCheckBtn.value.msg = `${remainingTime}`
          }
        }, 1000);
      }
    })
  })
};

//重置表单
const resetForm = () => {
  nextTick(() => {
    changeCheckCode(0);
    formDataRef.value.resetFields();
    formData.value = {};

    //登录
    if (opType.value === 1) {
      const cookieLoginInfo = localStorage.getItem("loginInfo");
      if (cookieLoginInfo) {
        const info = JSON.parse(cookieLoginInfo)
        if (info) formData.value = info;
      }
    }
  });
};

// 登录、注册、重置密码  提交表单
const doSubmit = () => {
  formDataRef.value.validate(async (valid) => {
    if (!valid) {
      return;
    }
    let params = {};
    Object.assign(params, formData.value);
    //注册
    if (opType.value == 0 || opType.value == 2) {
      params.password = params.registerPassword;
      params.confirmPassword = params.reRegisterPassword;
      delete params.registerPassword;
      delete params.reRegisterPassword;
    }
    //登录
    // if (opType.value == 1) {
    //   let cookieLoginInfo = proxy.VueCookies.get("loginInfo");
    //   let cookiePassword =
    //       cookieLoginInfo == null ? null : cookieLoginInfo.password;
    //   if (params.password !== cookiePassword) {
    //     params.password = md5(params.password);
    //   }
    // }
    let url = null;
    if (opType.value == 0) {
      url = "/account/register";
    } else if (opType.value == 1) {
      url = "/account/login";
    } else if (opType.value == 2) {
      url = "/account/resetPwd";
    }
    httpRequest.post(url, params).then(({data}) => {
      console.log(data)
      if (data.code !== 0) {
        throw data;
      }
      //注册返回
      if (opType.value == 0) {
        ElMessage.success("注册成功,请登录");
        showPanel(1);
      } else if (opType.value == 1) {
        //登录
        if (params.rememberMe) {
          localStorage.setItem("loginInfo", JSON.stringify({
            email: params.email,
            password: params.password,
            rememberMe: params.rememberMe,
          }));
        } else {
          localStorage.removeItem("loginInfo");
        }
        ElMessage.success("登录成功");
        //存储cookie
        localStorage.setItem("jwt", `Bearer ${data.data.access}`);
        localStorage.setItem("userID", `${data.data.user_id}`);
        const redirectUrl = route.query.redirectUrl || "/";
        router.push(redirectUrl);
      } else if (opType.value == 2) {
        //重置密码
        ElMessage.success("重置密码成功,请登录");
        showPanel(1);
      }
    }).catch((error) => {
      changeCheckCode(0);
      console.log(error);
      ElMessage.error(error.msg);
    })
  });
};
</script>

<style lang="scss" scoped>
.login-body {
  height: calc(100vh);
  background-size: cover;
  background: url("../../assets/login_bg.jpg");
  display: flex;

  .bg {
    flex: 1;
    background-size: cover;
    background-position: center;
    background-size: 800px;
    background-repeat: no-repeat;
    background-image: url("../../assets/login_img.png");
  }

  .login-panel {
    width: 430px;
    margin: 0 auto; /* 水平居中 */
    //margin-right: 15%;
    margin-top: calc((100vh - 500px) / 2);

    .login-register {
      padding: 25px;
      background: #fff;
      border-radius: 5px;

      .login-title {
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 20px;
      }

      .send-emali-panel {
        display: flex;
        width: 100%;
        justify-content: space-between;

        .send-mail-btn {
          margin-left: 5px;
        }
      }

      .rememberme-panel {
        width: 100%;
      }

      .no-account {
        width: 100%;
        display: flex;
        justify-content: space-between;
      }

      .op-btn {
        width: 100%;
      }
    }
  }

  .check-code-panel {
    width: 100%;
    display: flex;

    .check-code {
      margin-left: 5px;
      cursor: pointer;
    }
  }

  .login-btn-qq {
    margin-top: 20px;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;

    img {
      cursor: pointer;
      margin-left: 10px;
      width: 20px;
    }
  }
}
</style>
