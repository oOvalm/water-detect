<template>
  <div>
    <div class="top">
      <el-button
          type="primary"
          :disabled="selectIdList.length === 0"
          @click="cancelShareBatch"
      >
        <span class="iconfont icon-cancel"></span>取消分享
      </el-button>
    </div>
    <div class="file-list">
      <Table
          :columns="columns"
          :showPagination="true"
          :dataSource="tableData"
          :fetch="loadDataList"
          :options="tableOptions"
          @rowSelected="rowSelected"
      >
        <template #filename="{ index, row }">
          <div
              class="file-item"
              @mouseenter="showOp(row)"
              @mouseleave="cancelShowOp(row)"
          >
            <template v-if="(row.file_info.file_type === 3 || row.file_info.file_type === 2)">
              <icon :cover="`${row.file_info.id}`" :width="32"></icon>
            </template>
            <template v-else>
              <icon :fileType="row.file_info.file_type"></icon>
              <!--              <icon v-if="row.file_info.file_type == 0" :fileType="row.file_info.file_type"></icon>-->
              <!--              <icon v-if="row.file_info.file_type == 1" :fileType="0"></icon>-->
            </template>
            <span
                class="file-name"
                :title="row.file_info.filename"
            >
              <span>{{ row.file_info.filename }}</span>
            </span>
            <span class="op">
              <template v-if="row.showOp && row.file_id">
                <span class="iconfont icon-link" @click="copy(row)"
                >复制链接</span
                >
                <span class="iconfont icon-cancel" @click="cancelShare(row)"
                >取消分享</span
                >
              </template>
            </span>
          </div>
        </template>
        <template #expire_time="{ index, row }">
          {{ row.valid_type === 3 ? "永久" : row.expire_time }}
        </template>
      </Table>
    </div>
  </div>
</template>

<script setup>
import useClipboard from "vue-clipboard3";

const {toClipboard} = useClipboard();
import {onMounted, ref} from "vue";
import Icon from "@/components/Icon.vue";
import Table from "@/components/Table.vue"
import httpRequest from "@/api/httpRequest.ts";
import Confirm from "@/utils/Confirm.js";
import message from "@/utils/Message.js";

const api = {
  loadDataList: "/share/loadShareList",
  cancelShare: "/share/cancelShare",
};

const shareUrl = ref(document.location.origin + "/share/");

//列表
const columns = [
  {
    label: "文件名",
    prop: "filename",
    scopedSlots: "filename",
  },
  {
    label: "分享时间",
    prop: "share_time",
    width: 200,
  },
  {
    label: "失效时间",
    prop: "expire_time",
    scopedSlots: "expire_time",
    width: 200,
  },
  {
    label: "浏览次数",
    prop: "show_count",
    width: 200,
  },
];
//搜索
const search = () => {
  showLoading.value = true;
  loadDataList();
};
//列表
const tableData = ref({});
const tableOptions = {
  extHeight: 20,
  selectType: "checkbox",
};

const loadDataList = async () => {
  let params = {
    pageNo: tableData.value.pageNo,
    pageSize: tableData.value.pageSize,
  };
  if (params.category !== "all") {
    delete params.filePid;
  }
  console.log('lqkwjelqkwje');
  httpRequest.get(api.loadDataList, {params: params}).then(({data}) => {
    if (data.code !== 0) {
      message.error(`获取分享列表失败: ${data.msg}`);
    }
    tableData.value = data.data;
  }).catch((e) => {
    console.log(e)
    message.error("获取分享列表失败")
  });
};

//展示操作按钮
const showOp = (row) => {
  tableData.value.list.forEach((element) => {
    element.showOp = false;
  });
  row.showOp = true;
};

const cancelShowOp = (row) => {
  row.showOp = false;
};

//复制链接
const copy = async (data) => {
  await toClipboard(
      `链接:${shareUrl.value}${data.share_code} 提取码: ${data.code}`
  );
  message.success("复制成功");
};

//多选 批量选择
const selectIdList = ref([]);
const rowSelected = (rows) => {
  selectIdList.value = [];
  rows.forEach((item) => {
    selectIdList.value.push(item.share_code);
  });
};

//取消分享
const cancelShareIdList = ref([]);
const cancelShareBatch = () => {
  if (selectIdList.value.length === 0) {
    return;
  }
  cancelShareIdList.value = selectIdList.value;
  cancelShareDone();
};

const cancelShare = (row) => {
  cancelShareIdList.value = [row.share_code];
  cancelShareDone();
};

const cancelShareDone = async () => {
  Confirm(`你确定要取消分享吗？`, async () => {
    let data = {
      shareIds: cancelShareIdList.value.join(","),
    }
    httpRequest.post(api.cancelShare, data).then(({data}) => {
      if (data.code !== 0) {
        message.error(`取消分享失败, ${data.msg}`)
      }
      message.success("取消分享成功");
      loadDataList();
    }).catch((e) => {
      message.error(`取消分享失败, ${data.msg}`)
      console.log(e)
    });
  });
};
onMounted(() => {
  loadDataList();
})
</script>

<style lang="scss" scoped>
@import "@/assets/file.list.scss";

.file-list {
  margin-top: 10px;

  .file-item {
    .file-name {
      span {
        &:hover {
          color: #494944;
        }
      }
    }

    .op {
      width: 170px;
    }
  }
}
</style>
