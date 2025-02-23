<!--
Copyright 2020-2021 Huawei Technologies Co., Ltd.All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

<template>
  <div id="cl-summary-manage">
    <div v-show="loading"
         class="no-data-page">
      <div class="no-data-img">
        <img :src="require('@/assets/images/nodata.png')"
             alt="" />
        <p class="no-data-text">{{$t("public.dataLoading")}}</p>
      </div>
    </div>
    <div class="cl-summary-manage-container"
         v-show="!loading">
      <div class="cl-title">
        <div class="cl-title-left">
          <span class="summary-title">{{$t('explain.explainSummary')}}</span>
          <span>{{$t("symbols.leftbracket")}}</span>
          <span>{{$t('explain.explainSummaryCurrentFolder')}}</span>
          <span :title="currentFolder">{{currentFolder}}</span>
          <span>{{$t("symbols.rightbracket")}}</span>
        </div>
      </div>

      <!--table content area -->
      <div class="container">
        <!-- list table -->
        <div class="list-table">
          <el-table :data="summaryList"
                    stripe
                    height="100%"
                    tooltip-effect="light"
                    class="list-el-table"
                    ref="table">
            <el-table-column width="50"
                             type=index
                             :label="$t('summaryManage.sorting')">
            </el-table-column>
            <el-table-column min-width="600"
                             prop="train_id"
                             :label="$t('explain.summaryPath')"
                             show-overflow-tooltip>
            </el-table-column>
            <el-table-column width="180"
                             prop="update_time"
                             :label="$t('summaryManage.updateTime')"
                             show-overflow-tooltip>
            </el-table-column>
            <!--operate   -->
            <el-table-column prop="operate"
                             :label="$t('summaryManage.operation')"
                             class-name="operate-container"
                             :width="operateWidth">
              <template slot-scope="scope">
                <span class="menu-item operate-btn first-btn"
                      @contextmenu.prevent="rightClick(scope.row, $event, 0)"
                      @click.stop="goToSaliencyMap(scope.row)"
                      v-if="scope.row.saliency_map">
                  {{$t('explain.title')}} </span>
                <span class="menu-item operate-btn button-disable first-btn"
                      v-else
                      :title="$t('explain.disableSaliencyMapTip')">
                  {{$t('explain.title')}}
                </span>
                <span class="menu-item operate-btn"
                      @contextmenu.prevent="rightClick(scope.row, $event, 1)"
                      @click.stop="goToConterfactualinterpretation(scope.row)"
                      v-if="scope.row.hierarchical_occlusion">
                  {{$t('explain.conterfactualInterpretation')}} </span>
                <span class="menu-item operate-btn button-disable"
                      v-else
                      :title="$t('explain.disableHOCTip')">
                  {{$t('explain.conterfactualInterpretation')}}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </div>

      </div>
      <!--   outer Page   -->
      <div class="pagination-content">
        <el-pagination @current-change="currentPageChange"
                       @size-change="currentPagesizeChange"
                       :current-page="pagination.currentPage"
                       :page-size="pagination.pageSize"
                       :page-sizes="pagination.pageSizes"
                       :layout="pagination.layout"
                       :total="pagination.total"
                       class="page">
        </el-pagination>
      </div>
    </div>
    <div id="contextMenu"
         v-if="contextMenu.show"
         :style="{left: contextMenu.left, top: contextMenu.top}">
      <ul>
        <li @click="doRightClick()">{{$t('summaryManage.openNewTab')}}</li>
      </ul>
    </div>
  </div>
</template>

<script>
import RequestService from '../../services/request-service';

export default {
  data() {
    return {
      loading: true,
      currentFolder: '--',
      // table filter condition
      summaryList: [],
      pagination: {
        currentPage: 1,
        pageSize: 20,
        pageSizes: [10, 20, 50],
        total: 0,
        layout: 'total, sizes, prev, pager, next, jumper',
      },
      contextMenu: {
        show: false,
        left: '',
        top: '',
        data: null,
        type: 0,
      },
      tableDom: null,
      operateWidth: this.$store.state.language === 'en-us' ? 430 : 290,
    };
  },
  computed: {},
  watch: {},
  destroyed() {
    window.removeEventListener('resize', this.closeMenu);
    window.removeEventListener('mousewheel', this.closeMenu);
    if (this.tableDom) {
      this.tableDom.removeEventListener('scroll', this.closeMenu);
    }
    document.onclick = null;
    document.onscroll = null;
  },
  activated() {},
  mounted() {
    document.title = `${this.$t('explain.explain')}-MindInsight`;
    this.$nextTick(() => {
      this.init();
    });
    setTimeout(() => {
      window.addEventListener('resize', this.closeMenu, false);
      window.addEventListener('mousewheel', this.closeMenu, false);
      this.tableDom = this.$refs.table.bodyWrapper;
      if (this.tableDom) {
        this.tableDom.addEventListener('scroll', this.closeMenu, false);
      }
    }, 300);
  },

  methods: {
    init() {
      document.onclick = () => {
        this.contextMenu.show = false;
      };
      document.onscroll = () => {
        this.contextMenu.show = false;
      };

      const params = {
        limit: this.pagination.pageSize,
        offset: this.pagination.currentPage - 1,
      };
      this.querySummaryList(params);
    },
    /**
     * Querying summary list
     * @param {Object} params page info param
     */
    querySummaryList(params) {
      RequestService.getExplainList(params)
          .then(
              (res) => {
                this.loading = false;
                if (res && res.data && res.data.explain_jobs) {
                  const summaryList = JSON.parse(
                      JSON.stringify(res.data.explain_jobs),
                  );
                  summaryList.forEach((i) => {
                    i.update_time = i.update_time ? i.update_time : '--';
                  });
                  this.currentFolder = res.data.name ? res.data.name : '--';
                  this.pagination.total = res.data.total;
                  this.summaryList = summaryList;
                } else {
                  this.currentFolder = '--';
                  this.pagination.total = 0;
                  this.summaryList = [];
                }
              },
              (error) => {
                this.loading = false;
              },
          )
          .catch((e) => {
            this.loading = false;
          });
    },
    currentPagesizeChange(pageSize) {
      this.pagination.pageSize = pageSize;
      const params = {
        offset: this.pagination.currentPage - 1,
        limit: this.pagination.pageSize,
      };
      this.querySummaryList(params);
    },
    currentPageChange(currentPage) {
      this.pagination.currentPage = currentPage;
      const params = {
        offset: this.pagination.currentPage - 1,
        limit: this.pagination.pageSize,
      };
      this.querySummaryList(params);
    },
    /**
     * go to train dashboard
     * @param {Object} row select row
     */
    goToSaliencyMap(row) {
      this.contextMenu.show = false;
      const trainId = row.train_id;

      this.$router.push({
        path: '/explain/saliency-map',
        query: {id: trainId},
      });
    },

    /**
     * go to Profiler
     * @param {Object} row select row
     */
    goToConterfactualinterpretation(row) {
      this.contextMenu.show = false;
      const profilerDir = row.profiler_dir;
      const trainId = row.train_id;
      const path = row.relative_path;
      const router = '/explain/conterfactual-interpretation';

      this.$router.push({
        path: router,
        query: {
          dir: profilerDir,
          id: trainId,
          path: path,
        },
      });
    },

    rightClick(row, event, type) {
      const maxWidth = 175;
      this.contextMenu.data = row;
      this.contextMenu.type = type;
      const width = document.getElementById('cl-summary-manage').clientWidth;
      const left = Math.min(width - maxWidth, event.clientX + window.scrollX);
      this.contextMenu.left = left + 'px';
      this.contextMenu.top = event.clientY + window.scrollY + 'px';
      this.contextMenu.show = true;
    },

    doRightClick() {
      const row = this.contextMenu.data;
      if (!row) {
        return;
      }
      this.contextMenu.show = false;
      const trainId = row.train_id;
      if (this.contextMenu.type) {
        const router = '/explain/conterfactual-interpretation';

        const routeUrl = this.$router.resolve({
          path: router,
          query: {
            id: trainId,
          },
        });
        window.open(routeUrl.href, '_blank');
      } else {
        const routeUrl = this.$router.resolve({
          path: '/explain/saliency-map',
          query: {id: trainId},
        });
        window.open(routeUrl.href, '_blank');
      }
    },
    closeMenu() {
      this.contextMenu.show = false;
    },
    /**
     * tree data
     * @param {Object} tree
     * @param {Object} treeNode
     * @param {Object} resolve
     */
    loadDataListChildren(tree, treeNode, resolve) {
      setTimeout(() => {
        resolve(tree.children);
      });
    },
  },
  components: {},
};
</script>
<style>
#cl-summary-manage {
  height: 100%;
  width: 100%;
  background-color: #fff;
}
#cl-summary-manage .no-data-page {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}
#cl-summary-manage .no-data-page .no-data-img {
  background: #fff;
  text-align: center;
  height: 200px;
  width: 310px;
  margin: auto;
}
#cl-summary-manage .no-data-page .no-data-img img {
  max-width: 100%;
}
#cl-summary-manage .no-data-page .no-data-img p {
  font-size: 16px;
  padding-top: 10px;
}
#cl-summary-manage .cl-summary-manage-container {
  height: 100%;
  padding: 14px 32px 32px;
}
#cl-summary-manage .cl-title {
  border: none;
  height: 55px;
  line-height: 75px;
}
#cl-summary-manage .cl-title-left {
  padding-left: 0;
  height: 55px;
  line-height: 55px;
}
#cl-summary-manage .summary-title {
  font-size: 20px;
  font-weight: bold;
  margin-right: 15px;
}
#cl-summary-manage .summary-subtitle {
  margin-left: 20px;
}
#cl-summary-manage .container {
  height: calc(100% - 97px);
  overflow-y: auto;
}
#cl-summary-manage .container .list-table {
  height: 100%;
}
#cl-summary-manage .container .list-table .operate-container {
  padding-right: 32px;
}
#cl-summary-manage .pagination-content {
  margin-top: 16px;
  text-align: right;
}
#cl-summary-manage .operate-btn {
  margin-left: 20px;
  padding: 12px 0;
}
#cl-summary-manage .el-dialog {
  min-width: 500px;
  padding-bottom: 30px;
}
#cl-summary-manage .operate-btn.button-disable {
  -moz-user-select: none;
  /*Firefox*/
  -webkit-user-select: none;
  /*webkitbrowser*/
  -ms-user-select: none;
  /*IE10*/
  -khtml-user-select: none;
  /*Early browser*/
  user-select: none;
  color: #c0c4cc;
  cursor: not-allowed;
}
#cl-summary-manage .menu-item {
  color: #00a5a7;
  cursor: pointer;
}
#cl-summary-manage .menu-item.operate-btn.first-btn {
  margin-left: 0;
}
#cl-summary-manage #contextMenu {
  position: absolute;
  min-width: 150px;
  border: 1px solid #d4d4d4;
}
#cl-summary-manage #contextMenu ul {
  background-color: #f7faff;
  border-radius: 2px;
}
#cl-summary-manage #contextMenu ul li {
  padding: 5px 18px;
  cursor: pointer;
}
#cl-summary-manage #contextMenu ul li:hover {
  background-color: #a7a7a7;
  color: white;
}
#cl-summary-manage .details-data-list .el-table td,
#cl-summary-manage .details-data-list .el-table th.is-leaf {
  border: none;
  border-top: 1px solid #ebeef5;
}
#cl-summary-manage .details-data-list .el-table th {
  padding: 10px 0;
  border-top: 1px solid #ebeef5;
}
#cl-summary-manage .details-data-list .el-table th .cell {
  border-left: 1px solid #d9d8dd;
  height: 14px;
  line-height: 14px;
}
#cl-summary-manage .details-data-list .el-table th:first-child .cell {
  border-left: none;
}
#cl-summary-manage .details-data-list .el-table th:nth-child(2),
#cl-summary-manage .details-data-list .el-table td:nth-child(2) {
  max-width: 30%;
}
#cl-summary-manage .details-data-list .el-table td {
  padding: 8px 0;
}
#cl-summary-manage .details-data-list .el-table__row--level-0 td:first-child:after {
  width: 20px;
  height: 1px;
  background: #ebeef5;
  z-index: 11;
  position: absolute;
  left: 0;
  bottom: -1px;
  content: "";
  display: block;
}
#cl-summary-manage .details-data-list .el-table__row--level-1 td {
  padding: 4px 0;
  position: relative;
}
#cl-summary-manage .details-data-list .el-table__row--level-1 td:first-child::before {
  width: 42px;
  background: #f0fdfd;
  border-right: 2px #00a5a7 solid;
  z-index: 10;
  position: absolute;
  left: 0;
  top: -1px;
  bottom: 0px;
  content: "";
  display: block;
}
#cl-summary-manage .details-data-list .el-table__row--level-1:first-child td:first-child::before {
  bottom: 0;
}
#cl-summary-manage .details-data-list .el-dialog__title {
  font-weight: bold;
}
#cl-summary-manage .details-data-list .el-dialog__body {
  max-height: 500px;
  padding-top: 10px;
  padding-bottom: 0px;
  overflow: auto;
}
#cl-summary-manage .details-data-list .el-dialog__body .details-data-title {
  margin-bottom: 20px;
}
</style>
